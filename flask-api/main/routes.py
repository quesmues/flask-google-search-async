import asyncio

from flask import Blueprint
from flask import request
from flask.views import View

scrap_google = Blueprint('scrap_google', __name__)


async def async_get_data(search: str):
    await asyncio.sleep(1)
    return search


class ScrapGoogleSearchView(View):
    async def dispatch_request(self):
        args = request.args.to_dict()
        assert args.get("search")
        data = await async_get_data(args.get("search"))
        return data


scrap_google.add_url_rule(
    "/scrap-google-search",
    view_func=ScrapGoogleSearchView.as_view("scrap_list")
)
