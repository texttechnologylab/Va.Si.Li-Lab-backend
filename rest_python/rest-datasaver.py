import copy
from dataclasses import dataclass
from bson import ObjectId
from flask import Flask, request, jsonify
from bson.json_util import dumps, loads
from flask_restx import Api, Resource, fields
from pymongo import MongoClient
from pymongo.cursor import Cursor
import gridfs
import datetime
import pymongo.errors
import json
import numpy as np
from urllib.parse import quote_plus
from ConvertAudio import RestApiAudioConverter
from whisper2text import Whisper2Text
from Text2Speech import TextToSpeech
from chatgpt import ChatGpt

app = Flask(__name__)
api = Api(app, title="Va.Si.Li REST API", version="1.0")

logger = api.namespace(
    "Logging", description="Endpoints to log various data", path="/logging")

required_data_audio = {"roomId", "messageType", "clientId", "timestamp", "position", "rotation", "cameraRotation",
                       "audioData", "peers"}
required_data_player = {"roomId", "szeneId", "messageId", "clientId", "localTime", "body", "rightHand", "leftHand",
                        "audioData",
                        "peers", "roles"}
required_data_object = {"roomId", "szeneId", "referenceMessage", "clientId", "localTime", "objectId", "objectName",
                        "hand"}
required_data_special = {"roomId", "szeneId", "clientId", "localTime"}
required_data_log = {"roomId", "szeneId", "clientId", "localTime"}


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
        fs = gridfs.GridFS(mydb, "Audio")
    except pymongo.errors as ex:
        print(ex)
        mydb = None
        fs = None
    return mydb, fs


databasedb, audiofs = build_pymongo_connection(f"./config.json")
scene_db = databasedb["scenarios-v2"]
mycol = databasedb["testing"]
db_player = databasedb["player"]
db_object = databasedb["object"]
body_fs = gridfs.GridFS(databasedb, "body")
right_hand_fs = gridfs.GridFS(databasedb, "rightHand")
left_hand_fs = gridfs.GridFS(databasedb, "leftHand")
db_special = databasedb["special"]
db_log = databasedb["log"]

audio_converter = RestApiAudioConverter(np.int64, 16000, 2, 1)
whisper_model = Whisper2Text("small")
with open("./config_chatgpt.json", "r", encoding="UTF-8") as json_file:
    key_chatgpt = json.load(json_file)
chatgpt_class = ChatGpt(key_chatgpt["key"], "text-davinci-003")
text_2_speech = TextToSpeech(False)


audioData_model = logger.model("AudioData", {
    "base64": fields.String(required=True)
})

chat_response = logger.model("ChatGPTResponse", {
    "status": fields.String(required=True),
    "audio": fields.Nested(audioData_model),
    "text_in": fields.String(required=True),
    "text_out": fields.String(required=True),
    "lang": fields.String(required=True)
})

chat_payload = logger.model("ChatGPTPayload", {
    "status": fields.String(required=True),
    "audioData": fields.Nested(audioData_model, required=True),
    "lang": fields.String(required=True)
})


generic_error_response = logger.model("GenericErrorResponse", {
    "message": fields.String(required=True)
})

generic_success_response = logger.model("GenericSuccessResponse", {
    "success": fields.String(required=True),
    "message": fields.String
})


@logger.route("/chatgpt")
@logger.doc(body=chat_payload)
class ChatGPT(Resource):
    @logger.response(201, "Sucess", chat_response)
    @logger.response(415, "Invalid JSON", generic_error_response)
    @logger.response(500, "Internal Server Error", generic_error_response)
    @logger.expect(chat_payload, validate=True)
    def post(self):
        if request.is_json:
            data_request = request.get_json()
            try:
                audio_bytes = data_request["audioData"]["base64"]
                audio_seg = audio_converter.convert_bytes_to_audio_segment(
                    audio_bytes)
                whisper_text = whisper_model.get_text(audio_seg, True)
                response = chatgpt_class.get_response(whisper_text["text"])
                audio_response = text_2_speech.text_audio(
                    response, whisper_text["language"])
                return {
                    "status": "success",
                    "audio": {
                        "base64": audio_response
                    },
                    "text_in": whisper_text["text"],
                    "text_out": response,
                    "lang": whisper_text["language"]
                }, 202
            except Exception as ex:
                return {"message": f"{ex}"}, 500
        return {"message": "Request must be JSON"}, 415


