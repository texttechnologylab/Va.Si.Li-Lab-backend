from pymongo import IndexModel
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
required_data_object = {"playerId", "messageId",
                        "localTime", "objectId", "objectName", "hand", "interaction"}
required_data_special = {"localTime", "mode"}
required_data_log = {"playerId", "localTime",
                     "messageId", "logMessage", "logType", "stacktrace"}
required_data_logIn = {"playerId", "roomId",
                       "sceneName", "clientId", "localTime", "messageId"}
required_data_roleIn = {"playerId", "role", "localTime", "messageId"}
required_data_levelChange = {"playerId", "roomId", "sceneName", "localTime", "levelID", "levelStatus"}
required_data_misc = {"playerId", "jsonData"}

databasedb = build_pymongo_connection() 
mycol = databasedb["logging"]
#db_player = databasedb["player"]
db_object = databasedb["object"]
db_audio = databasedb["Audio"]
db_body = databasedb["Body"]
db_hand = databasedb["Hand"]
db_finger = databasedb["Finger"]
db_head = databasedb["Head"]
db_log = databasedb["Log"]
db_special = databasedb["Special"]
db_logIn = databasedb["LogIn"]
db_face = databasedb["Facial"]
db_eye = databasedb["Eye"]
db_role = databasedb["Role"]
db_level = databasedb["Level"]
db_misc = databasedb["Misc"]


db_object.create_index([("playerId", 1)], name="object_index_playerId")
db_object.create_index([("messageId", 1)], name="object_index_messageId")
db_object.create_index([("interaction", 1)], name="object_index_interaction")
db_object.create_index([("hand", 1)], name="object_index_hand")

db_audio.create_index([("playerId", 1)], name="audio_index_playerId")
db_audio.create_index([("messageId", 1)], name="audio_index_messageId")

db_body.create_index([("playerId", 1)], name="body_index_playerId")
db_body.create_index([("messageId", 1)], name="body_index_messageId")
db_body.create_index([("counter", 1)], name="body_index_counter")
db_body.create_index([("position", 1)], name="body_index_position")
db_body.create_index([("rotation", 1)], name="body_index_rotation")

db_hand.create_index([("playerId", 1)], name="hand_index_playerId")
db_hand.create_index([("messageId", 1)], name="hand_index_messageId")
db_hand.create_index([("counter", 1)], name="hand_index_counter")
db_hand.create_index([("identifier", 1)], name="hand_index_identifier")
db_hand.create_index([("position", 1)], name="hand_index_position")
db_hand.create_index([("rotation", 1)], name="hand_index_rotation")

db_finger.create_index([("playerId", 1)], name="finger_index_playerId")
db_finger.create_index([("messageId", 1)], name="finger_index_messageId")
db_finger.create_index([("counter", 1)], name="finger_index_counter")
db_finger.create_index([("identifier", 1)], name="finger_index_identifier")
db_finger.create_index([("rootPose", 1)], name="finger_index_rootPose")
db_finger.create_index([("pointerPose", 1)], name="finger_index_pointerPose")

db_head.create_index([("playerId", 1)], name="head_index_playerId")
db_head.create_index([("messageId", 1)], name="head_index_messageId")
db_head.create_index([("counter", 1)], name="head_index_counter")
db_head.create_index([("position", 1)], name="head_index_position")
db_head.create_index([("rotation", 1)], name="head_index_rotation")

db_log.create_index([("playerId", 1)], name="log_index_playerId")
db_log.create_index([("messageId", 1)], name="log_index_messageId")
db_log.create_index([("roomId", 1)], name="log_index_roomId")
db_log.create_index([("sceneName", 1)], name="log_index_sceneName")

db_special.create_index([("messageId", 1)], name="special_index_messageId")
db_special.create_index([("roomId", 1)], name="special_index_roomId")

db_logIn.create_index([("playerId", 1)], name="login_index_playerId")
db_logIn.create_index([("messageId", 1)], name="login_index_messageId")
db_logIn.create_index([("roomId", 1)], name="login_index_roomId")
db_logIn.create_index([("sceneName", 1)], name="login_index_sceneName")

db_face.create_index([("playerId", 1)], name="face_index_playerId")
db_face.create_index([("messageId", 1)], name="face_index_messageId")
db_face.create_index([("expressionWeights", 1)], name="face_index_expressionWeights")
db_face.create_index([("expressionWeightConfidences", 1)], name="face_index_expressionWeightConfidences")

