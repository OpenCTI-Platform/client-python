import datetime
import logging
import queue
import ssl
import threading
import time
from enum import Enum
from queue import Queue
from typing import Any, Dict, List

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
SEPARATOR = "_"


# TODO implement JSON logging format


class ConnectorType(Enum):
    EXTERNAL_IMPORT = "EXTERNAL_IMPORT"  # From remote sources to OpenCTI stix2
    INTERNAL_IMPORT_FILE = (
        "INTERNAL_IMPORT_FILE"  # From OpenCTI file system to OpenCTI stix2
    )
    INTERNAL_ENRICHMENT = "INTERNAL_ENRICHMENT"  # From OpenCTI stix2 to OpenCTI stix2
    INTERNAL_EXPORT_FILE = (
        "INTERNAL_EXPORT_FILE"  # From OpenCTI stix2 to OpenCTI file system
    )
    STREAM = "STREAM"  # Read the stream and do something
    WORKER = "WORKER"


def get_logger(
    name: str, logging_level: str = "INFO", logging_format: str = LOG_FORMAT
) -> Any:
    logger = logging.getLogger(name)
    logger.setLevel(logging_level)

    c_handler = logging.StreamHandler()
    console_formatter = logging.Formatter(logging_format)
    c_handler.setFormatter(console_formatter)

    logger.addHandler(c_handler)

    return logger


def create_ssl_context() -> ssl.SSLContext:
    """Set strong SSL defaults: require TLSv1.2+

    `ssl` uses bitwise operations to specify context `<enum 'Options'>`
    """

    ssl_context_options: List[int] = [
        ssl.OP_NO_COMPRESSION,
        ssl.OP_NO_TICKET,  # pylint: disable=no-member
        ssl.OP_NO_RENEGOTIATION,  # pylint: disable=no-member
        ssl.OP_SINGLE_DH_USE,
        ssl.OP_SINGLE_ECDH_USE,
    ]
    ssl_context = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH)
    ssl_context.options &= ~ssl.OP_ENABLE_MIDDLEBOX_COMPAT  # pylint: disable=no-member
    ssl_context.verify_mode = ssl.CERT_REQUIRED
    ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2

    for option in ssl_context_options:
        ssl_context.options |= option

    return ssl_context


def date_now() -> str:
    """get the current date (UTC)
    :return: current datetime for utc
    :rtype: str
    """
    return (
        datetime.datetime.utcnow()
        .replace(microsecond=0, tzinfo=datetime.timezone.utc)
        .isoformat()
    )


def check_max_tlp(tlp: str, max_tlp: str) -> bool:
    """check the allowed TLP levels for a TLP string

    :param tlp: string for TLP level to check
    :type tlp: str
    :param max_tlp: the highest allowed TLP level
    :type max_tlp: str
    :return: TLP level in allowed TLPs
    :rtype: bool
    """

    allowed_tlps: Dict[str, List[str]] = {
        "TLP:RED": [
            "TLP:WHITE",
            "TLP:CLEAR",
            "TLP:GREEN",
            "TLP:AMBER",
            "TLP:AMBER+STRICT",
            "TLP:RED",
        ],
        "TLP:AMBER+STRICT": [
            "TLP:WHITE",
            "TLP:CLEAR",
            "TLP:GREEN",
            "TLP:AMBER",
            "TLP:AMBER+STRICT",
        ],
        "TLP:AMBER": ["TLP:WHITE", "TLP:CLEAR", "TLP:GREEN", "TLP:AMBER"],
        "TLP:GREEN": ["TLP:WHITE", "TLP:CLEAR", "TLP:GREEN"],
        "TLP:WHITE": ["TLP:WHITE", "TLP:CLEAR"],
        "TLP:CLEAR": ["TLP:WHITE", "TLP:CLEAR"],
    }

    return tlp in allowed_tlps[max_tlp]


class StreamAlive(threading.Thread):
    def __init__(
        self, q: Queue, log_level: str, connector_stop_event: threading.Event
    ) -> None:
        threading.Thread.__init__(self)
        self.logger = get_logger("StreamAlive", log_level)
        self.q = q
        self.connector_stop_event = connector_stop_event
        self.exit_event = threading.Event()

    def run(self) -> None:
        self.logger.info("Starting stream alive thread")
        time_since_last_heartbeat = 0
        while not self.exit_event.is_set():
            time.sleep(5)
            try:
                self.q.get(block=False)
                time_since_last_heartbeat = 0
            except queue.Empty:
                time_since_last_heartbeat = time_since_last_heartbeat + 5
                if time_since_last_heartbeat > 45:
                    self.logger.error(
                        "Time since last heartbeat exceeded 45s, stopping the connector"
                    )
                    self.stop()
                    self.connector_stop_event.set()

    def stop(self) -> None:
        logging.info("Preparing for clean shutdown")
        self.exit_event.set()


def merge_dict(dictionary: dict) -> dict:
    result = {}
    for key, val in dictionary.items():
        if isinstance(val, dict):
            tmp_result = merge_dict(val)
            for t_key, t_val in tmp_result.items():
                result[f"{key}{SEPARATOR}{t_key}"] = t_val
        else:
            result[f"{key}"] = val

    return result