tts_payload = logger.model("TTS", {
    "text": fields.String(required=True),
    "lang": fields.String(required=True)
})

tts_response = logger.model("TTSResponse", {
    "status": fields.String(required=True),
    "audio": fields.Nested(audioData_model, required=True)
})


@logger.route("/tts")
@logger.doc(body=tts_payload)
class TTS(Resource):
    @logger.response(201, "Sucess", tts_response)
    @logger.response(500, "Internal Server Error", generic_error_response)
    @logger.expect(tts_payload, validate=True)
    def post(self):
        if request.is_json:
            data_request = request.get_json()
            try:
                audio_response = text_2_speech.text_audio(
                    data_request["text"], data_request["lang"])
                return {
                    "status": "success",
                    "audio": {
                        "base64": audio_response
                    }
                }
            except Exception as ex:
                return {"message": f"{ex}"}, 500


position_message = logger.model("PositionMessage", {
    "x": fields.Float(required=True),
    "y": fields.Float(required=True),
    "z": fields.Float(required=True)
})

rotation_message = logger.model("RotationMessage", {
    "x": fields.Float(required=True),
    "y": fields.Float(required=True),
    "z": fields.Float(required=True),
    "w": fields.Float(required=True)
})

player_body_message = logger.model("PlayerBodyMessage", {
    "positions": fields.List(fields.Nested(position_message), required=True),
    "rotations": fields.List(fields.Nested(rotation_message), required=True),
    "cameraRotations": fields.List(fields.Nested(rotation_message), required=True),
    "cameraPositions": fields.List(fields.Nested(position_message), required=True)
})

player_hand_message = logger.model("PlayerHandMessage", {
    "positions": fields.List(fields.Nested(position_message), required=True),
    "rotations": fields.List(fields.Nested(rotation_message), required=True)
})

player_payload = logger.model("PlayerPayload", {
    "messageId": fields.Integer(required=True),
    "audioData": fields.Nested(audioData_model, required=True),
    "peers": fields.List(fields.String, required=True),
    "role": fields.String(required=True),
    "positionTags": fields.List(fields.String, required=True),
    "body": fields.List(fields.Nested(player_body_message), required=True),
    "rightHand": fields.List(fields.Nested(player_hand_message), required=True),
    "leftHand": fields.List(fields.Nested(player_hand_message), required=True),
})


@logger.route("/player")
@logger.doc(body=player_payload)
class Player(Resource):
    @logger.response(201, "Sucess", generic_success_response)
    @logger.response(415, "Invalid JSON", generic_error_response)
    @logger.response(500, "Internal Server Error", generic_error_response)
    def post():
        server_time = datetime.datetime.now()
        dt_string = server_time.strftime("%d/%m/%Y %H:%M:%S")
        if request.is_json:
            player_data = request.get_json()
            z = set(player_data.keys()).intersection(required_data_player)
            if len(z) == len(required_data_player):
                try:
                    player_data_clone = copy.deepcopy(player_data)
                    player_data_clone.pop("audioData")
                    player_data_clone.pop("body")
                    player_data_clone.pop("rightHand")
                    player_data_clone.pop("leftHand")
                    byte_audio = json.dumps(
                        player_data["audioData"]).encode("utf-8")
                    audio_id_fs = audiofs.put(byte_audio,
                                              filename=f"{player_data['clientId']}#{player_data['roomId']}#{player_data['szeneId']}#{player_data['messageId']}")
                    byte_body = json.dumps(player_data["body"]).encode("utf-8")
                    body_id_fs = body_fs.put(byte_body,
                                             filename=f"{player_data['clientId']}#{player_data['roomId']}#{player_data['szeneId']}#{player_data['messageId']}")
                    byte_right_hand = json.dumps(
                        player_data["rightHand"]).encode("utf-8")
                    right_hand_id_fs = right_hand_fs.put(byte_right_hand,
                                                         filename=f"{player_data['clientId']}#{player_data['roomId']}#{player_data['szeneId']}#{player_data['messageId']}")
                    byte_left_hand = json.dumps(
                        player_data["leftHand"]).encode("utf-8")
                    left_hand_id_fs = left_hand_fs.put(byte_left_hand,
                                                       filename=f"{player_data['clientId']}#{player_data['roomId']}#{player_data['szeneId']}#{player_data['messageId']}")
                    player_data_clone["server-timestamp"] = dt_string
                    player_data_clone["audio_id"] = audio_id_fs
                    player_data_clone["body"] = body_id_fs
                    player_data_clone["rightHand"] = right_hand_id_fs
                    player_data_clone["leftHand"] = left_hand_id_fs
                    id_insert = db_player.insert_one(player_data_clone)
                    return {"status": "success", "message": str(id_insert.inserted_id)}, 201
                except Exception as ex:
                    return {"message": f"{ex}"}, 500
            else:
                return {"message": f"Request Json must content following keys for player: {required_data_player}"}, 415
        return {"message": "Request must be JSON"}, 415


