import obd

from logger_cfg import get_logger

logger = get_logger(__name__)


def get_connection(portstr: str, **kwargs) -> obd.Async:
    """Creates and initializes an obd.Async connection object

    Parameters
    ----------
    portstr : str
        The UNIX device file for the OBDII adapter
    **kwargs
        Additional keyword arguments to be passed to the obd.Async constructor

    Returns
    -------
    obd.Async
        connection object

    Raises
    ------
    RuntimeError if the connection cannot be established
    """
    logger.info("Connecting to OBD-II adapter...")
    connection = obd.Async(portstr, **kwargs)  # Adjust if necessary
    if not connection.is_connected():
        raise RuntimeError(
            "Failed to connect to OBD-II via '{portstr}'. Check your adapter and port."
        )
    logger.debug("Connected to OBD-II Successfully")
    return connection
