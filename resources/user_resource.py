import os
from flask_restful import Resource, reqparse, fields, marshal_with
from flask import request, abort
from services.user_service import get_all_users, get_user_by, create_user
from services.registry_service import get_registry_entry_by_id, get_allowed_origins
from werkzeug.security import generate_password_hash

user_args = reqparse.RequestParser()
user_args.add_argument("username", type=str, required=True, help="Name is required.")
user_args.add_argument("email", type=str)
user_args.add_argument("password", type=str, required=True, help="Password is required.")

user_auth_args = reqparse.RequestParser()
user_auth_args.add_argument("username_or_email", type=str, required=True, help="Either an username or an email is required.")
user_auth_args.add_argument("password", type=str, required=True, help="Password is required.")

user_creation_fields = {
    "user_id": fields.String,
    "username": fields.String,
    "email": fields.String,
    "message": fields.String,
}
user_limited_fields = {
    "user_id": fields.String,
    "username": fields.String,
    "email": fields.String,
}

class UserListResource(Resource): #allows all CRUD operations on all of the users (in that database)
    @marshal_with(user_limited_fields)
    def get(self, db_id):
        return get_all_users(db_id), 200
    
    @marshal_with(user_creation_fields)
    def post(self, db_id):
        registry_entry = get_registry_entry_by_id(db_id)
        allowed_origins = registry_entry.allowed_origins.split(",")
        allowed_origins = [origin.strip() for origin in allowed_origins]
        origin = request.headers.get("Origin")
        if origin not in allowed_origins:
            abort(403, description="Forbidden Origin.")
        args = user_args.parse_args()
        new_user = create_user(
            db_id,
            username=args["username"],
            email=args["email"],
            password=args["password"]
        )
        return new_user

class UserResource(Resource): #queries a singular user instance
    @marshal_with(user_limited_fields)
    def get(self, db_id, id_method, identifier):
        user = get_user_by(db_id, id_method, identifier)
        if user is not None:
            return user
        abort(404, description="User not found.")

class UserAuthenticateResource(Resource): #authenticates a user against the database
    def post(self, db_id):
        registry_entry = get_registry_entry_by_id(db_id)
        allowed_origins = registry_entry.allowed_origins.split(",")
        allowed_origins = [origin.strip() for origin in allowed_origins]
        origin = request.headers.get("Origin")
        if origin not in allowed_origins:
            abort(403, description="Forbidden Origin.")
        args = user_auth_args.parse_args()
        password_hash = generate_password_hash(args["password"])
        id_method = "username"
        identifier = args["username_or_email"]
        user = get_user_by(db_id, id_method, identifier)
        if user is not None:
            if user.password == password_hash:
                return True #temporary
            return False #temporary
        id_method = "email"
        user = get_user_by(db_id, id_method, identifier)
        if user is not None:
            if user.password == password_hash:
                return True #temporary
            return False #temporary
        abort(404, "User not found")
    """
    dont know when i will finish this lol
    
    def placeholder(db_id):
        registry_entry = get_registry_entry_by_id(db_id)
        allowed_origins = [origin.strip() for origin in registry_entry.allowed_origins.split(",") if origin.strip()]
        ALLOWED_BACKEND_ACCESS = get_allowed_origins(partial=True)
        allowed_registry_creators_list = [origin.strip() for origin in ALLOWED_BACKEND_ACCESS.split(",") if origin.strip()]
        for check_for_dupes in allowed_registry_creators_list:
            if check_for_dupes not in allowed_origins:
                allowed_origins.append(check_for_dupes)
        origin = request.headers.get("Origin")
        if origin not in allowed_originst:
            abort(403, description="Forbidden Origin.")"""
