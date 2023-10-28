import os

MONGO_HOST = os.environ.get("MONGO_HOST") or "mongodb"
MONGO_PORT = os.environ.get("MONGO_PORT") or 27017
RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST") or "rabbitmq"
AUDIO_QUEUE = os.environ.get("AUDIO_QUEUE") or "audio"
GATEWAY_HOST = os.environ.get("GATEWAY_HOST") or "gateway"
GATEWAY_PORT = os.environ.get("GATEWAY_PORT") or "8080"
GATEWAY_URI = f"http://{GATEWAY_HOST}:{GATEWAY_PORT}"
SERVICE_NAME = os.environ.get("SERVICE_NAME") or "converter"
