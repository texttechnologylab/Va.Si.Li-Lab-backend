from urllib.parse import quote_plus
import json
from flask_restx import Api
from pymongo import MongoClient
import pymongo.errors
from flask import Flask
import os

def build_pymongo_connection():
    db_name = os.environ.get("DB_NAME", "experiment")
    user_name = os.environ.get("DB_USERNAME", "user_rw")
    pw = os.environ.get("DB_PASSWORD", "password")
    host_name = os.environ.get("DB_SERVER", "localhost")
    host_port = os.environ.get("DB_PORT", "27017")
    host = f"{host_name}:{host_port}"
    uri = "mongodb://%s:%s@%s" % (
        quote_plus(user_name), quote_plus(pw), host)
    try:
        client = MongoClient(f'mongodb://{user_name}:{pw}@{host}/{db_name}')
        mydb = client.get_database(db_name)
    except pymongo.errors as ex:
        print(ex)
        mydb = None
    return mydb

app = Flask(__name__)
api = Api(app, title="Va.Si.Li REST API", version="1.0")