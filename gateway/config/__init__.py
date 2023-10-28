import os

AUTH_SVC_HOST = os.environ.get("AUTH_SVC_HOST") or "auth"
AUTH_SVC_PORT = os.environ.get("AUTH_SVC_PORT") or "5000"
AUTH_SVC_URL = f"http://{AUTH_SVC_HOST}:{AUTH_SVC_PORT}"
MONGO_HOST = os.environ.get("MONGO_HOST") or "localhost"
MONGO_PORT = os.environ.get("MONGO_PORT") or 27017
MONGO_VIDEODB = os.environ.get("MONGO_VIDEODB") or "video"
MONGO_AUDIOB = os.environ.get("MONGO_AUDIOB") or "audio"
RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST") or "rabbitmq"
VIDEO_QUEUE = os.environ.get("VIDEO_QUEUE") or "video"
SERVICE_NAME = os.environ.get("SERVICE_NAME") or "auth"
MONGO_URI = f"mongodb://{MONGO_HOST}:{MONGO_PORT}/{MONGO_VIDEODB}"
MONGO_VIDEO_URI = f"mongodb://{MONGO_HOST}:{MONGO_PORT}/{MONGO_VIDEODB}"
MONGO_AUDIO_URI = f"mongodb://{MONGO_HOST}:{MONGO_PORT}/{MONGO_AUDIOB}"
