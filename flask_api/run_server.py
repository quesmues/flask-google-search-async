import asyncio
import platform
import time
from multiprocessing import Manager, get_context
from multiprocessing.context import BaseContext
from multiprocessing.managers import DictProxy
from multiprocessing.process import BaseProcess
from os import getpid
from typing import List

from app import asgi_app
from config import env
from custom_typing import WorkerFunc
from hypercorn.asyncio.run import worker_serve
from hypercorn.config import Config, Sockets
from hypercorn.utils import wrap_app


def __worker_func(config: Config, manager: DictProxy, sockets: Sockets) -> None:
    """
    Função do worker, onde setamos o event_loop e servimos a aplicação
    """
    setattr(
        asgi_app.wsgi_application, "mutiprocessing_manager_dict", manager
    )  # Pequeno hack para passarmos nosso manager a aplicação
    asgi_app.wsgi_application.config["PID"] = getpid()
    if config.workers > 1 and platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(
        worker_serve(
            wrap_app(asgi_app, config.wsgi_max_body_size, mode="asgi"),
            config,
            sockets=sockets,
        )
    )


def start_processes(
    worker_func: WorkerFunc,
    ctx: BaseContext,
    config: Config,
    manager: DictProxy,
    sockets: Sockets,
) -> List[BaseProcess]:
    """Inicia os workers do servidor.

    Args:
        worker_func (WorkerFunc): Função do worker que servirá a aplicação em cada processo
        ctx (BaseContext): Contexto do multiprocessing
        config (Config): Configuração do hypercorn
        manager (DictProxy): Manager que será usado para compartilharmos informação entre os processos
        sockets (Sockets): Socket que será compartilhado entre os processos

    Returns:
        List[BaseProcess]: Lista dos processos que foram iniciados
    """
    processes = []
    for _ in range(config.workers):
        process = ctx.Process(  # type: ignore
            target=worker_func,
            kwargs={"config": config, "manager": manager, "sockets": sockets},
        )
        process.daemon = True
        process.start()
        processes.append(process)
        if platform.system() == "Windows":
            time.sleep(0.1)
    return processes


if __name__ == "__main__":
    """
    Fluxo de criação do workers produtivos da aplicação, onde precisamos instanciar o objeto Manager e chamar o método dict() fora dos processos, pois as váriaveis globais não são compartilhadas entre os workers, e necessitamos disto para nosso endpoint de métricas que são armazenadas em memória
    """
    worker_func: WorkerFunc

    config = Config()
    config.bind = [f"{env('HOST')}:{env('PORT')}"]
    config.workers = int(env("WORKERS"))  # type: ignore

    manager = Manager().dict()
    manager["metrics"] = []

    ctx = get_context("spawn")

    sockets = config.create_sockets()

    worker_func = __worker_func

    processes = start_processes(worker_func, ctx, config, manager, sockets)
    for process in processes:
        process.join()
    for process in processes:
        process.terminate()

    for sock in sockets.secure_sockets:
        sock.close()
    for sock in sockets.insecure_sockets:
        sock.close()
