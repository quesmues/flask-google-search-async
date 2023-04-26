import time
from urllib.parse import quote

import aiohttp
from flask import Blueprint, current_app
from flask import request
from flask.views import View
from bs4 import BeautifulSoup

scrap_google = Blueprint('scrap_google', __name__)

metrics = []


async def get_search_data(search: str):
    """
    Função assíncrona que retorna os 5 primeiros links da pesquisa do Google

    :param search: Texto a ser buscado na pesquisa do Google
    :return: Uma lista com os primeiros 5 links da pesquisa do Google
    """
    global metrics
    url = current_app.config['GOOGLE_URL'] + f"/search?q={quote(search)}"
    headers = current_app.config['BROWSER_HEADER']
    start = time.time()
    links = []
    async with aiohttp.ClientSession(headers=headers) as session:
        response = await session.get(url, allow_redirects=True, timeout=30)
        body = await response.text()
        soup = BeautifulSoup(body, 'html.parser')
        for result in soup.select('.tF2Cxc', limit=5):
            links.append(result.select_one('.yuRUbf a')['href'])
    end = time.time()
    data = {
        "search_text": search,
        "response_time": end - start
    }
    metrics.append(data)
    return links


class ScrapGoogleSearchView(View):
    """
    View que faz uma busca no Google de forma assíncrona,
    e retorna os 5 primeiros links que o Google respondeu
    """
    async def dispatch_request(self):
        args = request.args.to_dict()
        search = args.get("search", None)
        if not search:
            return {"error": "Parâmetros obrigatórios não informados!"}
        done = await get_search_data(search)
        return done


class GetMetricsView(View):
    """
    Metricas das requisições da view `ScrapGoogleSearchView`
    """
    async def dispatch_request(self):
        global metrics
        return metrics


scrap_google.add_url_rule(
    "/scrap-google-search",
    view_func=ScrapGoogleSearchView.as_view("scrap_list")
)
scrap_google.add_url_rule(
    "/metrics",
    view_func=GetMetricsView.as_view("metrics_list")
)
