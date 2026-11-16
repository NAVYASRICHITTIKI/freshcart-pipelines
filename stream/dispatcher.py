
import argparse, json, os, random, time, uuid
from datetime import datetime, timezone
import pika

URL = os.environ.get("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/%2F")  # keep real URLs out of Git
EXCHANGE = "rapido-dispatch"
ZONES = {"bangalore": ["koramangala", "indiranagar", "whitefield"],
         "chennai": ["tnagar", "whitefield"]}
TYPES = ["ride", "food"]

ap = argparse.ArgumentParser()
ap.add_argument("--interval", type=float, default=2.0)
ap.add_argument("--duration", type=float, default=120.0)
ap.add_argument("--bad-every", type=int, default=0, help="every Nth message omits 'zone' (0 = never)")
args = ap.parse_args()

conn = pika.BlockingConnection(pika.URLParameters(URL))
ch = conn.channel()
ch.exchange_declare(exchange=EXCHANGE, exchange_type="topic")

start, n = time.time(), 0
while time.time() - start < args.duration:
    n += 1
    city = random.choice(list(ZONES))
    zone = random.choice(ZONES[city])
    typ = random.choice(TYPES)
    key = f"{city}.{zone}.{typ}"
    msg = {"id": uuid.uuid4().hex[:8], "city": city, "zone": zone, "type": typ,
           "ts": datetime.now(timezone.utc).isoformat()}
    bad = args.bad_every and n % args.bad_every == 0
    if bad:
        del msg["zone"]          # the routing key still has a zone, the body does not
    ch.basic_publish(exchange=EXCHANGE, routing_key=key, body=json.dumps(msg),
                     properties=pika.BasicProperties(content_type="application/json"))
    print(f"#{n} published key={key} id={msg['id']}{' (BAD: no zone)' if bad else ''}", flush=True)
    time.sleep(args.interval)
conn.close()