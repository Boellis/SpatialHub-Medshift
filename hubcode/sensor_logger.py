import sqlite3
import time
import logging
from datetime import datetime
from AtlasI2C import AtlasI2C
import os

# === Paths and Config ===
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(SCRIPT_DIR, "database1.db")

HUB_ID = "Xy12Ab34Cd56Ef78Gh90"
SENSOR_ADDR = 99

# === Logging Setup ===
def configure_logging():
    logging.basicConfig(
        filename='sensor_log.txt',
        level=logging.DEBUG,
        format='%(asctime)s %(message)s'
    )

# === DB Insert ===
def insert_sensor_data(addr, val):
    print(f"Inserting sensor data: addr={addr}, val={val}")
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS sensor_data1 (
            sensor_name TEXT,
            device_addr REAL,
            sensor_val REAL,
            timestamp TEXT,
            synced INTEGER DEFAULT 0
        )''')
        ts = datetime.now().isoformat()
        # Insert with synced = 0
        c.execute('INSERT INTO sensor_data1 VALUES (?, ?, ?, ?, ?)',
                  ("sensor", addr, val, ts, 0))
        conn.commit()
        conn.close()
        logging.info(f"Saved to DB: addr={addr}, val={val}, ts={ts}")
    except Exception as e:
        logging.error(f"DB insert failed: {e}")

# === Sensor Read ===
def query_sensor(device_list, addr, command="R"):
    for device in device_list:
        if device.address == int(addr):
            try:
                value = device.query_device_data(command)
                for _ in range(3):
                    if not value.startswith("Error"):
                        return float(value)
                    value = device.query_device_data(command)
            except Exception as e:
                logging.error(f"Sensor read failed: {e}")
    return None

# === I2C Detection ===
def get_devices(atlas_obj):
    device = atlas_obj()
    device_list = []
    for addr in device.list_i2c_devices():
        try:
            device.set_i2c_address(addr)
            type_id = device.query("I").split(",")[1]
            name = device.query("name,?").split(",")[1]
            device_list.append(atlas_obj(address=addr, moduletype=type_id, name=name))
        except Exception:
            continue
    return device_list

# === Main Loop ===
if __name__ == "__main__":
    configure_logging()
    device_list = get_devices(AtlasI2C)

    while True:
        val = query_sensor(device_list, SENSOR_ADDR)
        if val is not None:
            logging.info(f"Read sensor: addr={SENSOR_ADDR}, val={val}")
            insert_sensor_data(SENSOR_ADDR, val)
        else:
            logging.warning("Sensor returned None")
        time.sleep(5)
