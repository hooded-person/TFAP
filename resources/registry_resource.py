import os
from flask_restful import Resource, reqparse, fields, marshal_with
from services.registry_service import create_registry_entry, get_registry_entry_by_id, get_registry_entries
from flask import request, abort
from dotenv import load_dotenv

load_dotenv()
ALLOWED_REGISTRY_CREATORS = os.getenv("ALLOWED_REGISTRY_CREATORS")

registry_args = reqparse.RequestParser()
registry_args.add_argument("app_name", type=str, required=True, help="App name is required.")
registry_args.add_argument("allowed_origins", type=str, required=True, help="At least 1 origin has to be given")
registry_creation_fields = {
    "db_id": fields.String,
    "db_secret": fields.String,
    "app_name": fields.String,
    "allowed_origins": fields.String,
    "authorized": fields.Boolean,
}
registry_limited_fields = {
    "db_id": fields.String,
    "app_name": fields.String,
    "authorized": fields.Boolean,
}

class RegistryResource(Resource): #queries all registry entries and allows creation of new entries
    @marshal_with(registry_limited_fields)
    def get(self):
        return get_registry_entries()

    @marshal_with(registry_creation_fields)
    def post(self):
        origin = request.headers.get("Origin")
        if origin != ALLOWED_REGISTRY_CREATORS:
            abort(403, description="Forbidden Origin.")
        args = registry_args.parse_args()
        app_name = args["app_name"]
        allowed_origins = [args["allowed_origins"], ""]
        allowed_origins = ",".join(allowed_origins)
        new_entry = create_registry_entry(app_name, allowed_origins=allowed_origins)
        return new_entry, 201

class RegistryLookupResource(Resource): #queries a singular registry instance
    @marshal_with(registry_limited_fields)
    def get(self, db_id):
        entry = get_registry_entry_by_id(db_id)
        if entry:
            return entry, 200
        abort(404, description="Database not found.")