from typing import Type

import time
from datetime import datetime

from requests import HTTPError

from pycti import ConnectorType
from pycti.connector_v2.connectors.connector import (
    Connector,
    ConnectorBaseSettings,
    ApplicationSettings,
)


class ExternalImportConnectorSettings(ConnectorBaseSettings):
    type: str = ConnectorType.EXTERNAL_IMPORT
    interval: int = 3
    external_identity: str  # STIX ID of identity


class ExternalImportConnector(Connector):
    def __init__(self, application_model: Type[ApplicationSettings] = None):
        if application_model is None:
            application_model = ApplicationSettings
        super().__init__(ExternalImportConnectorSettings, application_model)

    def run(self, run_once: bool = False) -> None:
        self.start()

        identity = self.api.identity.read(id=self.config.connector.external_identity)
        if identity:
            self.logger.error(
                f"External Identity {self.config.connector.external_identity} could not be found. Make "
                f"sure the opencti connector is importing an updated identity list",
                exc_info=True,
            )
            self.stop()

        # TODO add while loop
        work_id = None
        try:
            timestamp = int(time.time())
            now = datetime.utcfromtimestamp(timestamp)
            # TODO get last run and interval
            # check if difference is bigger than interval

            work_id = self.api.work.initiate_work(
                self.config.connector.id,
                f"{self.config.connector.name} run @ {now.strftime('%Y-%m-%d %H:%M:%S')}",
            )
            self.logger.debug(f"Registerd work with ID {work_id}")
            if work_id is None:
                raise ValueError(f"No work ID was registered {work_id}")

            self._run()

            self.set_state({"last_run": timestamp})
            message = (
                "Last_run stored, next run in: "
                + str(round(self.get_interval() * 60 * 60 * 24, 2))
                + " days"
            )
            self.api.work.to_processed(work_id, message)
        except HTTPError as e:
            self.logger.error(e, exc_info=True)
            self.api.work.report_expectation(work_id, str(e))
            # TODO maybe start again?
            # self.stop()
        except AssertionError as e:
            self.logger.error(e, exc_info=True)
            self.api.work.report_expectation(work_id, str(e))
            self.stop()
        except Exception as e:
            self.logger.error(e, exc_info=True)
            self.api.work.report_expectation(work_id, str(e))
            self.stop()
        except KeyboardInterrupt:
            self.stop()
        # except MixinException  as e:
        #   print error
        #   cancel work
        # something else:
        #   try again
        # handle

    def _run(self) -> None:
        pass

    def get_interval(self) -> int:
        return self.config.connector.interval