object_payload = logger.model("ObjectPayload", {
    "referenceMessage": fields.Integer(required=True),
    "objectId": fields.String(required=True),
    "objectName": fields.String(required=True),
    "hand": fields.String(required=True),
    "interaction": fields.String(required=True)
})


@logger.route("/object")
@logger.doc(body=object_payload)
class Object(Resource):
    @logger.response(201, "Sucess", generic_success_response)
    @logger.response(415, "Error", generic_error_response)
    @logger.response(500, "Internal Server Error", generic_error_response)
    def post():
        server_time = datetime.datetime.now()
        dt_string = server_time.strftime("%d/%m/%Y %H:%M:%S")
        if request.is_json:
            object_data = request.get_json()
            z = set(object_data.keys()).intersection(required_data_object)
            if len(z) == len(required_data_object):
                try:
                    object_data["server-timestamp"] = dt_string
                    id_insert = db_object.insert_one(object_data)
                    return {"status": "success", "message": str(id_insert.inserted_id)}, 201
                except Exception as ex:
                    return {"message": f"{ex}"}, 500
            else:
                return {"message": f"Request Json must content following keys for Object: {required_data_object}"}, 415
        return {"message": "Request must be JSON"}, 415


@logger.route("/special")
@logger.doc(params={"body": {"in": "body", "description": "Payload data as json", "required": True}})
class Special(Resource):
    @logger.response(201, "Sucess", generic_success_response)
    @logger.response(415, "Error", generic_error_response)
    @logger.response(500, "Internal Server Error", generic_error_response)
    def post():
        server_time = datetime.datetime.now()
        dt_string = server_time.strftime("%d/%m/%Y %H:%M:%S")
        if request.is_json:
            special_data = request.get_json()
            z = set(special_data.keys()).intersection(required_data_special)
            if len(z) == len(required_data_special):
                try:
                    special_data["server-timestamp"] = dt_string
                    id_insert = db_special.insert_one(special_data)
                    return {"status": "success", "message": str(id_insert.inserted_id)}, 201
                except Exception as ex:
                    return {"message": f"{ex}"}, 500
            else:
                return {"message": f"Request Json must content following keys for Special: {required_data_special}"}, 415
        return {"message": "Request must be JSON"}, 415


audio_payload = logger.model("AudioPayload", {
    "audioData": fields.Nested(audioData_model, required=True),
})


@logger.route("/audio")
@logger.doc(body=audio_payload)
class Audio(Resource):
    @logger.response(201, "Sucess", generic_success_response)
    @logger.response(415, "Error", generic_error_response)
    @logger.response(500, "Internal Server Error", generic_error_response)
    def post():
        if request.is_json:
            audio_data = request.get_json()
            audio_data_clone = copy.deepcopy(audio_data)
            audio_data_clone.pop("audioData")
            z = set(audio_data.keys()).intersection(required_data_audio)
            if len(z) == len(required_data_audio):
                server_time = datetime.datetime.now()
                dt_string = server_time.strftime("%d/%m/%Y %H:%M:%S")

                if mycol.count_documents({"roomId": audio_data["roomId"], "clientId": audio_data["clientId"],
                                          "messageType": audio_data["messageType"]}, limit=1):
                    result = mycol.find_one({"roomId": audio_data["roomId"], "clientId": audio_data["clientId"],
                                            "messageType": audio_data["messageType"]})
                    return {"status": "success", "message": str(result["_id"])}, 201

                else:
                    byte_data = bytes(
                        audio_data["audioData"]["base64"], 'utf-8')
                    id_fs = audiofs.put(byte_data, filename=f"{audio_data['clientId']}#{audio_data['roomId']}",
                                        contentType="base64")
                    audio_data_clone["id_fs"] = id_fs
                    audio_data_clone["server-time"] = server_time
                    id_insert = mycol.insert_one(audio_data_clone)
                return {"status": "success", "message": str(id_insert.inserted_id)}, 201
            else:
                return {"message": f"Request Json must content following keys for audio: {required_data_audio}"}, 415
        return {"message": "Request must be JSON"}, 415


