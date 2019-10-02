# coding: utf-8
import threading

import pika
import logging
import json
import time
import base64
import uuid

import requests
from pika.exceptions import UnroutableError, NackError
from stix2validator import validate_string

from opencti_connector import OpenCTIConnector
from pycti import OpenCTIApiClient


class ListenQueue(threading.Thread):
    def __init__(self, queue_name, channel, callback):
        threading.Thread.__init__(self)
        self.channel = channel
        self.callback = callback
        self.queue_name = queue_name

    def _process_message(self, channel, method, properties, body):
        try:
            self.callback(json.loads(body), channel, method, properties)
            channel.basic_ack(delivery_tag=method.delivery_tag)
        except requests.exceptions.Timeout:
            logging.warning('Error calling the API, prevent message ack')

    def run(self):
        logging.info('Starting consuming listen queue')
        self.channel.basic_consume(queue=self.queue_name, on_message_callback=self._process_message)
        self.channel.start_consuming()


class PingAlive(threading.Thread):
    def __init__(self, connector_id, api):
        threading.Thread.__init__(self)
        self.connector_id = connector_id
        self.api = api

    def ping(self):
        logging.debug('Ping api')
        self.api.ping_connector(self.connector_id)
        time.sleep(10)
        self.ping()

    def run(self):
        logging.info('Starting ping alive thread')
        self.ping()


