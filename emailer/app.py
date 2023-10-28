import pika
import sys
import json
from config import RABBITMQ_HOST, AUDIO_QUEUE


def send_mail(message, channel):
    message = json.loads(message)
    return None, message["audio_fid"]


def callback(ch, method, properties, body):
    err, message = send_mail(body, ch)
    if err:
        ch.basic_nack(delivery_tag=method.delivery_tag)
    else:
        ch.basic_ack(delivery_tag=method.delivery_tag)
    print(message, file=sys.stderr)


def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.basic_consume(queue=AUDIO_QUEUE, on_message_callback=callback)
    channel.start_consuming()


if __name__ == "__main__":
    main()