db_eye.create_index([("playerId", 1)], name="eye_index_playerId")
db_eye.create_index([("messageId", 1)], name="eye_index_messageId")
db_eye.create_index([("position", 1)], name="eye_index_position")
db_eye.create_index([("orientation", 1)], name="eye_index_orientation")

db_role.create_index([("playerId", 1)], name="role_index_playerId")
db_role.create_index([("messageId", 1)], name="role_index_messageId")

db_level.create_index([("playerId", 1)], name="level_index_playerId")
db_level.create_index([("messageId", 1)], name="level_index_messageId")
db_level.create_index([("roomId", 1)], name="level_index_roomId")
db_level.create_index([("sceneName", 1)], name="level_index_sceneName")
db_level.create_index([("levelID", 1)], name="level_index_levelID")
db_level.create_index([("levelStatus", 1)], name="level_index_levelStatus")

db_misc.create_index([("playerId", 1)], name="misc_index_playerId")
db_misc.create_index([("messageId", 1)], name="misc_index_messageId")

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
    @logger.doc(security=None)
    @logger.response(201, "Sucess", generic_success_response)
    @logger.response(415, "Invalid JSON", generic_error_response)
    @logger.response(500, "Internal Server Error", generic_error_response)
    def post(self):
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
                    left_hand_finger_infos = []
                    right_hand_finger_infos = []
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

                        left_hand_finger_infos.append({
                            "playerId": player_data["playerId"],
                            "identifier": "left",
                            "status": player_data["metaMessage"]["leftHandStates"][c]["Status"],
                            "rootPose": player_data["metaMessage"]["leftHandStates"][c]["RootPose"],
                            "boneRotations": player_data["metaMessage"]["leftHandStates"][c]["BoneRotations"],
                            "pinches": player_data["metaMessage"]["leftHandStates"][c]["Pinches"],
                            "pinchStrength": player_data["metaMessage"]["leftHandStates"][c]["PinchStrength"],
                            "pointerPose": player_data["metaMessage"]["leftHandStates"][c]["PointerPose"],
                            "handScale": player_data["metaMessage"]["leftHandStates"][c]["HandScale"],
                            "handConfidence": player_data["metaMessage"]["leftHandStates"][c]["HandConfidence"],
                            "fingerConfidences": player_data["metaMessage"]["leftHandStates"][c]["FingerConfidences"],
                            "requestedTimeStamp": player_data["metaMessage"]["leftHandStates"][c][
                                "RequestedTimeStamp"],
                            "sampleTimeStamp": player_data["metaMessage"]["leftHandStates"][c]["SampleTimeStamp"],
                            "messageId": player_data["messageId"],
                            "localTime": player_data["localTime"],
                            "counter": player_data["count"][c],
                            "serverTime": server_time
                        })
                        right_hand_finger_infos.append({
                            "playerId": player_data["playerId"],
                            "identifier": "right",
                            "status": player_data["metaMessage"]["rightHandStates"][c]["Status"],
                            "rootPose": player_data["metaMessage"]["rightHandStates"][c]["RootPose"],
                            "boneRotations": player_data["metaMessage"]["rightHandStates"][c]["BoneRotations"],
                            "pinches": player_data["metaMessage"]["rightHandStates"][c]["Pinches"],
                            "pinchStrength": player_data["metaMessage"]["rightHandStates"][c]["PinchStrength"],
                            "pointerPose": player_data["metaMessage"]["rightHandStates"][c]["PointerPose"],
                            "handScale": player_data["metaMessage"]["rightHandStates"][c]["HandScale"],
                            "handConfidence": player_data["metaMessage"]["rightHandStates"][c]["HandConfidence"],
                            "fingerConfidences": player_data["metaMessage"]["rightHandStates"][c][
                                "FingerConfidences"],
                            "requestedTimeStamp": player_data["metaMessage"]["rightHandStates"][c][
                                "RequestedTimeStamp"],
                            "sampleTimeStamp": player_data["metaMessage"]["rightHandStates"][c]["SampleTimeStamp"],
                            "messageId": player_data["messageId"],
                            "localTime": player_data["localTime"],
                            "counter": player_data["count"][c],
                            "serverTime": server_time
                        })
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
                    db_finger.insert_many(left_hand_finger_infos)
                    db_finger.insert_many(right_hand_finger_infos)
                    return {"status": "success", "message": "success"}, 201
                except Exception as ex:
                    return {"message": f"{ex}"}, 500
            else:
                return {"message": f"Request Json must content following keys for player: {required_data_player}"}, 415
        return {"message": "Request must be JSON"}, 415


