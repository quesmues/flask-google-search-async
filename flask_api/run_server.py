import asyncio
import platform
import time

from multiprocessing import Manager, get_context
from multiprocessing.managers import DictProxy
from multiprocessing.process import BaseProcess
from os import getpid
from typing import List

from hypercorn.asyncio import serve, worker_serve
from hypercorn.config import Config, Sockets
from hypercorn.utils import wrap_app

from app import asgi_app


def __worker_async(config: Config, manager: DictProxy, sockets: Sockets) -> None:
    asgi_app.wsgi_application.config["MULTI_DICT_MANAGER"] = manager
    asgi_app.wsgi_application.config["PID"] = getpid()
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(
        worker_serve(
            wrap_app(asgi_app, config.wsgi_max_body_size, mode="asgi"), config, sockets=sockets
        )
    )


def start_processes(worker_func, ctx, config: Config, manager: DictProxy, sockets: Sockets) -> List[BaseProcess]:
    processes = []
    for _ in range(4):
        process = ctx.Process(
            target=worker_func,
            kwargs={"config": config, "manager": manager, "sockets": sockets}
        )
        process.daemon = True
        process.start()
        processes.append(process)
        if platform.system() == "Windows":
            time.sleep(0.1)
    return processes


if __name__ == '__main__':
    config = Config()
    config.bind = ["localhost:8000"]

    # Instancia o objeto Manager fora dos processos, para compartilhar ele entre os processos
    manager = Manager().dict()
    manager['metrics'] = []
    ctx = get_context("spawn")

    sockets = config.create_sockets()

    processes = start_processes(__worker_async, ctx, config, manager, sockets)
    for process in processes:
        process.join()
    for process in processes:
        process.terminate()
