from multiprocessing.managers import DictProxy
from typing import Callable

from hypercorn.config import Config, Sockets

WorkerFunc = Callable[[Config, DictProxy, Sockets], None]
