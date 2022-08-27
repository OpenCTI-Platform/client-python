import os
import sched
import threading
from datetime import datetime
from typing import Dict

import time
from pydantic import BaseModel

from pycti.connector.new.connector import Connector
from pycti.connector.new.connector_types.connector_settings import ExternalImportConfig
from pycti.connector.new.libs.connector_utils import ConnectorType
from pycti.connector.new.libs.opencti_schema import InternalFileInputMessage, FileEvent


class ListenConnector(Connector):
    def __init__(self):
        super().__init__()

    def start(self) -> None:
        self.broker_thread = threading.Thread(
            target=self.broker.listen,
            name="Broker Listen",
            args=[self.broker_config["listen"], self.process_broker_message],
        )

        self.broker_thread.daemon = True
        self.broker_thread.start()

    def process_broker_message(self, message: Dict) -> None:
        pass


class IterativeConnector(Connector):
    scope = ""

    def __init__(self):
        super().__init__()
        self.s = sched.scheduler(time.time, time.sleep)
        self.interval = self.base_config.interval
        self.event = self.s.enter(0, 1, self.issue_call)

    def start(self) -> None:
        self.s.run()

    def issue_call(self):
        try:
            # Get the current timestamp and check
            timestamp = int(time.time())
            current_state = self.get_state()
            if current_state is not None and "last_run" in current_state:
                last_run = current_state["last_run"]
                self.logger.info(
                    "Connector last run: "
                    + datetime.utcfromtimestamp(last_run).strftime("%Y-%m-%d %H:%M:%S")
                )
            else:
                last_run = None
                self.logger.info("Connector has never run")
            # If the last_run is more than interval-1 day
            if last_run is None or (
                (timestamp - last_run)
                > ((int(self.base_config.interval) - 1) * 60 * 60 * 24)
            ):
                timestamp = int(time.time())
                now = datetime.utcfromtimestamp(timestamp)
                friendly_name = "Connector run @ " + now.strftime("%Y-%m-%d %H:%M:%S")
                work_id = self.api.work.initiate_work(
                    self.base_config.id, friendly_name
                )

                run_message = self.run({}, self.connector_config)

                # Store the current timestamp as a last run
                self.logger.info(
                    "Connector successfully run, storing last_run as " + str(timestamp)
                )
                self.set_state({"last_run": timestamp})
                message = (
                    "Last_run stored, next run in: "
                    + str(round(self.interval / 60 / 60 / 24, 2))
                    + " days"
                )
                self.api.work.to_processed(work_id, message)
                self.logger.info(message)
            else:
                new_interval = self.interval - (timestamp - last_run)
                self.logger.info(
                    "Connector will not run, next run in: "
                    + str(round(new_interval / 60 / 60 / 24, 2))
                    + " days"
                )
        except Exception as e:
            self.logger.error(str(e))

        self.event = self.s.enter(self.interval, 1, self.issue_call)

    def _stop(self):
        self.s.cancel(self.event)
        self.logger.info("Ending")


class ExternalInputConnector(IterativeConnector):
    connector_type = ConnectorType.EXTERNAL_IMPORT.value
    scope = "external import"  # scope isn't needed for EIs
    settings = ExternalImportConfig

    def __init__(self):
        super().__init__()


# class StreamInputConnector(ListenStreamConnector):
#     settings = StreamInputSetting
#
#     def __init__(self):
#         super().__init__()


class WorkerConnector(ListenConnector):
    connector_type = ConnectorType.WORKER.value

    def __init__(self):
        super().__init__()


class InternalInputConnector(ListenConnector):
    connector_type = ConnectorType.INTERNAL_ENRICHMENT

    def __init__(self):
        super().__init__()


