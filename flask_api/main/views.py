import asyncio
import time
from os import getpid
from urllib.parse import quote

import aiohttp
from bs4 import BeautifulSoup
from flask import current_app, request
from flask.views import View

metrics = []


async def get_search_data(search: str) -> dict:
    """
    Função assíncrona que retorna os 5 primeiros links da pesquisa do Google

    :param search: Texto a ser buscado na pesquisa do Google
    :return: Um dicionário com o termo pesquisado e os primeiros 5 links da pesquisa do Google
    """
    links = []
    url = current_app.config["GOOGLE_URL"] + f"/search?q={quote(search)}"
    headers = current_app.config["BROWSER_HEADER"]
    async with aiohttp.ClientSession(headers=headers) as session:
        response = await session.get(url, allow_redirects=True, timeout=30)
        body = await response.text()
        soup = BeautifulSoup(body, "html.parser")
        for result in soup.select(".tF2Cxc", limit=5):
            links.append(result.select_one(".yuRUbf a")["href"])  # type: ignore
    return {"search_text": search, "links": links}


async def set_metrics(data):
    global metrics
    if hasattr(current_app, "mutiprocessing_manager_dict"):
        tmp = current_app.mutiprocessing_manager_dict["metrics"]  # type: ignore
        tmp.append(data)
        current_app.mutiprocessing_manager_dict.update({"metrics": tmp})  # type: ignore
        return
    metrics.append(data)


class ScrapGoogleSearchView(View):
    """
    View que faz uma busca no Google de forma assíncrona,
    e retorna os 5 primeiros links que o Google respondeu.
    Possui suporte para multiplas pesquisas simultâneas.
    Ex: search=teste1&search=teste2&...
    """

    async def dispatch_request(self):
        search = request.args.getlist("search")
        if not search:
            return {"error": "Parâmetros obrigatórios não informados!"}
        start = time.time()
        tasks = [asyncio.create_task(get_search_data(x)) for x in search]
        done = await asyncio.gather(*tasks)
        end = time.time()
        data = {"search_text": search, "response_time": end - start}
        await set_metrics(data)
        return done


class GetMetricsView(View):
    """
    Metricas das requisições da view `ScrapGoogleSearchView`
    """

    async def dispatch_request(self):
        if hasattr(current_app, "mutiprocessing_manager_dict"):
            return dict(current_app.mutiprocessing_manager_dict)  # type: ignore
        global metrics
        return metrics
