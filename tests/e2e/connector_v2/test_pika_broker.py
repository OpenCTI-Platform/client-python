# # @parametrize_with_cases("connector", cases=TestExternalImportConnectors)
# import uuid
# import pytest
# from unittest.mock import MagicMock
# import pika
# from pycti.connector_v2.libs.pika_broker import PikaBroker
#
#
# class GenericConsumer(object):
#     def __init__(self, channel, consume_queue_name, callback):
#         self.channel = channel
#         self.callback = callback
#
#         self.properties = pika.BasicProperties(
#             delivery_mode=2,  # make message persistent
#         )
#
#         self.channel.queue_declare(queue=consume_queue_name, durable=True)
#
#         self.channel.basic_consume(self.callback,
#                                    queue=consume_queue_name,
#                                    no_ack=False)
#
#         self.channel.start_consuming()
#
#     def callback(self, ch: pika.adapters.blocking_connection.BlockingChannel, method, properties, body):
#         if self.callback(ch, method, properties, body):
#             ch.basic_ack(delivery_tag=method.delivery_tag)
#         else:
#             # failed to handle message
#             pass
#
#     def wait_for_log_contains(self, text, level='info'):
#         timeout = 1
#         max_tries = 5
#         while max_tries is not 0:
#             if any(text in s for s in self.consumer_log_messages[level]):
#                 return True
#
#             import time
#             time.sleep(timeout)
#             max_tries -= 1
#
#         self.fail("Log message was not found %s" % text)
#
#     def test_that_consume_on_valid_message_are_consumed_from_the_queue(
#             self):  # publish a message
#         self.channel.basic_publish(
#             exchange = '',
#             routing_key = self.queue_name,
#             body = "dummymessage"
#     )
#
#         # see that the message is in the queue
#         res = self.create_queue(self.queue_name, True)
#         self.assertEqual(res.method.message_count, 1)
#
#         # accept any message
#         message_callback = MagicMock(return_value=True)
#
#         consumer = BasicConsumer(self.rabbitmq_url,
#         self.queue_name,
#         self.queue_arguments,
#         message_callback
#         )
#         # start consumer
#         consumer.start()
#
#         # wait for the consumer to be ready
#         self.wait_for_log_contains(BasicConsumer.CONSUMER_READY)
#
#         # wait for the consumer to signal that is has consumed a message
#         self.wait_for_log_contains(BasicConsumer.CONSUMER_PROCESSED_MESSAGE)
#
#         # assert that the queue is empty
#         res = self.create_queue(self.queue_name, True)
#         self.assertEqual(res.method.message_count, 0)
#
#         message_callback.assert_called_once()
#
#         # stop the consumer
#         consumer.join()
#
#
#
#
#     @pytest.mark.connectors
# def test_pika_simple_message(rabbit_mq_config, api_client):
#     connector_id = str(uuid.uuid4())
#     connector_config = {
#         "config": {
#             "connection": rabbit_mq_config,
#             "listen": f"listen_{connector_id}",
#             "listen_exchange": "amqp.connector.exchange",
#             "push": f"push_{connector_id}",
#             "push_exchange": "amqp.worker.exchange",
#         },
#         "id": connector_id,
#         "name": "TestExternalImportConnector",
#     }
#
#     pika_broker = PikaBroker(
#         connector_config["config"], connector_id, "123456", api_client
#     )
#
#     pika_credentials = pika.PlainCredentials("SjIHMjmnYyRtuDf", "EVOCuAGfhOEYmmt")
#
#     connection = pika.BlockingConnection(
#         pika.ConnectionParameters(
#             host="rabbitmq", port=5672, credentials=pika_credentials
#         )
#     )
#     consumer_channel = connection.channel()
#
#     message_callback = MagicMock(return_value=True)
#     queue_name = f"push_{connector_id}"
#     queue = consumer_channel.queue_declare(
#         queue_name
#     )
#
#
#
#
#     try:
#         pika_broker.send(f"work--{uuid.uuid4()}", ["fpp", "bar"], [], True)
#     except KeyboardInterrupt as e:
#         print(e)
#         return
#
#     consumer_channel.basic_consume(
#         queue=queue.method.queue, on_message_callback=message_callback, auto_ack=True
#     )
#     consumer_channel.start_consuming()
#
#     # consumer_channel.queue_bind(
#     #     exchange=connector_config['config']['push_exchange'],
#     #     routing_key=f"push_routing_{connector_config['config']['push']}",
#     #     queue=queue
#     # )
#
#
#     message_callback.assert_called_once()
#
#     consumer_channel.close()
