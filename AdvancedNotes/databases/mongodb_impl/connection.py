from pymongo import MongoClient
from colorama import Fore

from .config import MongoDB_HOST, MongoDB_PORT


class MongoDBConnection:
    @staticmethod
    def check_connection():
        try:
            client = MongoClient(MongoDB_HOST, int(MongoDB_PORT))["mynotes"]
            client["groups"].find_one({"title": "Home"})
        except TypeError:
            print(f"\n{Fore.LIGHTYELLOW_EX}Invalid connection parameters or database doesn't exists")
        else:
            return client
