from typing import Dict, Type

from pycti import ConnectorType
from pycti.connector_v2.connectors.connector import (
    Connector,
    ConnectorBaseSettings,
    ApplicationSettings,
)


class EnrichmentConnectorSettings(ConnectorBaseSettings):
    type: str = ConnectorType.INTERNAL_ENRICHMENT
    only_contextual: bool = False
    auto: bool = False


class EnrichmentConnector(Connector):
    def __init__(self, application_model: Type[ApplicationSettings] = None):
        if application_model is None:
            application_model = ApplicationSettings
        super().__init__(EnrichmentConnectorSettings, application_model)

    def run(self) -> None:
        self.start()
        try:
            self.messaging_broker.listen(self._run)
        except Exception as e:
            self.logger.error(e, exec_stack=True)
        except KeyboardInterrupt:
            self.stop()

    def _run(self, data: Dict) -> None:
        pass
