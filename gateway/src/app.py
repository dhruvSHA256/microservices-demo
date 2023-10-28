import gridfs
import pika
import json
from flask import Flask, request, send_file
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from flask_migrate import Migrate
from sqlalchemy_utils import database_exists, create_database
from pymongo import MongoClient
import auth_svc
from storage import util
from bson.objectid import ObjectId
from config import RABBITMQ_HOST, SERVICE_NAME, MONGO_URI, MONGO_HOST, MONGO_PORT, SQLALCHEMY_DATABASE_URI, AUTH_SVC_URL


app = Flask(__name__)
app.config["MONGO_URI"] = MONGO_URI
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
db = SQLAlchemy(app)
migrate = Migrate(app, db)
migrate.init_app(app)

client = MongoClient(MONGO_HOST, int(MONGO_PORT))
db_video = client.video
db_audio = client.audio
fs_video = gridfs.GridFS(db_video)
fs_audio = gridfs.GridFS(db_audio)

connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
channel = connection.channel()


class Files(db.Model):
    __tablename__ = "files"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(), nullable=False)
    audio_fid = db.Column(db.String())
    video_fid = db.Column(db.String())

    def __init__(self, email, video_fid):
        self.email = email
        self.video_fid = video_fid


@app.route("/login", methods=["POST"])
def login():
    err, token = auth_svc.login(request)
    if not err:
        return token
    else:
        return {"service": SERVICE_NAME, "message": f"Internal server error: {err}"}, 500


@app.route("/signup", methods=["POST"])
def signup():
    err, resp = auth_svc.signup(request)
    if not err:
        return resp
    else:
        return {"service": SERVICE_NAME, "message": f"Internal server error: {err}"}, 500


@app.route("/upload", methods=["POST"])
def upload():
    err, jwt_token = auth_svc.validate(request)
    if err or not jwt_token:
        return {"service": SERVICE_NAME, "message": f"Error: {err}"}, 400
    jwt_obj = json.loads(jwt_token)
    if len(request.files) > 1 or len(request.files) < 1:
        return {"service": SERVICE_NAME, "message": "exactly one file required"}, 400
    for _, f in request.files.items():
        err, video_fid = util.upload(f, fs_video, channel, jwt_obj)
        db.session.add(Files(jwt_obj["email"], str(video_fid)))
        db.session.commit()
        if err:
            return {"service": SERVICE_NAME, "message": f"Error: {err}"}, 400
        return {"service": SERVICE_NAME, "message": f"Success: {video_fid}"}, 200


@app.route("/download", methods=["GET"])
def download():
    err, jwt_token = auth_svc.validate(request)
    if err or not jwt_token:
        return {"service": SERVICE_NAME, "message": f"Error f{err}"}, 400
    jwt_obj = json.loads(jwt_token)
    video_fid = request.args.get("fid")
    if not video_fid:
        return {"service": SERVICE_NAME, "message": "fid is required"}, 400
    record = Files.query.filter(Files.video_fid == video_fid).first()
    if not record:
        return {"service": SERVICE_NAME, "message": "Not Found"}, 404
    if record.email != jwt_obj["email"]:
        return {"service": SERVICE_NAME, "message": "Unauthorized"}, 401
    audio_fid = record.audio_fid
    if not audio_fid:
        return {"service": SERVICE_NAME, "message": "Not converted yet"}, 400

    try:
        output = fs_audio.get(ObjectId(audio_fid))
        return send_file(output, download_name=f"{audio_fid}.mp3")
    except Exception as err:
        return {"service": SERVICE_NAME, "message": f"Internal server error: {err}"}, 500


@app.route("/update", methods=["GET"])
def update():
    audio_fid = request.args.get("aid")
    video_fid = request.args.get("vid")
    file = Files.query.filter(Files.video_fid == video_fid).first()
    if file:
        file.audio_fid = audio_fid
        db.session.commit()
        return "success"
    else:
        return "fail", 404


if __name__ == "__main__":
    engine = create_engine(SQLALCHEMY_DATABASE_URI)
    if not database_exists(engine.url):
        create_database(engine.url)
    Files.metadata.create_all(engine)
    app.run(host="0.0.0.0", port=8080, debug=True)
