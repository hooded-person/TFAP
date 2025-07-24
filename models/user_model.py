from utils.db_utils import db, generate_user_id

class UserModel(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.String(32), primary_key=True, default=generate_user_id)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True)
    auth_token = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(128), unique=True, nullable=False)
    show_email = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f"[User; {self.user_id}] <User {self.username} ({self.email})>"