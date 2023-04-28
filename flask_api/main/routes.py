import asyncio
import multiprocessing
import time
from urllib.parse import quote

import aiohttp
from flask import Blueprint, current_app
from flask import request
from flask.views import View
from bs4 import BeautifulSoup

scrap_google = Blueprint('scrap_google', __name__)

metrics = []


async def get_search_data(search: str) -> dict:
    """
    Função assíncrona que retorna os 5 primeiros links da pesquisa do Google

    :param search: Texto a ser buscado na pesquisa do Google
    :return: Um dicionário com o termo pesquisado e os primeiros 5 links da pesquisa do Google
    """
    links = []
    url = current_app.config['GOOGLE_URL'] + f"/search?q={quote(search)}"
    headers = current_app.config['BROWSER_HEADER']
    async with aiohttp.ClientSession(headers=headers) as session:
        response = await session.get(url, allow_redirects=True, timeout=30)
        body = await response.text()
        soup = BeautifulSoup(body, 'html.parser')
        for result in soup.select('.tF2Cxc', limit=5):
            links.append(result.select_one('.yuRUbf a')['href'])
    return {
        "search_text": search,
        "links": links
    }


async def set_metrics_multiprocessing(data):
    if current_app.config['MULTI_DICT_MANAGER']:
        with multiprocessing.Lock() as _:
            metrics = current_app.config['MULTI_DICT_MANAGER']["metrics"]
            metrics.append(data)
            current_app.config['MULTI_DICT_MANAGER'].update({"metrics": metrics})


async def set_metrics_global(data):
    if not current_app.config['MULTI_DICT_MANAGER']:
        global metrics
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
        data = {
            "search_text": search,
            "response_time": end - start
        }
        await set_metrics_multiprocessing(data)
        await set_metrics_global(data)
        return done


class GetMetricsView(View):
    """
    Metricas das requisições da view `ScrapGoogleSearchView`
    """
    async def dispatch_request(self):
        data = dict(current_app.config['MULTI_DICT_MANAGER'])
        if not data:
            global metrics
            return metrics
        return data


scrap_google.add_url_rule(
    "/scrap-google-search",
    view_func=ScrapGoogleSearchView.as_view("scrap_list")
)
scrap_google.add_url_rule(
    "/metrics",
    view_func=GetMetricsView.as_view("metrics_list")
)
