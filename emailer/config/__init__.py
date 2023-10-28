import os

MONGO_HOST = os.environ.get("MONGO_HOST") or "mongodb"
MONGO_PORT = os.environ.get("MONGO_PORT") or 27017
RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST") or "rabbitmq"
AUDIO_QUEUE = os.environ.get("AUDIO_QUEUE") or "audio"
SERVICE_NAME = os.environ.get("SERVICE_NAME") or "converter"
