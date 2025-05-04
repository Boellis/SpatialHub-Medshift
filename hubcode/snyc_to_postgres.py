import os
import sqlite3
import logging
import time
from datetime import datetime
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/pi/Medshift/spatialhub-service-account.json"

from google.cloud import pubsub_v1
import json

# === CONFIG ===
PROJECT_ID = "interviewing-457222"
INGEST_TOPIC = "spatialhub-ingest"
DB_FILE = "database1.db"
LOG_FILE = "sync_log.txt"
MAX_BATCH_SIZE = 25
SYNC_INTERVAL = 30  # Seconds between syncs
HUB_ID = "Xy12Ab34Cd56Ef78Gh90"

# === Logging ===
def configure_logging():
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format='%(asctime)s: %(levelname)s: %(message)s'
    )

# === SQLite Handling ===
def get_unsynced_rows(limit=MAX_BATCH_SIZE):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT rowid, * FROM sensor_data1 WHERE synced = 0 ORDER BY timestamp ASC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return rows

def mark_rows_as_synced(row_ids):
    if not row_ids:
        return
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    q_marks = ",".join(["?"] * len(row_ids))
    c.execute(f"UPDATE sensor_data1 SET synced = 1 WHERE rowid IN ({q_marks})", row_ids)
    conn.commit()
    conn.close()

# === Pub/Sub Publishing ===
def publish_one_by_one(rows):
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(PROJECT_ID, INGEST_TOPIC)
    synced_ids = []
    for row in rows:
        payload = {
            "hub_id": HUB_ID,
            "sensor_id": str(HUB_ID) + "_" + str(int(row[2])),
            "sensor_name": 'ph',#row[1],
            "device_addr": row[2],
            "sensor_val": row[3],
            "datetime": row[4],
            "collection_type": "sensor_data"
        }
        try:
            print(f"Publishing: {payload}")
            encoded = json.dumps(payload).encode("utf-8")
            future = publisher.publish(topic_path, encoded)
            future.result()
            logging.info(f"Published row ID {row[0]} to Pub/Sub.")
            synced_ids.append(row[0])
        except Exception as e:
            logging.error(f"Failed to publish row ID {row[0]}: {e}")

    mark_rows_as_synced(synced_ids)

# === Main Loop ===
if __name__ == "__main__":
    configure_logging()
    logging.info("Starting continuous single-row sync...")

    while True:
        rows = get_unsynced_rows()
        if rows:
            publish_one_by_one(rows)
        else:
            logging.info("No new rows to sync.")
        time.sleep(SYNC_INTERVAL)
        print("ran sync")
