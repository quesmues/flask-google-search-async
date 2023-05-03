import asyncio
import random
import time
from multiprocessing import Process

import aiohttp

URL = "http://localhost:8000/api/v1/scrap-google-search?search={}"

WORDS = (
    "banana",
    "computer",
    "coffee",
    "beach",
    "dog",
    "mountain",
    "book",
    "movie",
    "pizza",
    "guitar",
)


async def client_task() -> None:
    async with aiohttp.ClientSession() as session:
        _ = await session.get(URL.format(random.choice(WORDS)))


async def stress_http_connection(qtd: int) -> None:
    tasks = [asyncio.create_task(client_task()) for _ in range(qtd)]
    _ = await asyncio.gather(*tasks)


if "__main__" == __name__:
    qtd = 10
    processes = []
    start = time.time()
    asyncio.run(stress_http_connection(qtd))
    end = time.time()
    print(f"{qtd} de requisições realizada em {end-start:.2f} segundos!")
