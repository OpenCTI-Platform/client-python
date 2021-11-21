from typing import Type, Dict

from pycti import ConnectorType
from pycti.connector_v2.connectors.connector import (
    Connector,
    ApplicationSettings,
    ConnectorBaseSettings,
)


class ExportConnectorSettings(ConnectorBaseSettings):
    type: str = ConnectorType.INTERNAL_EXPORT_FILE


class ExportConnector(Connector):
    def __init__(self, application_model: Type[ApplicationSettings] = None):
        if application_model is None:
            application_model = ApplicationSettings
        super().__init__(ExportConnectorSettings, application_model)

    def run(self) -> None:
        self.start()
        try:
            self.messaging_broker.listen(self._run)
        except Exception as e:
            self.logger.error(e, exec_stack=True)
        except KeyboardInterrupt:
            self.stop()

    def _run(self, data: Dict) -> str:
        pass
