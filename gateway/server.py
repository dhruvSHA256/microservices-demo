import gridfs
import pika
import json
from flask import Flask, request, send_file
from flask_pymongo import PyMongo
from auth import validate
from auth_svc import access
from storage import util
from bson.objectid import ObjectId
from config import MONGO_AUDIO_URI, MONGO_VIDEO_URI, RABBITMQ_HOST, SERVICE_NAME, MONGO_URI


server = Flask(__name__)
server.config["MONGO_URI"] = MONGO_URI
mongo_video = PyMongo(server, uri=MONGO_VIDEO_URI)
mongo_audio = PyMongo(server, uri=MONGO_AUDIO_URI)
fs_audio = gridfs.GridFS(mongo_video.db)
fs_audio = gridfs.GridFS(mongo_audio.db)
connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
channel = connection.channel()


@server.route("/login", methods=["POST"])
def login():
    token, err = access.login(request)
    if not err:
        return token
    else:
        return {"service": SERVICE_NAME, "message": f"Internal server error: {err}"}, 500


@server.route("/upload", methods=["POST"])
def upload():
    jwt_token, err = validate.token(request)
    if err or not jwt_token:
        return {"service": SERVICE_NAME, "message": f"Error f{err}"}, 400
    jwt_obj = json.loads(jwt_token)
    if jwt_obj["admin"]:
        if len(request.files) > 1 or len(request.files) < 1:
            return {"service": SERVICE_NAME, "message": "exactly one file required"}, 400
        for _, f in request.files.items():
            err = util.upload(f, fs_audio, channel, jwt_obj)
            if err:
                return err, 400
        return {"service": SERVICE_NAME, "message": "Success"}, 200
    else:
        return {"service": SERVICE_NAME, "message": "Not Authorized"}, 401


@server.route("/download", methods=["GET"])
def download():
    jwt_token, err = validate.token(request)
    if err or not jwt_token:
        return {"service": SERVICE_NAME, "message": f"Error f{err}"}, 400
    jwt_obj = json.loads(jwt_token)
    if jwt_obj["admin"]:
        fid_string = request.args.get("fid")
        if not fid_string:
            return {"service": SERVICE_NAME, "message": "fid is required"}, 400
        try:
            output = fs_audio.get(ObjectId(fid_string))
            return send_file(output, download_name=f"{fid_string}.mp3")
        except Exception as err:
            return {"service": SERVICE_NAME, "message": f"Internal server error: {err}"}, 500

    else:
        return {"service": SERVICE_NAME, "message": "Not Authorized"}, 401


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8080, debug=True)
