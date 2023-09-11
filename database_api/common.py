from urllib.parse import quote_plus
import json
from flask_restx import Api
from pymongo import MongoClient
import pymongo.errors
from flask import Flask

def build_pymongo_connection(access_dir: str):
    with open(access_dir, "r", encoding="UTF-8") as json_file:
        access_data = json.load(json_file)
    db_name = access_data["Datenbank"]
    user_name = access_data["User"]
    pw = access_data["Passwort"]
    host = f"{access_data['Server']}:{access_data['Port']}"
    uri = "mongodb://%s:%s@%s" % (
        quote_plus(user_name), quote_plus(pw), host)
    try:
        print(f'mongodb://{user_name}:{pw}@{host}/{db_name}')
        client = MongoClient(f'mongodb://{user_name}:{pw}@{host}/{db_name}')
        mydb = client.get_database(db_name)
    except pymongo.errors as ex:
        print(ex)
        mydb = None
    return mydb

app = Flask(__name__)
api = Api(app, title="Va.Si.Li REST API", version="1.0")