import time
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

import numpy as np
import obd
import pandas as pd

from logger_cfg import get_logger

logger = get_logger(__name__)


class CmdData:
    def __init__(self, cmd: obd.OBDCommand):
        self._cmd = cmd
        self._measurements = []
        self._timestamps = []

    def append_datum(self, response):
        val = response.value.magnitude if response.value is not None else np.nan
        dt = datetime.now()
        self._measurements.append(val)
        self._timestamps.append(dt)
        logger.debug(f"Got {self._cmd.name} datum: {val} at {dt}")

    def clear(self):
        self._measurements = []
        self._timestamps = []

    def get_measurements(self) -> list[Any]:
        return self._measurements

    def get_timestamps(self) -> list[datetime]:
        return self._timestamps

    def get_name(self) -> str:
        return self._cmd.name


class Writer(ABC):
    @abstractmethod
    def write(self, command_objs: list[CmdData]):
        pass


class PandasParquetWriter(Writer):
    def __init__(self):
        self._write_count = 0
        self._written_files = []

    def write(self, command_objs: list[CmdData]):
        self._write_count += 1
        dfs = [self._get_cmd_data_df(command_obj) for command_obj in command_objs]

        df = self._get_combined_df(dfs)
        file_path = f"obd_log_{self._write_count}.parquet"
        self._write_parquet_file(df, file_path)
        self._clear_command_objs(command_objs)

    def _clear_command_objs(self, command_objs):
        logger.info("Clearing in-memory data stores from command data objects")
        _ = [data_obj.clear() for data_obj in command_objs]

    def _get_cmd_data_df(self, cmd_obj: CmdData):
        name = cmd_obj.get_name()
        measurements = cmd_obj.get_measurements()
        timestamps = cmd_obj.get_timestamps()
        return pd.DataFrame(measurements, columns=[name], index=timestamps)

    def _get_combined_df(self, dfs: list[pd.DataFrame]) -> pd.DataFrame:
        return (
            pd.concat(dfs, axis=1)
            .melt(ignore_index=False, var_name="Metric", value_name="Value")
            .dropna()
        )

    def _write_parquet_file(self, df, file_path: str):
        logger.info(f"Writing data to Parquet at {file_path}")
        df.to_parquet(file_path, engine="fastparquet", index=True)
        self._written_files.append(file_path)


def get_writer(writer_mode):
    if writer_mode == "pandas":
        return PandasParquetWriter()
    else:
        raise ValueError(
            "Invalid writer_mode received: Got: '{writer_mode}'. Valid options are ['pandas']"
        )


class DataManager:
    def __init__(self, connection: obd.Async, commands: list[obd.OBDCommand], writer):
        self._connection = connection
        self._writer = writer
        self._command_objs = []
        for cmd in commands:
            if connection.supports(cmd):
                logger.info(f"Monitoring cmd {cmd}")
                self._add_command(cmd)
            else:
                logger.warning(f"Not monitoring cmd {cmd}, it is not supported")

    def run(self, refresh_period: float):
        logger.info("Starting data collection")
        self._connection.start()
        while True:
            time.sleep(refresh_period)  # Adjust for frequency of data collection
            self._write()

    def _add_command(self, cmd: obd.OBDCommand):
        command_obj = CmdData(cmd=cmd)
        self._command_objs.append(command_obj)
        self._connection.watch(cmd, callback=command_obj.append_datum)

    def _write(self):
        logger.info("Pausing connection")
        with self._connection.paused() as was_running:
            if not was_running:
                raise RuntimeError(
                    "Error encountered in writing, it seems connection was not active."
                )
            self._writer.write(self._command_objs)
        logger.info("Resumed connection")

    def finalize(self):
        logger.error("Don't know how to finalize yet")
