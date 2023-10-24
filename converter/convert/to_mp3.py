import pika
import json
import tempfile
import os
from bson.objectid import ObjectId
import moviepy.editor


def start(message, fs_videos, fs_mp3s, channel):
    message = json.loads(message)

    # empty temp file
    with tempfile.NamedTemporaryFile() as tf:
        # video contents
        out = fs_videos.get(ObjectId(message["video_fid"]))
        # add video contents to empty file
        tf.write(out.read())
        # create audio from temp video file
        audio = moviepy.editor.VideoFileClip(tf.name).audio
        # write audio to the file
        tf_path = tempfile.gettempdir() + f"/{message['video_fid']}.mp3"
        audio.write_audiofile(tf_path)

        # save file to mongo
        with open(tf_path, "rb") as f:
            data = f.read()
            fid = fs_mp3s.put(data)
            os.remove(tf_path)

    message["mp3_fid"] = str(fid)

    try:
        channel.basic_publish(
            exchange="",
            routing_key=os.environ.get("MP3_QUEUE"),
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE),
        )
    except Exception as err:
        fs_mp3s.delete(fid)
        return {"service": "Converter", "message": f"Failed to publish message: {err}"}, 500
