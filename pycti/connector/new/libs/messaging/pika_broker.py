import json
import threading
from typing import Dict, Callable
import pika
from pika.exceptions import StreamLostError

from pycti.connector.new.libs.orchestrator_schemas import RunContainer


class PikaBroker(threading.Thread):
    def __init__(self, broker_settings: Dict, callback_function: Callable) -> None:
        threading.Thread.__init__(self)
        self.callback_function = callback_function
        self.broker_settings = broker_settings
        pika_credentials = pika.PlainCredentials(
            broker_settings["user"], broker_settings["password"]
        )

        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=broker_settings["host"],
                port=broker_settings["port"],
                virtual_host="/",
                credentials=pika_credentials,
            )
        )

    def listen(self, queue):
        self.channel = self.connection.channel()

        self.channel.queue_declare(queue=queue, durable=True)
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=queue, on_message_callback=self.callback, auto_ack=True
        )
        try:
            self.channel.start_consuming()
            # self.channel.close()
        except StreamLostError as e:
            # No idea why pika throws this exception when closing
            pass

    def callback(self, ch, method, properties, body):
        print(" [x] %r" % body.decode())
        # TODO get task
        # for connector:
        #   get task message
        # for stix worker:
        #   get stix bundle and ingest
        try:
            run_container = RunContainer(**json.loads(body.decode()))
        except Exception as e:
            print(f"Received unknown container format {e}")
            return
            # Print log
            # accept delivery?
            # send message to orchestrator that it failed? (but for which config?)

        try:
            return_container: RunContainer = self.callback_function(run_container)
        except Exception as e:
            # TODO handle exceptions (in case something went wrong)
            # then no container is passed and the job as well as the run
            # are set to failed result
            # do something??...
            print(f"errorr: {str(e)}")
            return
        # manual ack is necessary, when rerunning connector
        # or should we only rerun entire workflow runs?
        ch.basic_ack(delivery_tag=method.delivery_tag)

        self.send(return_container)

    def send(self, run_container: RunContainer):
        job = run_container.jobs[0]

        channel = self.connection.channel()
        channel.queue_declare(queue=job.queue, durable=True)
        channel.basic_publish(
            exchange="",
            routing_key=job.queue,
            body=run_container.json(),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ),
        )

    def stop(self):
        if self.channel:
            try:
                self.channel.stop_consuming()
                # self.channel.close()
            except StreamLostError as e:
                # No idea why pika throws this exception when closing
                pass
        else:
            self.connection.close()
