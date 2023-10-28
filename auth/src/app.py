import jwt
import datetime
from flask import Flask, request
from sqlalchemy import create_engine
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy_utils import database_exists, create_database
from werkzeug.security import generate_password_hash, check_password_hash
from enum import Enum
from config import JWT_SECRET, SERVICE_NAME, SQLALCHEMY_DATABASE_URI

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Role(Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    email = db.Column(db.String(), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)
    role = db.Column(db.Enum(Role), default=Role.GUEST)

    def __init__(self, email, password, name=""):
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


@app.route("/login", methods=["POST"])
def login():
    auth = request.authorization
    if not auth:
        return {"service": SERVICE_NAME, "message": "Missing credentials"}, 401
    email = auth.username
    password = auth.password
    user = User.query.filter(User.email == email).first()
    if user:
        if user.check_password(password):
            return user.create_jwt(JWT_SECRET, "user"), 200
        else:
            return {"service": SERVICE_NAME, "message": "Invalid creds"}, 401
    else:
        return "Invalid creds", 401


@app.route("/signup", methods=["POST"])
def signup():
    auth = request.authorization
    if not auth:
        return {"service": SERVICE_NAME, "message": "Missing credentials"}, 401
    email = auth.username
    password = auth.password
    user = User(email, password)
    try:
        db.session.add(user)
        db.session.commit()
        return user.email, 200
    except Exception as err:
        return {"service": SERVICE_NAME, "message": f"{err}"}, 400


@app.route("/validate", methods=["POST"])
def validate():
    encoded_jwt = request.headers["Authorization"]
    if not encoded_jwt:
        return {"service": SERVICE_NAME, "message": "Missing credentials"}, 401
    encoded_jwt = encoded_jwt.split(" ")[1]
    try:
        decoded = jwt.decode(encoded_jwt, JWT_SECRET, algorithms=["HS256"])
        return decoded, 200
    except Exception as err:
        return f"Not authorized {err}", 403


if __name__ == "__main__":
    engine = create_engine(SQLALCHEMY_DATABASE_URI)
    if not database_exists(engine.url):
        create_database(engine.url)
    User.metadata.create_all(engine)
    app.run(host="0.0.0.0", port=5000)
