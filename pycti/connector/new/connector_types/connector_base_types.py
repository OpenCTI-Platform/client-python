import os
import threading
from datetime import datetime
from typing import Dict, Union, List, Any
import schedule


import time
from pydantic import BaseModel
from stix2 import Bundle

from pycti.connector.new.connector import Connector
from pycti.connector.new.connector_types.connector_settings import ExternalImportConfig, WorkerConfig
from pycti.connector.new.libs.connector_utils import ConnectorType
from pycti.connector.new.libs.opencti_schema import InternalFileInputMessage, FileEvent, WorkerMessage, \
    InternalEnrichmentMessage


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


class ExternalInputConnector(Connector):
    connector_type = ConnectorType.EXTERNAL_IMPORT.value
    # scope = "external import"  # scope isn't needed for EIs
    settings = ExternalImportConfig

    def __init__(self):
        super().__init__()
        self.interval = self.base_config.interval
        self.event = schedule.every(self.interval).seconds.do(self.issue_call)
        self.stop_event = threading.Event()

        if self.base_config.run_and_terminate:
            self.stop_event.set()
            # Make start() finish right away

    def start(self) -> None:
        # Call it for the first time directly
        self.issue_call()

        # Then start loop which spawns the first process
        # in self.interval seconds
        while not self.stop_event.is_set():
            schedule.run_pending()
            time.sleep(1)

    def issue_call(self):
        # Get the current timestamp and check
        self.get_last_run()

        timestamp = int(time.time())
        now = datetime.utcfromtimestamp(timestamp)
        friendly_name = "Connector run @ " + now.strftime("%Y-%m-%d %H:%M:%S")
        work_id = self.api.work.initiate_work(
            self.base_config.id, friendly_name
        )

        try:
            run_message, bundles = self.run(self.connector_config)
        except Exception as e:
            self.logger.error(f"Running Error: {str(e)}")
            # TODO run again one time
            return

        # Store the current timestamp as a last run
        self.logger.info(
            "Connector successfully run, storing last_run as " + str(timestamp)
        )
        message = (
                "Last_run stored, next run in: "
                + str(round(self.interval / 60 / 60 / 24, 2))
                + " days"
        )
        self.api.work.to_processed(work_id, message)
        self.logger.info(f"Sending message: {message}")

        for bundle in bundles:
            self._send_bundle(bundle, work_id, None, self.base_config.scope)

        self.set_last_run()

    def _stop(self):
        self.stop_event.set()
        self.logger.info("Ending")

    def run(self, config: BaseModel) -> (str, List[Bundle]):
        pass



# class StreamInputConnector(ListenStreamConnector):
#     settings = StreamInputSetting
#
#     def __init__(self):
#         super().__init__()


class InternalEnrichmentConnector(ListenConnector):
    connector_type = ConnectorType.INTERNAL_ENRICHMENT.value

    def __init__(self):
        super().__init__()

    def process_broker_message(self, message: Dict) -> None:
        try:
            msg = InternalEnrichmentMessage(**message)
        except Exception as e:
            self.logger.error(
                f"Received non-InternalEnrichmentInput packet ({message}) -> {e} "
            )
            return

        self.get_last_run()
        self.api.work.to_received(
            msg.internal.work_id, "Connector ready to process the operation"
        )
        self.logger.info(f"Received work {msg.internal.work_id}")
        try:
            run_msg, bundles = self.run(
                msg.event.entity_id,
                self.connector_config,
            )
            self.api.work.to_processed(msg.internal.work_id, run_msg)

        except ValueError as e:  # pydantic validation error
            self.logger.exception("Error in message processing, reporting error to API")
            try:
                self.api.work.to_processed(msg.internal.work_id, str(e), True)
            except:  # pylint: disable=bare-except
                self.logger.error("Failing reporting the processing")

            return

        for bundle in bundles:
            self._send_bundle(bundle, msg.internal.work_id, msg.internal.applicant_id)

        self.set_last_run()

    def run(
            self, entity_id: str, config: BaseModel
    ) -> (str, List[Bundle]):
        pass


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

        self.get_last_run()

        self.api.work.to_received(
            msg.internal.work_id, "Connector ready to process the operation"
        )
        self.logger.info(f"Received work {msg.internal.work_id}")
        file_path = self._download_import_file(msg)
        try:
            run_msg, bundles = self.run(
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

            return

        file_name = file_path.split('/')[-1]

        for bundle in bundles:
            self._send_bundle(bundle, msg.internal.work_id, msg.internal.applicant_id)

        self.set_last_run()

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
    ) -> (str, List[Bundle]):
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
