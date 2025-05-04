'''
This script simulates sending sensor data to a cloud function in batches.
It generates random hub IDs and correct Atlas Scientific device addresses, and sends sensor readings to the specified Cloud Function URL.

Usage:
python simulate_devices_batch.py 1000 50
'''

import asyncio
import random
import string
import aiohttp
import sys
from datetime import datetime

# Your deployed ingest cloud function
CLOUD_FUNCTION_URL = "https://us-central1-interviewing-457222.cloudfunctions.net/ingest_data_publisher"

BATCH_INTERVAL_SECONDS = 5

# Mapping sensor names to realistic Atlas device addresses
SENSOR_DEVICE_ADDRESS_MAP = {
    "ph": "99",
    "do": "97",
    "atemp": "102",
    "wtemp": "102",
    "co2": "104",
    "hum": "101"
}

# Mapping sensor names to their correct simulation ranges
SENSOR_VALUE_RANGES = {
    "ph": (0.0, 14.0),
    "do": (0.0, 2000.0),
    "atemp": (32.0, 110.0),
    "wtemp": (32.0, 110.0),
    "hum": (0.0, 100.0),
    "co2": (400.0, 5000.0)  # Typical CO2 range indoors
}

def generate_hub_id(length=20):
    """Generate a random hub ID."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def generate_sensor_name():
    """Randomly choose a sensor name."""
    return random.choice(list(SENSOR_DEVICE_ADDRESS_MAP.keys()))

def generate_sensor_value(sensor_name):
    """Generate a realistic sensor value based on sensor type."""
    min_val, max_val = SENSOR_VALUE_RANGES[sensor_name]
    return round(random.uniform(min_val, max_val), 2)

async def send_single_payload(session, hub_id, sensor_name, device_addr):
    """Send a single sensor reading."""
    payload = {
        "hub_id": hub_id,
        "sensor_name": sensor_name,
        "device_addr": device_addr,
        "sensor_val": generate_sensor_value(sensor_name),
        "datetime": str(datetime.utcnow()),
        "sensor_id": f"{hub_id}_{device_addr}",
        "collection_type": "sensor_data"
    }
    
    try:
        async with session.post(CLOUD_FUNCTION_URL, json=payload) as resp:
            status = resp.status
            text = await resp.text()
            print(f"[{hub_id}] Status: {status} | Sensor: {sensor_name} | Addr: {device_addr} | Value: {payload['sensor_val']} | Response: {text}")
    except Exception as e:
        print(f"[{hub_id}] Error: {e}")

async def send_batches(total_devices, batch_size):
    """Send devices in batches."""
    #hub_ids = [generate_hub_id() for _ in range(total_devices)]

    hub_ids = ['Xy12Ab34Cd56Ef78Gh90', 'Jk34Lm56No78Pq90Rs12'] * (total_devices // 2)
    random.shuffle(hub_ids)


    async with aiohttp.ClientSession() as session:
        for i in range(0, total_devices, batch_size):
            batch_hubs = hub_ids[i:i+batch_size]

            tasks = []
            for hub in batch_hubs:
                sensor_name = generate_sensor_name()
                device_addr = SENSOR_DEVICE_ADDRESS_MAP[sensor_name]
                tasks.append(send_single_payload(session, hub, sensor_name, device_addr))

            await asyncio.gather(*tasks)

            print(f"Batch {i // batch_size + 1}: Sent {len(tasks)} devices.")
            await asyncio.sleep(BATCH_INTERVAL_SECONDS)

def main():
    if len(sys.argv) != 3:
        print("Usage: python simulate_devices_batch.py TOTAL_DEVICES BATCH_SIZE")
        sys.exit(1)
    
    total_devices = int(sys.argv[1])
    batch_size = int(sys.argv[2])

    print(f"Simulating {total_devices} devices in batches of {batch_size} every {BATCH_INTERVAL_SECONDS} seconds...")
    asyncio.run(send_batches(total_devices, batch_size))

if __name__ == "__main__":
    main()
