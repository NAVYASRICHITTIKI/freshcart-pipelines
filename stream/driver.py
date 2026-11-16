
import json, os, sys
import pika

URL = os.environ.get("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/%2F")
EXCHANGE = "rapido-dispatch"
name, pattern = sys.argv[1], sys.argv[2]

conn = pika.BlockingConnection(pika.URLParameters(URL))
ch = conn.channel()
ch.exchange_declare(exchange=EXCHANGE, exchange_type="topic")
queue = ch.queue_declare(queue="", exclusive=True).method.queue   # private, server-named queue
ch.queue_bind(exchange=EXCHANGE, queue=queue, routing_key=pattern)
ch.basic_qos(prefetch_count=1)
print(f"[{name}] queue={queue} pattern={pattern}", flush=True)

def on_message(channel, method, properties, body):
    key = method.routing_key
    try:
        msg = json.loads(body)
    except ValueError:
        print(f"[{name}] NACK key={key} (not JSON)", flush=True)
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        return
    if "zone" not in msg:
        print(f"[{name}] NACK key={key} id={msg.get('id')} (missing zone)", flush=True)
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    else:
        print(f"[{name}] ACK key={key} id={msg['id']} {msg['type']} in {msg['zone']}", flush=True)
        channel.basic_ack(delivery_tag=method.delivery_tag)

ch.basic_consume(queue=queue, on_message_callback=on_message, auto_ack=False)
try:
    ch.start_consuming()
except KeyboardInterrupt:
    pass