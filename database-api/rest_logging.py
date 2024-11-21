from common import build_pymongo_connection, api
from flask import request
from flask_restx import Resource, fields
import datetime

logger = api.namespace(
    "Logging", description="Endpoints to log various data", path="/logging")

required_data_audio = {"roomId", "messageType", "clientId", "timestamp", "position", "rotation", "cameraRotation",
                       "audioData", "peers"}
required_data_player = {"playerId", "audioData",
                        "localTime", "messageId", "body", "leftHand", "rightHand"}
required_data_object = {"playerId", "referenceMessage",
                        "localTime", "objectId", "objectName", "hand", "interaction"}
required_data_special = {"localTime", "mode"}
required_data_log = {"playerId", "localTime",
                     "referenceMessage", "logMessage", "logType", "stacktrace"}
required_data_logIn = {"playerId", "roomId",
                       "sceneName", "clientId", "localTime", "messageId"}
required_data_roleIn = {"playerId", "role", "localTime", "messageId"}


databasedb = build_pymongo_connection()
mycol = databasedb["logging"]
db_player = databasedb["player"]
db_object = databasedb["object"]
db_audio = databasedb["Audio"]
db_body = databasedb["Body"]
db_hand = databasedb["Hand"]
db_head = databasedb["Head"]
db_log = databasedb["Log"]
db_special = databasedb["special"]
db_log = databasedb["log"]
db_logIn = databasedb["LogIn"]
db_role = databasedb["Role"]
db_face = databasedb["Facial"]
db_eye = databasedb["Eye"]

audioData_model = logger.model("AudioData", {
    "base64": fields.String(required=True)
})

generic_error_response = logger.model("GenericErrorResponse", {
    "message": fields.String(required=True)
})

generic_success_response = logger.model("GenericSuccessResponse", {
    "success": fields.String(required=True),
    "message": fields.String
})

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
    "playerId": fields.String(required=True),
    "messageId": fields.Integer(required=True),
    "audioData": fields.Nested(audioData_model, required=True),
    "localTime": fields.String(required=True),
    # "positionTags": fields.List(fields.String, required=True),
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
                    # Audio
                    audio_data = {
                        "playerId": player_data["playerId"],
                        "audio": player_data["audioData"]["base64"],
                        "messageId": player_data["messageId"],
                        "localTime": player_data["localTime"],
                        "serverTime": server_time
                    }
                    db_audio.insert_one(audio_data)
                    # Body
                    body_infos = []
                    left_hand_infos = []
                    right_hand_infos = []
                    head_infos = []
                    eye_infos = []
                    face_infos = []
                    for c, i in enumerate(player_data["body"]["positions"]):
                        body_infos.append({
                            "playerId": player_data["playerId"],
                            "position": player_data["body"]["positions"][c],
                            "rotation": player_data["body"]["rotations"][c],
                            "messageId": player_data["messageId"],
                            "localTime": player_data["localTime"],
                            "counter": player_data["count"][c],
                            "serverTime": server_time
                        })
                        left_hand_infos.append({
                            "playerId": player_data["playerId"],
                            "position": player_data["leftHand"]["positions"][c],
                            "rotation": player_data["leftHand"]["rotations"][c],
                            "messageId": player_data["messageId"],
                            "identifier": "left",
                            "localTime": player_data["localTime"],
                            "counter": player_data["count"][c],
                            "serverTime": server_time
                        })
                        right_hand_infos.append({
                            "playerId": player_data["playerId"],
                            "position": player_data["rightHand"]["positions"][c],
                            "rotation": player_data["rightHand"]["rotations"][c],
                            "messageId": player_data["messageId"],
                            "identifier": "right",
                            "localTime": player_data["localTime"],
                            "counter": player_data["count"][c],
                            "serverTime": server_time
                        })
                        head_infos.append({
                            "playerId": player_data["playerId"],
                            "position": player_data["body"]["cameraPositions"][c],
                            "rotation": player_data["body"]["cameraRotations"][c],
                            "messageId": player_data["messageId"],
                            "localTime": player_data["localTime"],
                            "counter": player_data["count"][c],
                            "serverTime": server_time
                        })
                        if "metaMessage" not in player_data:
                            continue
                        face_infos.append({
                            "playerId": player_data["playerId"],
                            "expressionWeights": player_data["metaMessage"]["faceStates"][c]["ExpressionWeights"],
                            "expressionWeightConfidences": player_data["metaMessage"]["faceStates"][c]["ExpressionWeightConfidences"],
                            "status":
                                player_data["metaMessage"]["faceStates"][c]["Status"],
                            "time":
                                player_data["metaMessage"]["faceStates"][c]["Time"],

                            "messageId": player_data["messageId"],
                            "localTime": player_data["localTime"],
                            "counter": player_data["count"][c],
                            "serverTime": server_time
                        })
                        eye_infos.append({
                            "playerId": player_data["playerId"],
                            "eyeGazes": player_data["metaMessage"]["eyeGazesStates"][c]["EyeGazes"],
                            "time": player_data["metaMessage"]["eyeGazesStates"][c]["Time"],
                            "messageId": player_data["messageId"],
                            "localTime": player_data["localTime"],
                            "counter": player_data["count"][c],
                            "serverTime": server_time
                        })
                    db_body.insert_many(body_infos)
                    db_hand.insert_many(left_hand_infos)
                    db_hand.insert_many(right_hand_infos)
                    db_head.insert_many(head_infos)
                    db_face.insert_many(face_infos)
                    db_eye.insert_many(eye_infos)
                    return {"status": "success", "message": "success"}, 201
                except Exception as ex:
                    return {"message": f"{ex}"}, 500
            else:
                return {"message": f"Request Json must content following keys for player: {required_data_player}"}, 415
        return {"message": "Request must be JSON"}, 415