class InternalFileInputConnector(ListenConnector):
    connector_type = ConnectorType.INTERNAL_IMPORT_FILE.value

    def __init__(self):
        super().__init__()

    def process_broker_message(self, message: Dict) -> None:
        try:
            msg = InternalFileInputMessage(**message)
        except Exception as e:
            self.logger.error(
                f"Received non-InternalFileInput packet ({message}) -> {e} "
            )
            return

        self.api.work.to_received(
            msg.internal.work_id, "Connector ready to process the operation"
        )
        self.logger.info(f"Received work {msg.internal.work_id}")
        try:
            file_path = self._download_import_file(msg)
            run_msg = self.run(
                file_path,
                msg.event.file_mime,
                msg.event.entity_id,
                self.connector_config,
            )
            self.api.work.to_processed(msg.internal.work_id, run_msg)

            os.remove(file_path)

        except ValueError as e:  # pydantic validation error
            self.logger.exception("Error in message processing, reporting error to API")
            try:
                self.api.work.to_processed(msg.internal.work_id, str(e), True)
            except:  # pylint: disable=bare-except
                self.logger.error("Failing reporting the processing")

    def _download_import_file(self, message: InternalFileInputMessage) -> str:
        file_fetch = message.event.file_fetch
        file_uri = f"{self.base_config.url}{message.event.file_fetch}"

        # Downloading and saving file to connector
        self.logger.debug(f"Importing the file {file_uri}")
        file_name = os.path.basename(file_fetch)
        file_content = self.api.fetch_opencti_file(file_uri, True)

        with open(file_name, "wb") as f:
            f.write(file_content)

        return file_name

    def run(
        self, file_path: str, file_mime: str, entity_id: str, config: BaseModel
    ) -> str:
        pass


class InternalExportConnector(ListenConnector):
    connector_type = ConnectorType.INTERNAL_EXPORT_FILE.value

    def __init__(self):
        super().__init__()


