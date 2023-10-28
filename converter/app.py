import pika
import sys
import os
from pymongo import MongoClient
import gridfs
import json
import tempfile
from bson.objectid import ObjectId
import moviepy.editor
from config import MONGO_HOST, MONGO_PORT, RABBITMQ_HOST, VIDEO_QUEUE, AUDIO_QUEUE, SERVICE_NAME

client = MongoClient(MONGO_HOST, int(MONGO_PORT))
db_video = client.video
db_audio = client.audio
fs_video = gridfs.GridFS(db_video)
fs_audio = gridfs.GridFS(db_audio)


def convert_to_audio(message, channel):
    message = json.loads(message)
    tf = tempfile.NamedTemporaryFile()
    out = fs_video.get(ObjectId(message["video_fid"]))
    tf.write(out.read())
    audio = moviepy.editor.VideoFileClip(tf.name).audio
    tf.close()
    tf_path = tempfile.gettempdir() + f"/{message['video_fid']}.mp3"
    audio.write_audiofile(tf_path)
    f = open(tf_path, "rb")
    data = f.read()
    fid = fs_audio.put(data)
    f.close()
    os.remove(tf_path)
    message["audio_fid"] = str(fid)

    try:
        channel.basic_publish(
            exchange="",
            routing_key=AUDIO_QUEUE,
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE),
        )
        return None, {"service": SERVICE_NAME, "audio_fid": message["audio_fid"]}
    except Exception as err:
        fs_audio.delete(fid)
        return True, {"service": SERVICE_NAME, "message": f"Failed to publish message: {err}"}


def callback(ch, method, properties, body):
    err, message = convert_to_audio(body, ch)
    if err:
        ch.basic_nack(delivery_tag=method.delivery_tag)
    else:
        ch.basic_ack(delivery_tag=method.delivery_tag)
    print(message, file=sys.stderr)


def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.basic_consume(queue=VIDEO_QUEUE, on_message_callback=callback)
    channel.start_consuming()


if __name__ == "__main__":
    main()
