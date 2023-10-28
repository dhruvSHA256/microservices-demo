import pika
import json
from config import VIDEO_QUEUE, SERVICE_NAME


def upload(f, fs, channel, jwt_obj):
    try:
        fid = fs.put(f)
    except Exception as err:
        return {"service": SERVICE_NAME, "message": f"Internal server error: {err}"}, 500
    message = {"video_fid": str(fid), "audio_fid": None, "email": jwt_obj["email"]}
    try:
        channel.basic_publish(
            exchange="",
            routing_key=VIDEO_QUEUE,
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE),
        )
    except Exception as err:
        fs.delete(fid)
        return {"service": SERVICE_NAME, "message": f"Internal server error: {err}"}, 500
