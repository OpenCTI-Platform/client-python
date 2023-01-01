from pycti.connector.connector_types.worker import Worker
from pycti.test_plugin.test_class import ConnectorTest


class WorkerTest(ConnectorTest):
    connector = Worker

    def _setup(self, monkeypatch):
        monkeypatch.setenv("opencti_broker", "pika")
        monkeypatch.setenv("opencti_ssl_verify", "False")

    def shutdown(self):
        self.connector_instance.stop()
        self.t1.join()
