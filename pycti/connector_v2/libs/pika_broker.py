import base64
import json
import threading
from typing import Dict, Callable, List

import pika
from pika import spec
from pika.adapters.blocking_connection import BlockingChannel
from pika.exceptions import UnroutableError, NackError

from pycti import OpenCTIApiClient
from pycti.connector_v2.libs.messaging.messaging_queue import MessagingQueue
from pycti.connector_v2.libs.connector_utils import create_ssl_context, get_logger


class PikaBroker(MessagingQueue):
    """Main class for the ListenQueue used in OpenCTIConnectorHelper

    :param helper: instance of a `OpenCTIConnectorHelper` class
    :type helper: OpenCTIConnectorHelper
    :param connector_config: dict containing client config
    :type connector_config: Dict
    :param callback: callback function to process queue
    :type callback: callable
    """

    def __init__(
        self,
        connector_config: Dict,
        connector_id: str,
        applicant_id: str,
        api: OpenCTIApiClient,
    ) -> None:
        threading.Thread.__init__(self)
        self.pika_connection = None

        self.channel = None

        self.connector_id = connector_id
        self.applicant_id = applicant_id
        self.api = api

        self.host = connector_config["connection"]["host"]
        self.use_ssl = connector_config["connection"]["use_ssl"]
        self.port = connector_config["connection"]["port"]
        self.user = connector_config["connection"]["user"]
        self.password = connector_config["connection"]["pass"]
        self.queue_name = connector_config["listen"]
        self.connector_config = connector_config

        self.exit_event = threading.Event()
        self.thread = None
        self.logger = get_logger("pika_broker")

        self.callback_function = None

    def stop(self):
        self.exit_event.set()
        if self.thread:
            self.thread.join()

    def listen(self, callback_function: Callable) -> None:
        while not self.exit_event.is_set():
            try:
                # Connect the broker
                self.pika_connection = self._get_pika_blocking_connection()
                self.channel = self.pika_connection.channel()
                assert self.channel is not None
                # TODO add self.callback_function = callback_function as func arguments instead of global variable!!
                self.callback_function = callback_function
                self.channel.basic_consume(
                    queue=self.queue_name, on_message_callback=self._process_message
                )
                self.channel.start_consuming()
            except Exception as e:
                self.logger.error(str(e), exc_info=True)

    def send(
        self, work_id: str, bundles: List, entities_types: List, update: bool = False
    ):
        pika_connection = self._get_pika_blocking_connection()
        channel = pika_connection.channel()

        for sequence, bundle_item in enumerate(bundles, start=1):
            self._send_single_message(
                channel,
                bundle_item,
                work_id=work_id,
                entities_types=entities_types,
                sequence=sequence,
                update=update,
            )
        channel.close()
        return bundles

    def _get_pika_blocking_connection(self) -> pika.BlockingConnection:
        pika_credentials = pika.PlainCredentials(self.user, self.password)

        pika_parameters = pika.ConnectionParameters(
            host=self.host,
            port=self.port,
            virtual_host="/",
            credentials=pika_credentials,
            ssl_options=pika.SSLOptions(create_ssl_context(), self.host)
            if self.use_ssl
            else None,
        )
        return pika.BlockingConnection(pika_parameters)

    def _send_single_message(
        self,
        channel: BlockingChannel,
        item: str,
        work_id: str = None,
        sequence: int = 0,
        update: bool = False,
        entities_types: List = None,
    ) -> None:
        """send a STIX2 bundle to RabbitMQ to be consumed by workers

        :param channel: RabbitMQ channel
        :type channel: callable
        :param item: valid stix2 bundle
        :type item:
        :param entities_types: list of entity types, defaults to None
        :type entities_types: list, optional
        :param update: whether to update data in the database, defaults to False
        :type update: bool, optional
        """
        if entities_types is None:
            entities_types = []

        # Prepare the message
        # if self.current_work_id is None:
        #    raise ValueError('The job id must be specified')
        message = {
            "applicant_id": self.applicant_id,
            "action_sequence": sequence,
            "entities_types": entities_types,
            "content": base64.b64encode(item.encode("utf-8")).decode("utf-8"),
            "update": update,
        }
        if work_id is not None:
            message["work_id"] = work_id

        # Send the message
        try:
            routing_key = f"push_routing_{self.connector_id}"
            channel.basic_publish(
                exchange=self.connector_config["push_exchange"],
                routing_key=routing_key,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                ),
            )
            self.logger.info("Bundle has been sent")
        except (UnroutableError, NackError) as e:
            self.logger.error("Unable to send bundle, retry...%s", e)
            self._send_single_message(
                channel, item, work_id, sequence, update, entities_types
            )
        except Exception as e:
            self.logger.error("Unable to send bundle, retry...%s", e)
            self._send_single_message(
                channel, item, work_id, sequence, update, entities_types
            )

    ###  functions for further messaging handling
    def _process_message(
        self,
        channel: BlockingChannel,
        method: spec.Basic.Deliver,
        properties: spec.BasicProperties,
        body: bytes,
    ) -> None:
        """process a message from the rabbit queue

        :param channel: channel instance
        :type channel: callable
        :param method: message methods
        :type method: callable
        :param properties: unused
        :type properties: str
        :param body: message body (data)
        :type body: str or bytes or bytearray
        """

        json_data = json.loads(body)
        self.thread = threading.Thread(target=self._data_handler, args=[json_data])
        self.thread.start()
        while self.thread.is_alive():  # Loop while the thread is processing
            assert self.pika_connection is not None
            self.pika_connection.sleep(1.0)
        self.logger.info(
            f"Message (delivery_tag={method.delivery_tag}) processed, thread terminated"
        )
        channel.basic_ack(delivery_tag=method.delivery_tag)

    def _data_handler(self, json_data) -> None:
        # Set the API headers
        work_id = json_data["internal"]["work_id"]
        applicant_id = json_data["internal"]["applicant_id"]
        self.work_id = work_id
        if applicant_id is not None:
            self.applicant_id = applicant_id
            self.api.set_applicant_id_header(applicant_id)
        # Execute the callback
        try:
            self.api.work.to_received(
                work_id, "Connector ready to process the operation"
            )
            message = self.callback_function(json_data["event"])
            self.api.work.to_processed(work_id, message)
        except Exception as e:  # pylint: disable=broad-except
            self.logger.exception("Error in message processing, reporting error to API")
            try:
                self.api.work.to_processed(work_id, str(e), True)
            except:  # pylint: disable=bare-except
                self.logger.error("Failing reporting the processing")
