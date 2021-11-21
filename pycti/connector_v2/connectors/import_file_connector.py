from typing import Dict, Type

from pycti.connector_v2.connectors.connector import (
    Connector,
    ConnectorBaseSettings,
    ApplicationSettings,
)


class ImportFileConnectorSettings(ConnectorBaseSettings):
    type: str = "INTERNAL_IMPORT_FILE"
    # only_contextual: bool = False
    # auto: bool = False


class InternalImportFileConnector(Connector):
    def __init__(self, application_model: Type[ApplicationSettings] = None):
        if application_model is None:
            application_model = ApplicationSettings
        super().__init__(ImportFileConnectorSettings, application_model)

    def run(self) -> None:
        self.start()
        try:
            self.messaging_broker.listen(self._run)
        except Exception as e:
            self.logger.error(e, exec_stack=True)
            # TODO report exception?
        except KeyboardInterrupt:
            self.stop()

    def _run(self, data: Dict) -> str:
        pass
