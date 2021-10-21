import base64
import json
import logging
import threading
from typing import Dict

import pika
from pika.exceptions import UnroutableError, NackError

from pycti.connector_v2.libs.messaging.messaging_queue import MessagingQueue
from pycti.connector_v2.libs.utils.connector_utils import create_ssl_context


class PikaListenQueue(MessagingQueue):
    """Main class for the ListenQueue used in OpenCTIConnectorHelper

    :param helper: instance of a `OpenCTIConnectorHelper` class
    :type helper: OpenCTIConnectorHelper
    :param config: dict containing client config
    :type config: Dict
    :param callback: callback function to process queue
    :type callback: callable
    """

    def __init__(self, helper, config: Dict, callback) -> None:
        threading.Thread.__init__(self)
        self.pika_credentials = None
        self.pika_parameters = None
        self.pika_connection = None
        self.channel = None
        self.helper = helper
        self.callback = callback
        self.host = config["connection"]["host"]
        self.use_ssl = config["connection"]["use_ssl"]
        self.port = config["connection"]["port"]
        self.user = config["connection"]["user"]
        self.password = config["connection"]["pass"]
        self.queue_name = config["listen"]
        self.exit_event = threading.Event()
        self.thread = None

    # noinspection PyUnusedLocal
    def _process_message(self, channel, method, properties, body) -> None:
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
        logging.info(
            "%s",
            (
                f"Message (delivery_tag={method.delivery_tag}) processed"
                ", thread terminated"
            ),
        )
        channel.basic_ack(delivery_tag=method.delivery_tag)

    def _data_handler(self, json_data) -> None:
        # Set the API headers
        work_id = json_data["internal"]["work_id"]
        applicant_id = json_data["internal"]["applicant_id"]
        self.helper.work_id = work_id
        if applicant_id is not None:
            self.helper.applicant_id = applicant_id
            self.helper.api.set_applicant_id_header(applicant_id)
        # Execute the callback
        try:
            self.helper.api.work.to_received(
                work_id, "Connector ready to process the operation"
            )
            message = self.callback(json_data["event"])
            self.helper.api.work.to_processed(work_id, message)
        except Exception as e:  # pylint: disable=broad-except
            logging.exception("Error in message processing, reporting error to API")
            try:
                self.helper.api.work.to_processed(work_id, str(e), True)
            except:  # pylint: disable=bare-except
                logging.error("Failing reporting the processing")

    def run(self) -> None:
        while not self.exit_event.is_set():
            try:
                # Connect the broker
                self.pika_credentials = pika.PlainCredentials(self.user, self.password)
                self.pika_parameters = pika.ConnectionParameters(
                    host=self.host,
                    port=self.port,
                    virtual_host="/",
                    credentials=self.pika_credentials,
                    ssl_options=pika.SSLOptions(create_ssl_context(), self.host)
                    if self.use_ssl
                    else None,
                )
                self.pika_connection = pika.BlockingConnection(self.pika_parameters)
                self.channel = self.pika_connection.channel()
                assert self.channel is not None
                self.channel.basic_consume(
                    queue=self.queue_name, on_message_callback=self._process_message
                )
                self.channel.start_consuming()
            except Exception as e:
                self.helper.log_error(str(e))

    def stop(self):
        self.exit_event.set()
        if self.thread:
            self.thread.join()

    def push(self, msg: Dict, connector_id: str):
        pika_credentials = pika.PlainCredentials(
            self.config["connection"]["user"], self.config["connection"]["pass"]
        )
        pika_parameters = pika.ConnectionParameters(
            host=self.config["connection"]["host"],
            port=self.config["connection"]["port"],
            virtual_host="/",
            credentials=pika_credentials,
            ssl_options=pika.SSLOptions(
                create_ssl_context(), self.config["connection"]["host"]
            )
            if self.config["connection"]["use_ssl"]
            else None,
        )

        pika_connection = pika.BlockingConnection(pika_parameters)
        channel = pika_connection.channel()
        for sequence, bundle in enumerate(bundles, start=1):
            self._send_bundle(
                channel,
                bundle,
                work_id=work_id,
                entities_types=entities_types,
                sequence=sequence,
                update=update,
            )
        channel.close()
        return bundles
        # Send the message

    def send_single_message(self, channel, bundle, **kwargs) -> None:
        """send a STIX2 bundle to RabbitMQ to be consumed by workers

        :param channel: RabbitMQ channel
        :type channel: callable
        :param bundle: valid stix2 bundle
        :type bundle:
        :param entities_types: list of entity types, defaults to None
        :type entities_types: list, optional
        :param update: whether to update data in the database, defaults to False
        :type update: bool, optional
        """
        work_id = kwargs.get("work_id", None)
        sequence = kwargs.get("sequence", 0)
        update = kwargs.get("update", False)
        entities_types = kwargs.get("entities_types", None)

        if entities_types is None:
            entities_types = []

        # Validate the STIX 2 bundle
        # validation = validate_string(bundle)
        # if not validation.is_valid:
        # raise ValueError('The bundle is not a valid STIX2 JSON')

        # Prepare the message
        # if self.current_work_id is None:
        #    raise ValueError('The job id must be specified')
        message = {
            "applicant_id": self.applicant_id,
            "action_sequence": sequence,
            "entities_types": entities_types,
            "content": base64.b64encode(bundle.encode("utf-8")).decode("utf-8"),
            "update": update,
        }
        if work_id is not None:
            message["work_id"] = work_id

        # Send the message
        try:
            self.listen_queue.push(message, self.connector_id)
            logging.info("Bundle has been sent")
        except Exception as e:
            logging.error("Unable to send bundle, retry...%s", e)
            self._send_bundle(channel, bundle, **kwargs)

        try:
            routing_key = f"push_routing_{connector_id}"
            self.channel.basic_publish(
                exchange=self.config["push_exchange"],
                routing_key=routing_key,
                body=json.dumps(msg),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                ),
            )
            logging.info("Bundle has been sent")
        except (UnroutableError, NackError) as e:
            raise Exception(f"Unable to send bundle: {e}")