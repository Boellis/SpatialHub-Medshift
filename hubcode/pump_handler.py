import logging
from AtlasI2C import AtlasI2C

def get_devices():
    device = AtlasI2C()
    return [AtlasI2C(address=addr) for addr in device.list_i2c_devices()]
def dose_pump(addr, amount):
    try:
        logging.info(f"Handling dose command for addr {addr} with amount {amount}")
        devices = get_devices()
        cmd = f"D,{amount}"
        for device in devices:
            if device.address == addr:
                device.query_device_data(cmd)
                logging.info(f"Dosed {amount}mL to pump at address {addr}")
                return
        logging.warning(f"No matching pump found at address {addr}")
    except Exception as e:
        logging.error(f"Pump error: {e}")
