from flask import Blueprint
from main import views

scrap_google = Blueprint("scrap_google", __name__)

scrap_google.add_url_rule(
    "/scrap-google-search", view_func=views.ScrapGoogleSearchView.as_view("scrap_list")
)
scrap_google.add_url_rule(
    "/metrics", view_func=views.GetMetricsView.as_view("metrics_list")
)
