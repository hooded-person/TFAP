import os
from dotenv import load_dotenv
from models.registry_models import RegistryModel
from utils.db_utils import db, create_user_db
from sqlalchemy.exc import IntegrityError
from utils.db_utils import generate_ids

def get_registry_entries(): #gets all registry entries
    return RegistryModel.query.all()

def get_registry_entry_by_id(db_id:str): #gets a specific registry entry
    return RegistryModel.query.filter_by(db_id=db_id).first()

def create_registry_entry(app_name:str, allowed_origins:str): #creates a new registry entry
    db_id, db_secret = generate_ids()
    new_entry = RegistryModel(
        db_id=db_id,
        db_secret=db_secret,
        app_name=app_name,
        allowed_origins=allowed_origins,
    )
    
    try:
        db.session.add(new_entry)
        db.session.commit()
        create_user_db(db_secret)
        return new_entry
    except IntegrityError:
        db.session.rollback()
        return None

def is_frontend_authorized(origin:str) -> bool: #checks frontend authorization
    match = RegistryModel.query.filter_by(allowed_origins=origin, authorized=True).first()
    return match is not None

def get_allowed_origins(partial=False): #returns a list of allowed origins
    with db.engine.connect() as connection:
        result = connection.execute(
            db.select(RegistryModel.allowed_origins).where(RegistryModel.authorized == True)
        )
        authList = [
            origin.strip()
            for row in result
            for origin in row[0].split(",")
            if origin.strip()
        ]
        load_dotenv()
        ALLOWED_REGISTRY_CREATORS = os.getenv("ALLOWED_REGISTRY_CREATORS")
        allowed_registry_creators_list = [origin.strip() for origin in ALLOWED_REGISTRY_CREATORS.split(",") if origin.strip()]
        for check_for_dupes in allowed_registry_creators_list:
            if check_for_dupes not in authList:
                authList.append(check_for_dupes)
        if partial:
            return ALLOWED_REGISTRY_CREATORS
        else:
            return authList