from typing import Type

from pycti import ConnectorType
from pycti.connector_v2.connectors.connector import (
    Connector,
    ConnectorBaseSettings,
    ApplicationSettings,
)


class StreamConnectorSettings(ConnectorBaseSettings):
    type: str = ConnectorType.STREAM
    live_stream_id: str


class StreamConnector(Connector):
    def __init__(self, application_model: Type[ApplicationSettings] = None):
        if application_model is None:
            application_model = ApplicationSettings
        super().__init__(StreamConnectorSettings, application_model)