class OpenCTIConnectorHelper:
    """
        Python API for OpenCTI connector
        :param connector: OpenCTIConnector identifier
        :param api_client: OpenCTIApiClient api
    """
    def __init__(self, connector: OpenCTIConnector, opencti_url: str, opencti_token: str, log_level='info'):
        # Configure logger
        numeric_level = getattr(logging, log_level.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError('Invalid log level: ' + log_level)
        logging.basicConfig(level=numeric_level)

        # Initialize configuration
        self.api = OpenCTIApiClient(opencti_url, opencti_token, log_level)

        # Register the connector in OpenCTI
        connector_configuration = self.api.register_connector(connector)
        self.connector_id = connector_configuration['id']
        self.config = connector_configuration['config']

        # Connect to the broker
        self.pika_connection = pika.BlockingConnection(pika.URLParameters(self.config['uri']))
        self.channel = self.pika_connection.channel()

        # Start ping thread
        self.ping = PingAlive(connector.id, self.api)
        self.ping.start()

        # Initialize caching
        self.cache_index = {}
        self.cache_added = []

    def listen(self, message_callback):
        listen_queue = ListenQueue(self.config['listen'], self.channel, message_callback)
        listen_queue.start()

    def send_stix2_bundle(self, bundle, entities_types=[]):
        bundles = self.split_stix2_bundle(bundle)
        for bundle in bundles:
            self._send_bundle(bundle, entities_types)

    def _send_bundle(self, bundle, entities_types=[]):
        """
            This method send a STIX2 bundle to RabbitMQ to be consumed by workers
            :param bundle: A valid STIX2 bundle
            :param entities_types: Entities types to ingest
        """
        if self.channel is None or not self.channel.is_open:
            self.channel = self.pika_connection.channel()

        # Validate the STIX 2 bundle
        # validation = validate_string(bundle)
        # if not validation.is_valid:
        # raise ValueError('The bundle is not a valid STIX2 JSON:' + bundle)

        # Prepare the message
        message = {
            'entities_types': entities_types,
            'content': base64.b64encode(bundle.encode('utf-8')).decode('utf-8')
        }

        # Send the message
        try:
            self.channel.basic_publish('amqp.worker.exchange', self.connector_id, json.dumps(message))
            logging.info('Bundle has been sent')
        except (UnroutableError, NackError) as e:
            logging.error('Unable to send bundle, retry...', e)
            self._send_bundle(bundle, entities_types)

    def split_stix2_bundle(self, bundle):
        self.cache_index = {}
        self.cache_added = []
        bundle_data = json.loads(bundle)

        # Index all objects by id
        for item in bundle_data['objects']:
            self.cache_index[item['id']] = item

        bundles = []
        # Reports must be handled because of object_refs
        for item in bundle_data['objects']:
            if item['type'] == 'report':
                items_to_send = self.stix2_deduplicate_objects(self.stix2_get_report_objects(item))
                for item_to_send in items_to_send:
                    self.cache_added.append(item_to_send['id'])
                bundles.append(self.stix2_create_bundle(items_to_send))

        # Relationships not added in previous reports
        for item in bundle_data['objects']:
            if item['type'] == 'relationship' and item['id'] not in self.cache_added:
                items_to_send = self.stix2_deduplicate_objects(self.stix2_get_relationship_objects(item))
                for item_to_send in items_to_send:
                    self.cache_added.append(item_to_send['id'])
                bundles.append(self.stix2_create_bundle(items_to_send))

        # Entities not added in previous reports and relationships
        for item in bundle_data['objects']:
            if item['type'] != 'relationship' and item['id'] not in self.cache_added:
                items_to_send = self.stix2_deduplicate_objects(self.stix2_get_entity_objects(item))
                for item_to_send in items_to_send:
                    self.cache_added.append(item_to_send['id'])
                bundles.append(self.stix2_create_bundle(items_to_send))

        return bundles

    def stix2_get_embedded_objects(self, item):
        # Marking definitions
        object_marking_refs = []
        if 'object_marking_refs' in item:
            for object_marking_ref in item['object_marking_refs']:
                if object_marking_ref in self.cache_index:
                    object_marking_refs.append(self.cache_index[object_marking_ref])
        # Created by ref
        created_by_ref = None
        if 'created_by_ref' in item and item['created_by_ref'] in self.cache_index:
            created_by_ref = self.cache_index[item['created_by_ref']]

        return {'object_marking_refs': object_marking_refs, 'created_by_ref': created_by_ref}

    def stix2_get_entity_objects(self, entity):
        items = [entity]
        # Get embedded objects
        embedded_objects = self.stix2_get_embedded_objects(entity)
        # Add created by ref
        if embedded_objects['created_by_ref'] is not None:
            items.append(embedded_objects['created_by_ref'])
        # Add marking definitions
        if len(embedded_objects['object_marking_refs']) > 0:
            items = items + embedded_objects['object_marking_refs']

        return items

    def stix2_get_relationship_objects(self, relationship):
        items = [relationship]
        # Get source ref
        if relationship['source_ref'] in self.cache_index:
            items.append(self.cache_index[relationship['source_ref']])
        else:
            return []

        # Get target ref
        if relationship['target_ref'] in self.cache_index:
            items.append(self.cache_index[relationship['target_ref']])
        else:
            return []

        # Get embedded objects
        embedded_objects = self.stix2_get_embedded_objects(relationship)
        # Add created by ref
        if embedded_objects['created_by_ref'] is not None:
            items.append(embedded_objects['created_by_ref'])
        # Add marking definitions
        if len(embedded_objects['object_marking_refs']) > 0:
            items = items + embedded_objects['object_marking_refs']

        return items

    def stix2_get_report_objects(self, report):
        items = [report]
        # Add all object refs
        for object_ref in report['object_refs']:
            items.append(self.cache_index[object_ref])
        for item in items:
            if item['type'] == 'relationship':
                items = items + self.stix2_get_relationship_objects(item)
            else:
                items = items + self.stix2_get_entity_objects(item)
        return items

    @staticmethod
    def stix2_deduplicate_objects(items):
        ids = []
        final_items = []
        for item in items:
            if item['id'] not in ids:
                final_items.append(item)
                ids.append(item['id'])
        return final_items

    @staticmethod
    def stix2_create_bundle(items):
        bundle = {
            'type': 'bundle',
            'id': 'bundle--' + str(uuid.uuid4()),
            'spec_version': '2.0',
            'objects': items
        }
        return json.dumps(bundle)
