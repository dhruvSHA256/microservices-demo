import gridfs
import pika
import json
from flask import Flask, request, send_file
from flask_pymongo import PyMongo
from pymongo import MongoClient
import auth_svc
from storage import util
from bson.objectid import ObjectId
from config import RABBITMQ_HOST, SERVICE_NAME, MONGO_URI, MONGO_HOST, MONGO_PORT


server = Flask(__name__)
server.config["MONGO_URI"] = MONGO_URI
client = MongoClient(MONGO_HOST, int(MONGO_PORT))
db_video = client.video
db_audio = client.audio
fs_video = gridfs.GridFS(db_video)
fs_audio = gridfs.GridFS(db_audio)

connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
channel = connection.channel()


@server.route("/login", methods=["POST"])
def login():
    token, err = auth_svc.login(request)
    if not err:
        return token
    else:
        return {"service": SERVICE_NAME, "message": f"Internal server error: {err}"}, 500


@server.route("/upload", methods=["POST"])
def upload():
    jwt_token, err = auth_svc.validate(request)
    if err or not jwt_token:
        return {"service": SERVICE_NAME, "message": f"Error: {err}"}, 400
    jwt_obj = json.loads(jwt_token)
    if len(request.files) > 1 or len(request.files) < 1:
        return {"service": SERVICE_NAME, "message": "exactly one file required"}, 400
    for _, f in request.files.items():
        err = util.upload(f, fs_video, channel, jwt_obj)
        if err:
            return {"service": SERVICE_NAME, "message": f"Error: {err}"}, 400
    return {"service": SERVICE_NAME, "message": "Success"}, 200


@server.route("/download", methods=["GET"])
def download():
    jwt_token, err = auth_svc.validate(request)
    if err or not jwt_token:
        return {"service": SERVICE_NAME, "message": f"Error f{err}"}, 400
    fid_string = request.args.get("fid")
    if not fid_string:
        return {"service": SERVICE_NAME, "message": "fid is required"}, 400
    try:
        output = fs_audio.get(ObjectId(fid_string))
        return send_file(output, download_name=f"{fid_string}.mp3")
    except Exception as err:
        return {"service": SERVICE_NAME, "message": f"Internal server error: {err}"}, 500


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8080, debug=True)
