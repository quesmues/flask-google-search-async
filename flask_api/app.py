import asyncio
import os

from asgiref.wsgi import WsgiToAsgi
from flask import Flask

from flask_api.config import Config
from flask_api.main.routes import scrap_google

if os.name == 'nt':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

app = Flask(__name__)
app.config.from_object(Config)

app.register_blueprint(scrap_google, url_prefix="/api/v1")

if "__main__" == __name__:
    app.run(port=8000)

asgi_app = WsgiToAsgi(app)
