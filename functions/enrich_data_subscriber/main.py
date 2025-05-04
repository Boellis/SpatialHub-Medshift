
import os
import psycopg2
import json
import base64
from datetime import datetime

DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')

def enrich_data(event, context):
    pubsub_message = event['data']
    decoded = base64.b64decode(pubsub_message).decode('utf-8')
    print(f"Raw decoded payload: {decoded}")

    try:
        payload = json.loads(decoded)
    except Exception as e:
        print(f"JSON decode failed: {e}")
        return

    # Always treat as a list for uniform handling
    payloads = payload if isinstance(payload, list) else [payload]

    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        cursor = conn.cursor()
        print("Your payloads:", payloads)
        for item in payloads:
            print("Your item:", item)
            print(f"Processing item: {item}")
            hub_id = item.get('hub_id')
            sensor_name = item.get('sensor_name')
            device_addr = item.get('device_addr')
            sensor_val = item.get('sensor_val')
            datetime_val = item.get('datetime')
            sensor_id = item.get('sensor_id')
            collection_type = item.get('collection_type')

            cursor.execute("""
                INSERT INTO raw_sensor_data (hub_id, sensor_name, device_addr, sensor_val, datetime, sensor_id)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (hub_id, sensor_name, device_addr, sensor_val, datetime_val, sensor_id))

            # Enrich if hub is provisioned
            cursor.execute("SELECT location, owner, workers FROM hub_config WHERE hub_id = %s", (hub_id,))
            result = cursor.fetchone()
            if result:
                location, owner, workers = result
                cursor.execute("""
                    INSERT INTO enriched_sensor_data (hub_id, sensor_name, device_addr, sensor_val, datetime, sensor_id, location, owner, workers)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (hub_id, sensor_name, device_addr, sensor_val, datetime_val, sensor_id, location, owner, workers))
    except Exception as e:
        print(f"Error processing record: {e}")
        

    conn.commit()
    cursor.close()
    conn.close()
