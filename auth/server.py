import jwt
import datetime
import os
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from enum import Enum


POSTGRES_USER = os.environ.get("POSTGRES_USER") or "postgres"
POSTGRES_HOST = os.environ.get("POSTGRES_HOST") or "localhost"
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD") or "postgres"
POSTGRES_DB = os.environ.get("POSTGRES_DB") or "auth"
POSTGRES_PORT = os.environ.get("POSTGRES_PORT") or 5432
JWT_SECRET = os.environ.get("JWT_SECRET") or "sarcasm"

server = Flask(__name__)
server.config[
    "SQLALCHEMY_DATABASE_URI"
] = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

db = SQLAlchemy(server)
migrate = Migrate(server, db)


class Role(Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    email = db.Column(db.String())
    password = db.Column(db.String(), nullable=False)
    role = db.Column(db.Enum(Role), default=Role.GUEST)

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = generate_password_hash(password)

    def __repr__(self):
        return f"<User {self.email}>"

    def create_jwt(self, secret, role):
        return jwt.encode(
            {
                "email": self.email,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1),
                "iat": datetime.datetime.utcnow(),
                "role": role,
            },
            secret,
            algorithm="HS256",
        )

    def check_password(self, password):
        return check_password_hash(self.password, password)


@server.route("/login", methods=["POST"])
def login():
    auth = request.authorization
    if not auth:
        return {"service": "Auth", "message": "Missing credentials"}, 401
    email = auth.username
    password = auth.password
    user = User.query.filter(User.email == email).first()
    if user:
        if user.check_password(password):
            return user.create_jwt(JWT_SECRET, "user"), 200
        else:
            return {"service": "Auth", "message": "Invalid creds"}, 401
    else:
        return {"service": "Auth", "message": "Invalid creds"}, 401


@server.route("/validate", methods=["POST"])
def validate():
    encoded_jwt = request.headers["Authorization"]
    if not encoded_jwt:
        return {"service": "Auth", "message": "Missing credentials"}, 401
    encoded_jwt = encoded_jwt.split(" ")[1]
    try:
        decoded = jwt.decode(encoded_jwt, JWT_SECRET, algorithms=["HS256"])
        return decoded, 200
    except Exception as err:
        return {"service": "Auth hello", "message": f"Not authorized {err}"}, 403


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=5000)
