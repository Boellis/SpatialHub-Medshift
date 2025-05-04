import os
import sqlite3
import logging
from datetime import datetime
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/pi/Medshift/spatialhub-service-account.json"

from google.cloud import pubsub_v1
import json
from pump_handler import dose_pump  # fan out to pump handler

# === CONFIG ===
HUB_ID = "Xy12Ab34Cd56Ef78Gh90"
PROJECT_ID = "interviewing-457222"
INGEST_TOPIC = "spatialhub-ingest"
COMMAND_SUBSCRIPTION = "command-sub"
DB_FILE = "database1.db"
LOG_FILE = "hubLog.txt"
PUMP1_ADDR = 103

# === Ensure files exist ===
def safe_init():
    if not os.path.exists(DB_FILE):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS sensor_data1 (
            sensor_name TEXT, device_addr REAL, sensor_val REAL, timestamp TEXT)''')
        conn.commit()
        conn.close()
    if not os.path.exists(LOG_FILE):
        open(LOG_FILE, "a").close()

# === Logging ===
def configure_logging(logfile=LOG_FILE):
    safe_init()
    logging.basicConfig(
        filename=logfile,
        level=logging.DEBUG,
        format='%(asctime)s: %(levelname)s: %(message)s'
    )

# === Pub/Sub ===
publisher = pubsub_v1.PublisherClient()
subscriber = pubsub_v1.SubscriberClient()
ingest_topic_path = publisher.topic_path(PROJECT_ID, INGEST_TOPIC)
subscription_path = subscriber.subscription_path(PROJECT_ID, COMMAND_SUBSCRIPTION)

def publish_to_ingest(payload: dict):
    try:
        encoded = json.dumps(payload).encode("utf-8")
        future = publisher.publish(ingest_topic_path, encoded)
        logging.info(f"Published to Pub/Sub ingest: {payload}")
        future.result()
    except Exception as e:
        logging.error(f"Failed to publish to ingest: {e}")

# === SQLite ===
def get_latest_sensor_reading(addr):
    safe_init()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "SELECT * FROM sensor_data1 WHERE device_addr = ? ORDER BY timestamp DESC LIMIT 1",
        (addr,)
    )
    row = c.fetchone()
    conn.close()
    return row

# === Callback ===
def callback(message):
    try:
        raw = message.data.decode("utf-8").strip()
        command_data = json.loads(raw)  

        logging.info(f"Received command: {command_data}")

        hub_id = command_data.get("hub_id")
        cmd = command_data['command']
        print(cmd)
        if cmd.startswith("D,"):
            amt = int(cmd.split(",")[1])
            #print("yessir type shit")
            dose_pump(PUMP1_ADDR, amt)

        else:
            logging.info("Command ignored (no action taken)")

        message.ack()
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse command JSON: {e}")
        message.nack()
    except Exception as e:
        logging.error(f"Command failed: {e}")
        message.nack()

# === Entry Point ===
if __name__ == "__main__":
    configure_logging()
    future = subscriber.subscribe(subscription_path, callback=callback)
    print(f"Listening for messages on {subscription_path}...")
    logging.info(f"Listening on {subscription_path}...")
    try:
        future.result()
    except KeyboardInterrupt:
        future.cancel()
        logging.info("Shutting down basic_funcs subscriber.")
