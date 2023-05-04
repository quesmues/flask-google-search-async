from asgiref.wsgi import WsgiToAsgi
from config import Config, env
from flask import Flask
from main.routes import scrap_google

app = Flask(__name__)
app.config.from_object(Config)

app.register_blueprint(scrap_google, url_prefix="/api/v1")

if "__main__" == __name__:
    app.run(port=env("PORT"))  # type: ignore

asgi_app = WsgiToAsgi(app)