log_payload = logger.model("LogPayload", {
    "referenceMessage": fields.Integer(required=True),
    "logMessage": fields.String(required=True),
    "logType": fields.String(required=True),
    "stacktrace": fields.String(required=True)
})


@logger.route("/log")
@logger.doc(body=log_payload)
class Log(Resource):
    @logger.response(201, "Sucess", generic_success_response)
    @logger.response(415, "Error", generic_error_response)
    @logger.response(500, "Internal Server Error", generic_error_response)
    def post(self):
        server_time = datetime.datetime.now()
        dt_string = server_time.strftime("%d/%m/%Y %H:%M:%S")
        if request.is_json:
            log_data = request.get_json()
            z = set(log_data.keys()).intersection(required_data_log)
            if len(z) == len(required_data_special):
                try:
                    log_data["server-timestamp"] = dt_string
                    id_insert = db_log.insert_one(log_data)
                    return {"status": "success", "message": str(id_insert.inserted_id)}, 201
                except Exception as ex:
                    return {"message": f"{ex}"}, 500
            else:
                return {"message": f"Request Json must content following keys for Special: {required_data_special}"}, 415
        return {"message": "Request must be JSON"}, 415


scene = api.namespace(
    "Scene Data",
    description="Endpoints to get and post various scene information", path="/")


def serialize_cursor(data: Cursor):
    items = []
    try:
        for item in data:
            if '_id' in item:
                item['_id'] = str(item['_id'])
            items.append(item)
    except TypeError:
        data['_id'] = str(data['_id'])
        return data
    else:
        return items


role_payload = scene.model("RolePayload", {
    "mode": fields.String(required=True),
    "spawnPosition": fields.String(required=True),
    "maxCount": fields.Integer(required=True),
    "admin": fields.Boolean(required=True)
})

role_locale_payload = scene.model("RoleLocalePayload", {
    "name": fields.String(required=True),
    "description": fields.List(fields.String, required=True)
})

role_result = scene.model("RoleResult", {
    "mode": fields.String(required=True),
    "spawnPosition": fields.String(required=True),
    "maxCount": fields.Integer(required=True),
    "admin": fields.Boolean(required=True),
    "locales": fields.Wildcard(fields.Nested(role_locale_payload))
})

scene_payload = scene.model("ScenePayload", {
    "name": fields.String(required=True),
    "shortName": fields.String(required=True),
    "enabled": fields.Boolean(required=True),
    "author": fields.String,
    "internalName": fields.String(required=True),
    "enabled": fields.Boolean(required=True)
})

scene_result = scene.model("SceneResponse", {
    "_id": fields.String(required=True),
    "name": fields.String(required=True),
    "shortName": fields.String(required=True),
    "enabled": fields.Boolean(required=True),
    "author": fields.String,
    "internalName": fields.String(required=True),
    "roles": fields.Wildcard(fields.Nested(role_result))
})


def create_many_result(namespace, model):
    return namespace.model("ResultMany"+model.name, {
        "result": fields.List(fields.Nested(model))
    })


def create_single_result(namespace, model):
    return namespace.model("ResultSingle"+model.name, {
        "result": fields.Nested(model)
    })


