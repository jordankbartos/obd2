from config import (
    COMMANDS,
    CONNECTION_KWARGS,
    OBDII_PORTSTR,
    REFRESH_PERIOD_S,
    WRITER_MODE,
)
from logger_cfg import get_logger
from obd_data import DataManager, get_writer
from utils import get_connection

logger = get_logger(__name__)


if __name__ == "__main__":

    connection = get_connection(OBDII_PORTSTR, **CONNECTION_KWARGS)
    writer = get_writer(WRITER_MODE)
    data_manager = DataManager(connection=connection, commands=COMMANDS, writer=writer)

    try:
        data_manager.run(refresh_period=REFRESH_PERIOD_S)
    except KeyboardInterrupt:
        logger.info("Keyboard Interrupt detected, finalizing Data Collection")
        data_manager.finalize()
    except Exception as err:
        logger.exception(f"Unexpected error occured {err}.")
        logger.info("Attempting to save unsaved data before exiting...")
        try:
            data_manager.finalize()
            logger.info("Successfully finalized data")
        except Exception as err2:
            logger.exception(f"Could not finalize data due to error {err2}.")
    finally:
        logger.info("Shutting down connection")
        connection.stop()
        connection.close()
        logger.info("Connection closed successfully")
