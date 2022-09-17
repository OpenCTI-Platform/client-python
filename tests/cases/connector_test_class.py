import threading
from typing import Type, Optional
from stix2 import Bundle

from pycti import OpenCTIApiClient
from pycti.connector.new.connector import Connector


class ConnectorTest:
    connector = None

    def __init__(self, api_client: OpenCTIApiClient):
        self.api_client = api_client

    def setup(self, monkeypatch):
        pass

    def run(self):
        print("Running it")
        self.connector_instance = self.connector()
        self.t1 = threading.Thread(target=self.connector_instance.start)
        self.t1.start()

    def teardown(self):
        pass

    # returns work_id if returned
    def initiate(self) -> Optional[str]:
        pass

    def shutdown(self):
        self.connector_instance.stop()
        self.t1.join()
        self.api_client.connector.unregister(self.connector_instance.base_config.id)

    def get_connector(self) -> Type[Connector]:
        pass

    def verify(self, bundle: Bundle):
        pass