@scene.route("/scene")
class Scene(Resource):
    @scene.response(200, "Sucess", create_single_result(scene, scene_result))
    @scene.response(415, "Error", generic_error_response)
    @scene.response(500, "Internal Server Error", generic_error_response)
    @scene.param("id", "Id of the scene", "query", required=True)
    @scene.param("small", "Only returns scene specific results", "query", required=False, type=bool)
    def get(self):
        projection = {}
        if request.args.get("small") and request.args.get("small") == "true":
            projection = {"roles": 0}
        return {
            "result":
                serialize_cursor(scene_db.find_one(
                    {"_id": ObjectId(request.args.get("id"))},
                    projection=projection
                ))
        }, 200

    @scene.expect(scene_payload, validate=True)
    @scene.response(201, "Sucess", generic_success_response)
    @scene.response(415, "Invalid JSON", generic_error_response)
    @scene.response(500, "Internal Server Error", generic_error_response)
    def post(self):
        if request.is_json:
            scene_data = request.get_json()
            try:
                id_insert = scene_db.insert_one(scene_data)
                return {"status": "success", "message": str(id_insert.inserted_id)}, 201
            except Exception as ex:
                return {"message": f"{ex}"}, 500
        return {"message": "Request must be JSON"}, 415

    @scene.param("id", "Id of the scene", "query", required=True)
    @scene.expect(scene_payload, validate=True)
    @scene.response(200, "Sucess", generic_success_response)
    @scene.response(415, "Invalid JSON", generic_error_response)
    @scene.response(500, "Internal Server Error", generic_error_response)
    def patch(self):
        if request.is_json:
            scene_data = request.get_json()
            try:
                scene_db.update_one(
                    {"_id": ObjectId(request.args.get("id"))}, {"$set": scene_data})
                return {"status": "success", "message": f"Successfully updated document with id '{request.args.get('id')}'"}, 200
            except Exception as ex:
                return {"message": f"{ex}"}, 500
        return {"message": "Request must be JSON"}, 415


@scene.route("/scenes")
class Scenes(Resource):
    @scene.param("disabled", "Weither to also return disabled scenes", "query", required=False)
    @scene.param("small", "Only returns scene specific results", "query", required=False, type=bool)
    @scene.response(200, "Sucess", create_many_result(scene, scene_result))
    def get(self):
        pipeline = []

        if request.args.get("disabled") is None:
            pipeline.append({"$match": {"enabled": True}})
        if request.args.get("small") and request.args.get("small") == "true":
            pipeline.append({"$project": {"roles": 0}})
        if len(pipeline) == 0:
            return {"result": serialize_cursor(scene_db.aggregate(pipeline))}, 200
        else:
            return {"result": serialize_cursor(scene_db.find())}, 200


@scene.route("/role")
class Role(Resource):

    @scene.param("id", "Id of the scene", "query", required=True)
    @scene.param("identifier", "Identifier for the role", "query", required=True)
    @scene.param("locale", "Locale of the role", "query", required=False)
    @scene.response(200, "Sucess", create_single_result(scene, role_result))
    def get(self):
        role_slug = f"roles.{request.args.get('identifier')}"
        result = {}
        if request.args.get("locale"):
            role_slug_locale = f"{role_slug}.locales.{request.args.get('locale')}"
            result = serialize_cursor(scene_db.find_one(
                {
                    "_id": ObjectId(request.args.get("id")),
                    role_slug: {"$exists": True}
                },
                projection={
                    f"{role_slug}.mode": 1,
                    f"{role_slug}.spawnPosition": 1,
                    f"{role_slug}.maxCount": 1,
                    f"{role_slug}.admin": 1,
                    role_slug_locale: 1
                }))["roles"][request.args.get("identifier")]
        else:
            result = serialize_cursor(scene_db.find_one({"_id": ObjectId(request.args.get(
                "id")), role_slug: {"$exists": True}}))["roles"][request.args.get("identifier")]
        return {"result": result}, 200

    @scene.doc(body=role_payload)
    @scene.param("id", "Id of the scene", "query", required=True)
    @scene.param("identifier", "Internal identifier for that role (e.g a name)", "query", required=True)
    @scene.expect(role_payload, validate=True)
    @scene.response(201, "Sucess", generic_success_response)
    @scene.response(415, "Invalid JSON", generic_error_response)
    @scene.response(500, "Internal Server Error", generic_error_response)
    def post(self):
        if request.is_json:
            role_data = request.get_json()
            try:
                role_slug = f"roles.{request.args.get('identifier')}"
                scene_db.update_one(
                    {
                        "_id": ObjectId(request.args.get("id")),
                        role_slug: {"$exists": False}
                    },
                    {"$set": {role_slug: role_data}})
                return {"status": "success", "message": f"Successfully updated document with id '{request.args.get('id')}'"}, 201
            except Exception as ex:
                return {"message": f"{ex}"}, 500
        return {"message": "Request must be JSON"}, 415

    @scene.doc(body=role_payload)
    @scene.param("id", "Id of the scene", "query", required=True)
    @scene.param("identifier", "Internal identifier for that role (e.g a name)", "query", required=True)
    @scene.expect(role_payload, validate=True)
    @scene.response(201, "Sucess", generic_success_response)
    @scene.response(415, "Invalid JSON", generic_error_response)
    @scene.response(500, "Internal Server Error", generic_error_response)
    def patch(self):
        if request.is_json:
            role_data = request.get_json()
            try:
                role_slug = f"roles.{request.args.get('identifier')}"
                scene_db.update_one({"_id": ObjectId(request.args.get("id"))}, {
                                             "$set": {role_slug: role_data}})
                return {"status": "success", "message": f"Successfully updated document with id '{request.args.get('id')}'"}, 200
            except Exception as ex:
                return {"message": f"{ex}"}, 500
        return {"message": "Request must be JSON"}, 415


