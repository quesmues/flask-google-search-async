from multiprocessing.managers import DictProxy
from typing import Union

from asgiref.wsgi import WsgiToAsgi
from config import Config, env
from flask import Flask
from main.routes import scrap_google


class CustomFlask(Flask):
    _mutiprocessing_manager_dict: Union[DictProxy, None] = None

    @property
    def mutiprocessing_manager_dict(self) -> Union[DictProxy, None]:
        return self._mutiprocessing_manager_dict

    @mutiprocessing_manager_dict.setter
    def mutiprocessing_manager_dict(self, manager: DictProxy):
        self._mutiprocessing_manager_dict = manager


app = CustomFlask(__name__)
app.config.from_object(Config)

app.register_blueprint(scrap_google, url_prefix="/api/v1")

if "__main__" == __name__:
    app.run(port=env("PORT"))  # type: ignore

asgi_app = WsgiToAsgi(app)
