import pika
import json
import os


def upload(f, fs, channel, jwt_obj):
    try:
        fid = fs.put(f)
    except Exception as err:
        return {"service": "Gateway", "message": f"Internal server error: {err}"}, 500
    message = {"video_fid": str(fid), "mp3_fid": None, "username": jwt_obj["username"]}
    try:
        channel.basic_publish(
            exchange="",
            routing_key=os.environ.get("VIDEO_QUEUE"),
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE),
        )
    except Exception as err:
        fs.delete(fid)
        return {"service": "Gateway", "message": f"Internal server error: {err}"}, 500
