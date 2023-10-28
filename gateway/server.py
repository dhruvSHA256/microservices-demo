import gridfs
import pika
import json
from flask import Flask, request, send_file
from flask_pymongo import PyMongo
from auth import validate
from auth_svc import access
from storage import util
from bson.objectid import ObjectId
import os

MONGO_HOST = os.environ.get("MONGO_HOST") or "localhost"
MONGO_PORT = os.environ.get("MONGO_PORT") or 27017
MONGO_VIDEODB = os.environ.get("MONGO_VIDEODB") or "video"
MONGO_AUDIOB = os.environ.get("MONGO_AUDIOB") or "audio"
RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST") or "rabbitmq"

server = Flask(__name__)
server.config["MONGO_URI"] = f"mongodb://{MONGO_HOST}:{MONGO_PORT}/{MONGO_VIDEODB}"
mongo_video = PyMongo(server, uri=f"mongodb://{MONGO_HOST}:{MONGO_PORT}/{MONGO_VIDEODB}")
mongo_audio = PyMongo(server, uri=f"mongodb://{MONGO_HOST}:{MONGO_PORT}/{MONGO_AUDIOB}")
fs_videos = gridfs.GridFS(mongo_video.db)
fs_mp3s = gridfs.GridFS(mongo_audio.db)
connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
channel = connection.channel()


@server.route("/login", methods=["POST"])
def login():
    token, err = access.login(request)
    if not err:
        return token
    else:
        return {"service": "Gateway", "message": f"Internal server error: {err}"}, 500


@server.route("/upload", methods=["POST"])
def upload():
    jwt_token, err = validate.token(request)
    if err or not jwt_token:
        return {"service": "Gateway", "message": f"Error f{err}"}, 400
    jwt_obj = json.loads(jwt_token)
    if jwt_obj["admin"]:
        if len(request.files) > 1 or len(request.files) < 1:
            return {"service": "Gateway", "message": "exactly one file required"}, 400
        for _, f in request.files.items():
            err = util.upload(f, fs_videos, channel, jwt_obj)
            if err:
                return err, 400
        return {"service": "Gateway", "message": "Success"}, 200
    else:
        return {"service": "Gateway", "message": "Not Authorized"}, 401


@server.route("/download", methods=["GET"])
def download():
    jwt_token, err = validate.token(request)
    if err or not jwt_token:
        return {"service": "Gateway", "message": f"Error f{err}"}, 400
    jwt_obj = json.loads(jwt_token)
    if jwt_obj["admin"]:
        fid_string = request.args.get("fid")
        if not fid_string:
            return {"service": "Gateway", "message": "fid is required"}, 400
        try:
            output = fs_mp3s.get(ObjectId(fid_string))
            return send_file(output, download_name=f"{fid_string}.mp3")
        except Exception as err:
            return {"service": "Gateway", "message": f"Internal server error: {err}"}, 500

    else:
        return {"service": "Gateway", "message": "Not Authorized"}, 401


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8080, debug=True)
