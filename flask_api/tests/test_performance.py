import asyncio
import random
import time
from multiprocessing import Process

import aiohttp

URL = "http://localhost:8000/api/v1/scrap-google-search?search={}"

WORDS = ('banana', 'computer', 'coffee', 'beach', 'dog', 'mountain', 'book', 'movie', 'pizza', 'guitar')


async def client_task() -> None:
    async with aiohttp.ClientSession() as session:
        _ = await session.get(URL.format(random.choice(WORDS)))


async def stress_http_connection():
    tasks = [asyncio.create_task(client_task())]
    _ = await asyncio.gather(*tasks)


def async_wrapper():
    asyncio.run(stress_http_connection())


if "__main__" == __name__:
    qtd = 10
    processes = []
    start = time.time()
    for _ in range(qtd):
        process = Process(target=async_wrapper)
        process.daemon = True
        process.start()
        processes.append(process)

    for process in processes:
        process.join()
    for process in processes:
        process.terminate()

    end = time.time()
    print(f"{qtd} de requisições realizada em {end-start:.2f} segundos!")


