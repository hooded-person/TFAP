from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api, reqparse, fields, marshal_with, abort
from dotenv import load_dotenv
import os

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
load_dotenv()
API_LOCATION = str(os.getenv("API_LOCATION"))
API_PORT = int(os.getenv("API_PORT"))
CLIENT_FRONT_END_LOCATION = str(os.getenv("CLIENT_FRONT_END_LOCATION"))
CORS(app, origins=[CLIENT_FRONT_END_LOCATION])
db = SQLAlchemy(app)
api = Api(app)

class UserModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return f"User(name = {self.name}, email = {self.email}, password = {self.password})"

user_args = reqparse.RequestParser()
user_args.add_argument("name", type=str, required=True, help="name can't be blank")
user_args.add_argument("email", type=str, required=True, help="email can't be blank")
user_args.add_argument("password", type=str, required=True, help="password can't be blank")

userFields = {
    "id":fields.Integer,
    "name":fields.String,
    "email":fields.String,
    "password":fields.String
}

class Users(Resource):
    @marshal_with(userFields)
    def get(self):
        users = UserModel.query.all()
        return users
    
    @marshal_with(userFields)
    def post(self):
        args = user_args.parse_args()
        user = UserModel(name=args['name'], email=args['email'], password=args['password'])
        db.session.add(user)
        db.session.commit()
        users = UserModel.query.all()
        return users, 201

class User(Resource):
    @marshal_with(userFields)
    def get(self, idmethod, id):
        if idmethod == "idn":
            user = UserModel.query.filter_by(id=id).first()
            if not user:
                abort(404,err="User not found")
            return user
        if idmethod == "username":
            user = UserModel.query.filter_by(name=id).first()
            if not user:
                abort(404, err="User not found")
            return user
        if idmethod == "email":
            user = UserModel.query.filter_by(email=id).first()
            if not user:
                abort(404, err="User not found")
            return user
        
    @marshal_with(userFields)
    def patch(self, idmethod, id):
        if idmethod == "idn":
            args = user_args.parse_args()
            user = UserModel.query.filter_by(id=id).first()
            if not user:
                abort(404, err="User not found")
            user.name = args["name"]
            user.email = args["email"]
            user.password = args["password"]
            db.session.commit()
            user = UserModel.query.filter_by(id=id).first()
            return user
        else:
            return abort(418, err="Unless you use /api/users/idn/<id_number> I dont want it.")
    
    def delete(self, idmethod, id):
        if idmethod == "idn":
            user = UserModel.query.filter_by(id=id).first()
            if not user:
                abort(404, err="User not found")
            db.session.delete(user)
            db.session.commit()
            return {"message": "User deleted successfully"}, 200
        if idmethod == "username":
            user = UserModel.query.filter_by(name=id).first()
            if not user:
                abort(404, err="User not found")
            db.session.delete(user)
            db.session.commit()
            return {"message": "User deleted successfully"}, 200
        if idmethod == "email":
            user = UserModel.query.filter_by(email=id).first()
            if not user:
                abort(404, err="User not found")
            db.session.delete(user)
            db.session.commit()
            return {"message": "User deleted successfully"}, 200

api.add_resource(Users, "/api/users/")
api.add_resource(User, "/api/users/<idmethod>/<id>")

@app.route("/")
def index():
    return "<h1>JVM REST API</h1>"

if __name__ == '__main__':
    app.run(debug=True, host=API_LOCATION, port=API_PORT)