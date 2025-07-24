from flask import abort
from models.user_model import UserModel
from utils.db_utils import db, connect_with_user_db, generate_user_id
from werkzeug.security import generate_password_hash

def create_user(db_id:str, username, password, email=None): #creates a new user in the specified database
    db, app = connect_with_user_db(db_id)
    with app.app_context():
        if email:
            if UserModel.query.filter_by(email=email).first():
                abort(400, description="Email has already been registered.")
        if UserModel.query.filter_by(username=username).first():
            abort(400, description="Username has already been taken.")
    
        hashed_password = generate_password_hash(password)
        new_user = UserModel(
            user_id=generate_user_id(),
            username=username,
            email=email,
            password_hash=hashed_password
        )

        db.session.add(new_user)
        new_user =  {
            "user_id":new_user.user_id,
            "username":new_user.username,
            "email":new_user.email,
            "message":f"User created succesfully."
        }
        db.session.commit()
        return new_user

def get_all_users(db_id:str): #returns all users in the specified database
    db, app = connect_with_user_db(db_id)
    with app.app_context():
        users = UserModel.query.all()
        return [
            {
                "user_id": user.user_id,
                "username": user.username,
                "email": user.email if user.show_email else "Email not publicly shared."
            }
            for user in users
        ]

def get_user_by(db_id:str, id_method:str, identifier:str): #returns a user from a specific database by the specified method and identifier
    db, app = connect_with_user_db(db_id)
    with app.app_context():
        if id_method == "id":
            user = UserModel.query.filter_by(user_id=identifier).first()
            if not user:
                return None
            return {
                "user_id": user.user_id,
                "username": user.username,
                "email": user.email if user.show_email else "Email not publicly shared."
            }
    
        elif id_method == "username":
            user = UserModel.query.filter_by(username=identifier).first()
            if not user:
                return None
            return {
                "user_id": user.user_id,
                "username": user.username,
                "email": user.email if user.show_email else "Email not publicly shared."
            } 
       
        elif id_method == "email":
            user = UserModel.query.filter_by(email=identifier).first()
            if not user:
                return None
            return {
                "user_id": user.user_id,
                "username": user.username,
                "email": user.email if user.show_email else "Email not publicly shared."
            }
        
        else:
            abort(404, description="Method not found.")

def update_user(db_id, identifier, username=None, email=None, password=None): #updates a user in the specified database
    db, app = connect_with_user_db(db_id)
    with app.app_context():
        user = UserModel.query.filter_by(id=identifier).first()
        if not user:
            abort(404, description="User not found")
        if username:
            user.name = username
        if email:
            user.email = email
        if password:
            user.password = generate_password_hash(password)
        db.session.commit()
        return user
    
def delete_user(db_id, method, value): #deletes a user from the specified database
    db, app = connect_with_user_db(db_id)
    with app.app_context():
        user = get_user_by(method,value)
        if not user:
            abort(404, description="User not found.")
        db.session.delete(user)
        db.session.commit()
        return {"message":"User deleted succesfully."}