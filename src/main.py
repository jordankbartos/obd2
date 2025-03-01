import obd
import logging

logging.basicConfig(level="DEBUG")

logger = logging.getLogger(__name__)

# Attempt to connect to OBD-II adapter
logging.debug("Connecting to OBD-II device...")
connection = obd.OBD("/dev/ttyUSB0")  # Change if your port is different

if connection.is_connected():
    logging.debug("✅ Successfully connected to OBD-II!")
    
    # Try reading vehicle temperature
    temp = connection.query(obd.commands.COOLANT_TEMP)
    
    if temp is not None and temp.value is not None:
        logging.debug(f"🚗 Vehicle Temp: {temp.value} km/h")
    else:
        logging.debug("⚠ Unable to read temperature. Is the engine running?")
else:
    logging.debug("❌ Failed to connect to OBD-II. Check your adapter and port.")

# Close connection
connection.close()