object_payload = logger.model("ObjectPayload", {
    "playerId": fields.String(required=True),
    "messageId": fields.Integer(required=True),
    "localTime": fields.String(required=True),
    "objectId": fields.String(required=True),
    "objectName": fields.String(required=True),
    "hand": fields.String(required=True),
    "interaction": fields.String(required=True)
})


@logger.route("/object")
@logger.doc(body=object_payload)
class Object(Resource):
    @logger.doc(security=None)
    @logger.response(201, "Sucess", generic_success_response)
    @logger.response(415, "Error", generic_error_response)
    @logger.response(500, "Internal Server Error", generic_error_response)
    def post(self):
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
    @logger.doc(security=None)
    @logger.response(201, "Sucess", generic_success_response)
    @logger.response(415, "Error", generic_error_response)
    @logger.response(500, "Internal Server Error", generic_error_response)
    def post(self):
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
    "messageId": fields.Integer(required=True),
    "logMessage": fields.String(required=True),
    "logType": fields.String(required=True),
    "stacktrace": fields.String(required=True)
})


@logger.route("/log")
@logger.doc(body=log_payload)
class Log(Resource):
    @logger.doc(security=None)
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
    @logger.doc(security=None)
    @logger.response(201, "Sucess", generic_success_response)
    @logger.response(415, "Error", generic_error_response)
    @logger.response(500, "Internal Server Error", generic_error_response)
    def post(self):
        server_time = datetime.datetime.now()
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
    @logger.doc(security=None)
    @logger.response(201, "Sucess", generic_success_response)
    @logger.response(415, "Error", generic_error_response)
    @logger.response(500, "Internal Server Error", generic_error_response)
    def post(self):
        server_time = datetime.datetime.now()
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

@logger.route("/levelChange")
class LevelChange(Resource):
    @logger.doc(security=None)
    @logger.response(201, "Sucess", generic_success_response)
    @logger.response(415, "Error", generic_error_response)
    @logger.response(500, "Internal Server Error", generic_error_response)
    def post(self):
        server_time = datetime.datetime.now()
        dt_string = server_time.strftime("%d/%m/%Y %H:%M:%S")
        level_data = request.get_json()
        z = set(level_data.keys()).intersection(required_data_levelChange)
        if request.is_json:
            if len(z) == len(required_data_levelChange):
                try:
                    level_input = {
                            "playerId": level_data["playerId"],
                            "roomId": level_data["roomId"],
                            "messageId": level_data["messageId"],
                            "sceneName": level_data["sceneName"],
                            "localTime": level_data["localTime"],
                            "serverTime": server_time,
                            "server-timestamp": dt_string,
                            "levelID": level_data["levelID"],
                            "levelStatus": level_data["levelStatus"]
                    }
                    db_level.insert_one(level_input)
                    return {"status": "success"}, 201
                except Exception as ex:
                    return {"error": f"{ex}"}, 500
            else:
                return {"error": f"Request Json must content following keys for level change: {required_data_levelChange}"}, 415
        return {"error": "Request must be JSON"}, 415

@logger.route("/logMisc")
class LogMisc(Resource):
    @logger.doc(security=None)
    @logger.response(201, "Sucess", generic_success_response)
    @logger.response(415, "Error", generic_error_response)
    @logger.response(500, "Internal Server Error", generic_error_response)
    def post(self):
        server_time = datetime.datetime.now()
        dt_string = server_time.strftime("%d/%m/%Y %H:%M:%S")
        misc_data = request.get_json()
        z = set(misc_data.keys()).intersection(required_data_misc)
        if request.is_json:
            if len(z) == len(required_data_misc):
                try:
                    misc_input = {
                            "playerId": misc_data["playerId"],
                            "localTime": misc_data["localTime"],
                            "serverTime": server_time,
                            "server-timestamp": dt_string,
                            "data": misc_data["jsonData"],
                    }
                    db_misc.insert_one(misc_input)
                    return {"status": "success"}, 201
                except Exception as ex:
                    return {"error": f"{ex}"}, 500
            else:
                return {"error": f"Request Json must content following keys for misc log: {required_data_misc}"}, 415
        return {"error": "Request must be JSON"}, 415


@logger.route("/status")
class Status(Resource):
    @logger.doc(security=None)
    def get(self):
        return {"status": "online"}, 200