#
# class ListenStreamConnector(Connector):
#     def __init__(self):
#         super().__init__()
#
#         self.broker_thread = threading.Thread(
#             target=self.broker.listen_stream,
#             name="Pika Broker Listen",
#             args=[self.config["queue"], self.process_broker_message],
#         )
#
#         self.broker_thread.daemon = True
#         self.broker_thread.start()
#
#     def process_broker_message(self, message: ConnectorMessage) -> None:
#         try:
#             current_state = self.get_state()
#             if current_state is None:
#                 current_state = {
#                     "connectorStartTime": date_now(),
#                     "connectorLastEventId": f"{self.start_timestamp}-0"
#                     if self.start_timestamp is not None
#                     and len(self.start_timestamp) > 0
#                     else "-",
#                 }
#                 self.set_state(current_state)
#
#             # If URL and token are provided, likely consuming a remote stream
#             if self.url is not None and self.token is not None:
#                 # If a live stream ID, appending the URL
#                 if self.base_config.live_stream_id is not None:
#                     live_stream_uri = f"/{self.base_config.live_stream_id}"
#                 elif self.base_config.connect_live_stream_id is not None:
#                     live_stream_uri = f"/{self.base_config.connect_live_stream_id}"
#                 else:
#                     live_stream_uri = ""
#                 # Live stream "from" should be empty if start from the beginning
#                 if (
#                     self.base_config.live_stream_id is not None
#                 ):
#
#                     live_stream_from = (
#                         f"?from={current_state['connectorLastEventId']}"
#                         if "connectorLastEventId" in current_state
#                         and current_state["connectorLastEventId"] != "-"
#                         else "?from=0-0&recover="
#                         + (
#                             current_state["connectorStartTime"]
#                             if self.recover_iso_date is None
#                             else self.recover_iso_date
#                         )
#                     )
#                 # Global stream "from" should be 0 if starting from the beginning
#                 else:
#                     live_stream_from = "?from=" + (
#                         current_state["connectorLastEventId"]
#                         if "connectorLastEventId" in current_state
#                         and current_state["connectorLastEventId"] != "-"
#                         else "0-0"
#                     )
#                 live_stream_url = (
#                     f"{self.url}/stream{live_stream_uri}{live_stream_from}"
#                 )
#                 opencti_ssl_verify = (
#                     self.verify_ssl if self.verify_ssl is not None else True
#                 )
#                 logging.info(
#                     "%s",
#                     (
#                         "Starting listening stream events (URL: "
#                         f"{live_stream_url}, SSL verify: {opencti_ssl_verify}, Listen Delete: {self.listen_delete})"
#                     ),
#                 )
#                 messages = SSEClient(
#                     live_stream_url,
#                     headers={
#                         "authorization": "Bearer " + self.token,
#                         "listen-delete": "false"
#                         if self.listen_delete is False
#                         else "true",
#                         "no-dependencies": "true"
#                         if self.no_dependencies is True
#                         else "false",
#                         "with-inferences": "true"
#                         if self.helper.connect_live_stream_with_inferences is True
#                         else "false",
#                     },
#                     verify=opencti_ssl_verify,
#                 )
#             else:
#                 live_stream_uri = (
#                     f"/{self.helper.connect_live_stream_id}"
#                     if self.helper.connect_live_stream_id is not None
#                     else ""
#                 )
#                 if self.helper.connect_live_stream_id is not None:
#                     live_stream_from = (
#                         f"?from={current_state['connectorLastEventId']}"
#                         if "connectorLastEventId" in current_state
#                         and current_state["connectorLastEventId"] != "-"
#                         else "?from=0-0&recover="
#                         + (
#                             self.helper.date_now_z()
#                             if self.recover_iso_date is None
#                             else self.recover_iso_date
#                         )
#                     )
#                 # Global stream "from" should be 0 if starting from the beginning
#                 else:
#                     live_stream_from = "?from=" + (
#                         current_state["connectorLastEventId"]
#                         if "connectorLastEventId" in current_state
#                         and current_state["connectorLastEventId"] != "-"
#                         else "0-0"
#                     )
#                 live_stream_url = f"{self.helper.opencti_url}/stream{live_stream_uri}{live_stream_from}"
#                 logging.info(
#                     "%s",
#                     (
#                         f"Starting listening stream events (URL: {live_stream_url}"
#                         f", SSL verify: {self.helper.opencti_ssl_verify}, Listen Delete: {self.helper.connect_live_stream_listen_delete}, No Dependencies: {self.helper.connect_live_stream_no_dependencies})"
#                     ),
#                 )
#                 messages = SSEClient(
#                     live_stream_url,
#                     headers={
#                         "authorization": "Bearer " + self.helper.opencti_token,
#                         "listen-delete": "false"
#                         if self.helper.connect_live_stream_listen_delete is False
#                         else "true",
#                         "no-dependencies": "true"
#                         if self.helper.connect_live_stream_no_dependencies is True
#                         else "false",
#                         "with-inferences": "true"
#                         if self.helper.connect_live_stream_with_inferences is True
#                         else "false",
#                     },
#                     verify=self.helper.opencti_ssl_verify,
#                 )
#             # Iter on stream messages
#             for msg in messages:
#                 if self.exit:
#                     break
#                 if msg.event == "heartbeat" or msg.event == "connected":
#                     continue
#                 if msg.event == "sync":
#                     if msg.id is not None:
#                         state = self.helper.get_state()
#                         state["connectorLastEventId"] = str(msg.id)
#                         self.helper.set_state(state)
#                 else:
#                     self.callback(msg)
#                     if msg.id is not None:
#                         state = self.helper.get_state()
#                         state["connectorLastEventId"] = str(msg.id)
#                         self.helper.set_state(state)
#         except:
#             sys.excepthook(*sys.exc_info())
#
#         if message.internal.applicant_id is not None:
#             self.applicant_id = message.internal.applicant_id
#             self.api.set_applicant_id_header(message.internal.applicant_id)
#
#         self.api.work.to_received(
#                 message.internal.work_id, "Connector ready to process the operation"
#         )
#         try:
#
#             run_message, bundle = self.run(message.event, self.connector_config)
#             self.broker.send(bundle)
#             self.api.work.to_processed(message.internal.work_id, run_message)
#
#             # if isinstance(bundle, Bundle):
#             #     bundle = bundle.serialize()
#             # run.bundle = bundle
#         except ValueError as e:  # pydantic validation error
#             self.logger.exception("Error in message processing, reporting error to API")
#             try:
#                 self.api.work.to_processed(message.internal.work_id, str(e), True)
#             except:  # pylint: disable=bare-except
#                 self.logger.error("Failing reporting the processing")
