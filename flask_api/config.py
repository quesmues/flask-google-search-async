import os

BASEDIR = os.path.abspath(os.path.dirname(__file__))

global_objects = {}

class Config:
    """
    Arquivo de configuração do Flask
    """
    SECRET_KEY = "28465d8dfeefa59211639cacd4b5cdc6"
    GOOGLE_URL = "https://www.google.com"
    BROWSER_HEADER = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9,lt;q=0.8,et;q=0.7,de;q=0.6",
    }
    MULTI_DICT_MANAGER = None
    PID = None