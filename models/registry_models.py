from utils.db_utils import db

class RegistryModel(db.Model):
    __tablename__ = "registry"

    db_id = db.Column(db.String(12), primary_key=True)
    db_secret = db.Column(db.String(128), unique=True, nullable=False)
    app_name = db.Column(db.String(100), nullable=False)
    allowed_origins = db.Column(db.String, nullable=False)
    authorized = db.Column(db.Boolean, default=True, nullable=False)

    def __repr__(self):
        return f"<Registry db_id={self.db_id}, app={self.app_name}>"