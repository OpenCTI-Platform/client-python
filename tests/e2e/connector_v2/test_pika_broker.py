# @parametrize_with_cases("connector", cases=TestExternalImportConnectors)
import uuid
import pytest
from unittest.mock import MagicMock
import pika
from pycti.connector_v2.libs.pika_broker import PikaBroker


@pytest.mark.connectors
def test_pika_simple_message(rabbit_mq_config, api_client):
    connector_id = str(uuid.uuid4())
    connector_config = \
        {
            'config': {
                'connection': rabbit_mq_config,
                'listen': f"listen_{connector_id}",
                "listen_exchange": "amqp.connector.exchange",
                'push': f"push_{connector_id}",
                "push_exchange": "amqp.worker.exchange",
            },
            'id': connector_id,
            'name': 'TestExternalImportConnector'
        }

    pika_broker = PikaBroker(
        connector_config['config'],
        connector_id,
        "123456",
        api_client)

    pika_credentials = pika.PlainCredentials('SjIHMjmnYyRtuDf', 'EVOCuAGfhOEYmmt')

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host='rabbitmq',
            port=5672,
            credentials=pika_credentials
        )
    )

    pika_broker.send(f"work--{uuid.uuid4()}",
                     ["fpp", "bar"],
                     [],
                     True)

    consumer_channel = connection.channel()

    message_callback = MagicMock(return_value=True)
    queue = consumer_channel.queue_declare(connector_config['config']['push'], exclusive=True).method.queue

    # consumer_channel.queue_bind(
    #     exchange=connector_config['config']['push_exchange'],
    #     routing_key=f"push_routing_{connector_config['config']['push']}",
    #     queue=queue
    # )
    consumer_channel.basic_consume(connector_config['config']['push'], message_callback, auto_ack=True)

    consumer_channel.start_consuming()

    message_callback.assert_called_once()

    consumer_channel.close()
