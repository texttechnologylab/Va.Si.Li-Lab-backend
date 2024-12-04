from urllib.parse import quote
from flask_restx import Api
from pymongo import MongoClient
import pymongo.errors
from flask import Flask, request
import os
from functools import wraps

def build_pymongo_connection():
    db_name = os.environ.get("DB_NAME", "experiment")
    user_name = os.environ.get("DB_USERNAME", "user_rw")
    pw = os.environ.get("DB_PASSWORD", "password")
    host_name = os.environ.get("DB_SERVER", "localhost")
    host_port = os.environ.get("DB_PORT", "27017")
    host = f"{host_name}:{host_port}"
    try:
        client = MongoClient(f'mongodb://{quote(user_name)}:{quote(pw)}@{host}')
        mydb = client.get_database(db_name)
    except pymongo.errors as ex:
        print(ex)
        mydb = None
    return mydb

api_key = os.environ.get("X_API_KEY", "")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        headers = request.headers
        auth = headers.get("X-Api-Key")
        if auth != api_key:
            return {"message": "Unauthorized"}, 401
        return f(*args, **kwargs)
    return decorated_function

authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'X-API-KEY'
    }
}

app = Flask(__name__)
api = Api(app, authorizations=authorizations, security='apikey', title="Va.Si.Li REST API", version="1.0")