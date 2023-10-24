import jwt
import datetime
import os
from flask import Flask, request
from flask_mysqldb import MySQL

server = Flask(__name__)
mysql = MySQL(server)

server.config["MYSQL_HOST"] = os.environ.get("MYSQL_HOST")
server.config["MYSQL_PORT"] = int(os.environ.get("MYSQL_PORT", "3306"))
server.config["MYSQL_USER"] = os.environ.get("MYSQL_USER")
server.config["MYSQL_PASSWORD"] = os.environ.get("MYSQL_PASSWORD")
server.config["MYSQL_DB"] = os.environ.get("MYSQL_DB")
JWT_SECRET = os.environ.get("JWT_SECRET")


def create_jwt(username, secret, authz):
    return jwt.encode(
        {
            "username": username,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1),
            "iat": datetime.datetime.utcnow(),
            "admin": authz,
        },
        secret,
        algorithm="HS256",
    )


@server.route("/login", methods=["POST"])
def login():
    auth = request.authorization
    if not auth:
        return {"service": "Auth", "message": "Missing credentials"}, 401
    cur = mysql.connection.cursor()
    res = cur.execute("SELECT email, password FROM user WHERE email=%s", (auth.username,))
    if res > 0:
        user_row = cur.fetchone()
        email = user_row[0]
        password = user_row[1]
        if auth.username != email or auth.password != password:
            return {"service": "Auth", "message": "Invalid creds"}, 401
        else:
            return create_jwt(auth.username, JWT_SECRET, True), 200
    else:
        return {"service": "Auth", "message": "Invalid creds"}, 401


@server.route("/validate", methods=["POST"])
def validate():
    encoded_jwt = request.headers["Authorization"]
    if not encoded_jwt:
        return {"service": "Auth", "message": "Missing credentials"}, 401
    encoded_jwt = encoded_jwt.split(" ")[1]
    try:
        decoded = jwt.decode(encoded_jwt, JWT_SECRET, algorithm=["HS256"])
        return decoded, 200
    except Exception as err:
        return {"service": "Auth", "message": f"Not authorized {err}"}, 403


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=5000)
