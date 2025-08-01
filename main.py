import os
from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from dotenv import load_dotenv
from utils.db_utils import db
from resources.registry_resource import RegistryLookupResource, RegistryResource
from resources.user_resource import UserListResource, UserResource, UserAuthenticateResource
from services.registry_service import get_allowed_origins
from utils.init_db import init_registry_database

try:
    init_registry_database()
except:
    print("registry already exists")

app = Flask(__name__)
api = Api(app)

load_dotenv()
API_LOCATION = os.getenv("API_LOCATION")
API_PORT = int(os.getenv("API_PORT"))
ALLOWED_REGISTRY_CREATORS = os.getenv("ALLOWED_REGISTRY_CREATORS")
DB_REGISTRY = os.getenv("DB_REGISTRY")

instance_path = os.path.join(os.getcwd(), "instance")
db_path = os.path.join(instance_path, DB_REGISTRY)

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

with app.app_context():
    origins = get_allowed_origins()
    CORS(app, origins=origins)

api.add_resource(RegistryResource, "/api/registry/")
api.add_resource(RegistryLookupResource, "/api/registry/<db_id>/")

api.add_resource(UserListResource, "/api/<db_id>/users/")
api.add_resource(UserResource, "/api/<db_id>/users/<id_method>/<identifier>/")
api.add_resource(UserAuthenticateResource, "/api/<db_id>/users/authenticate/")

if __name__ == "__main__":
    app.run(host=API_LOCATION, port=API_PORT, debug=False)