@scene.route("/role/locales")
class RoleLocale(Resource):
    @scene.doc(body=role_locale_payload)
    @scene.param("id", "Id of the scene", "query", required=True)
    @scene.param("identifier", "Internal identifier for that role (e.g a name)", "query", required=True)
    @scene.param("locale", "Locale of the role", "query", required=True)
    @scene.expect(role_locale_payload, validate=True)
    @scene.response(201, "Sucess", generic_success_response)
    @scene.response(412, "Entry does not exist", generic_error_response)
    @scene.response(415, "Invalid JSON", generic_error_response)
    @scene.response(500, "Internal Server Error", generic_error_response)
    def post(self):
        if request.is_json:
            role_data = request.get_json()
            try:
                role_slug = f"roles.{request.args.get('identifier')}"
                role_slug_locale = f"{role_slug}.locales.{request.args.get('locale')}"
                update = scene_db.update_one({"_id": ObjectId(request.args.get("id")),
                                              role_slug: {"$exists": True},
                                              role_slug_locale: {"$exists": False}},
                                             {"$set": {role_slug_locale: role_data}})
                if (update.matched_count == 0):
                    return {"message": "Role does not exist or locale already exists"}, 412
                return {"status": "success", "message": f"Successfully updated document with id '{request.args.get('id')}'"}, 201
            except Exception as ex:
                return {"message": f"{ex}"}, 405
        return {"message": "Request must be JSON"}, 415

    @scene.doc(body=role_locale_payload)
    @scene.param("id", "Id of the scene", "query", required=True)
    @scene.param("identifier", "Internal identifier for that role (e.g a name)", "query", required=True)
    @scene.param("locale", "Locale of the role", "query", required=True)
    @scene.expect(role_locale_payload, validate=True)
    @scene.response(201, "Sucess", generic_success_response)
    @scene.response(412, "Entry does not exist", generic_error_response)
    @scene.response(415, "Invalid JSON", generic_error_response)
    @scene.response(500, "Internal Server Error", generic_error_response)
    def patch(self):
        if request.is_json:
            role_data = request.get_json()
            try:
                role_slug = f"roles.{request.args.get('identifier')}"
                role_slug_locale = f"{role_slug}.locales.{request.args.get('locale')}"
                update = scene_db.update_one({"_id": ObjectId(request.args.get("id")),
                                              role_slug: {"$exists": True},
                                              role_slug_locale: {"$exists": True}},
                                             {"$set": {role_slug_locale: role_data}})
                if (update.matched_count == 0):
                    return {"message": "Role or locale does not exists"}, 412
                return {"status": "success", "message": f"Successfully updated document with id '{request.args.get('id')}'"}, 201
            except Exception as ex:
                return {"message": f"{ex}"}, 405
        return {"message": "Request must be JSON"}, 415

roles_result = scene.model("RolesResult", {
    "result": fields.Wildcard(fields.Nested(role_result))
})

@scene.route("/roles")
class Roles(Resource):
    @scene.doc()
    @scene.param("id", "Id of the scene", "query", required=True)
    @scene.response(200, "Sucess", roles_result)
    def get(self):
        result = serialize_cursor(scene_db.find_one(
            {"_id": ObjectId(request.args.get("id"))}))["roles"]
        return {"result": result}


if __name__ == '__main__':
    app.run(threaded=True, host="0.0.0.0", port=5000)