object_payload = logger.model("ObjectPayload", {
    "playerId": fields.String(required=True),
    "referenceMessage": fields.Integer(required=True),
    "localTime": fields.String(required=True),
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


@logger.route("/playerLogIn")
class PlayerLogIn(Resource):
    @logger.response(201, "Sucess", generic_success_response)
    @logger.response(415, "Error", generic_error_response)
    @logger.response(500, "Internal Server Error", generic_error_response)
    def post(self):
        server_time = datetime.datetime.now()
        dt_string = server_time.strftime("%d/%m/%Y %H:%M:%S")
        player_data = request.get_json()
        z = set(player_data.keys()).intersection(required_data_logIn)
        if request.is_json:
            if len(z) == len(required_data_logIn):
                try:
                    player_input = {
                        "playerId": player_data["playerId"],
                        "clientId": player_data["clientId"],
                        "roomId": player_data["roomId"],
                        "sceneName": player_data["sceneName"],
                        "localTime": player_data["localTime"],
                        "serverTime": server_time,
                        "messageId": player_data["messageId"]
                    }
                    db_logIn.insert_one(player_input)
                    return {"status": "success"}, 201
                except Exception as ex:
                    return {"error": f"{ex}"}, 500
            else:
                return {"error": f"Request Json must content following keys for player LogIn: {required_data_logIn}"}, 415
        return {"error": "Request must be JSON"}, 415


@logger.route("/playerRoleLogIn")
class PlayerRoleLogIn(Resource):
    @logger.response(201, "Sucess", generic_success_response)
    @logger.response(415, "Error", generic_error_response)
    @logger.response(500, "Internal Server Error", generic_error_response)
    def post():
        server_time = datetime.datetime.now()
        dt_string = server_time.strftime("%d/%m/%Y %H:%M:%S")
        player_data = request.get_json()
        z = set(player_data.keys()).intersection(required_data_roleIn)
        if request.is_json:
            if len(z) == len(required_data_roleIn):
                try:
                    player_input = {
                        "playerId": player_data["playerId"],
                        "localTime": player_data["localTime"],
                        "serverTime": server_time,
                        "role": player_data["role"],
                        "messageId": player_data["messageId"]
                    }
                    db_role.insert_one(player_input)
                    return {"status": "success"}, 201
                except Exception as ex:
                    return {"error": f"{ex}"}, 500
            else:
                return {"error": f"Request Json must content following keys for player LogIn: {required_data_roleIn}"}, 415
        return {"error": "Request must be JSON"}, 415


@logger.route("/status")
class Status(Resource):
    def get(self):
        return {"status": "online"}, 200
