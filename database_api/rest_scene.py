from bson import ObjectId
from flask import request
from flask_restx import Resource, fields
from pymongo.cursor import Cursor
from common import build_pymongo_connection, api

databasedb = build_pymongo_connection(f"./config_scene.json")
scene_db = databasedb["scenarios-v2"]

scene = api.namespace(
    "Scene Data",
    description="Endpoints to get and post various scene information", path="/")


generic_error_response = scene.model("GenericErrorResponse", {
    "message": fields.String(required=True)
})

generic_success_response = scene.model("GenericSuccessResponse", {
    "success": fields.String(required=True),
    "message": fields.String
})


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
    "admin": fields.Boolean(required=True),
    "restrictions": fields.List(fields.String)
})

role_locale_payload = scene.model("RoleLocalePayload", {
    "name": fields.String(required=True),
    "description": fields.List(fields.String, required=True)
})

role_result = scene.model("RoleResult", {
    "id": fields.String(required=True),
    "mode": fields.String(required=True),
    "spawnPosition": fields.String(required=True),
    "maxCount": fields.Integer(required=True),
    "admin": fields.Boolean(required=True),
    "restrictions": fields.List(fields.String),
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
                    {"id": ObjectId(request.args.get("id"))},
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
            return {"result": serialize_cursor(scene_db.find())}, 200
        else:
            return {"result": serialize_cursor(scene_db.aggregate(pipeline))}, 200


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
                # There must be a nicer way to do this
                projection={
                    f"{role_slug}.mode": 1,
                    f"{role_slug}.spawnPosition": 1,
                    f"{role_slug}.maxCount": 1,
                    f"{role_slug}.admin": 1,
                    f"{role_slug}.disabilities": 1,
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
            role_data["id"] = request.args.get("identifier")
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
