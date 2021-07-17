import os
import yaml
from pycti import OpenCTIConnector, OpenCTIConnectorHelper


class TestConnector:
    def test_register_simple_connector(self, api_connector, simple_connector):
        connector = OpenCTIConnector(**simple_connector.data())
        api_connector.register(connector)
        test_connector = ""
        registered_connectors = api_connector.list()
        for registered_connector in registered_connectors:
            if registered_connector["id"] == connector.to_input()["input"]["id"]:
                test_connector = registered_connector["id"]
                break

        assert (
            test_connector == simple_connector.data()["connector_id"]
        ), f"No registered connector with id '{simple_connector.data()['connector_id']}' found"

        # TODO deregister connector

    def test_register_basic_connector(self, api_connector, api_client):
        # set OPENCTI settings from fixture
        os.environ["OPENCTI_URL"] = api_client.api_url
        os.environ["OPENCTI_TOKEN"] = api_client.api_token
        os.environ["OPENCTI_SSL_VERIFY"] = str(api_client.ssl_verify)

        config_file_path = "tests/data/connector_config.yml"
        config = (
            yaml.load(open(config_file_path), Loader=yaml.SafeLoader)
            if os.path.isfile(config_file_path)
            else {}
        )
        connector_helper = OpenCTIConnectorHelper(config)
        config_connector_id = config["connector"]["id"]
        connector_helper_id = connector_helper.get_connector().to_input()["input"]["id"]

        assert (
            config_connector_id == connector_helper_id
        ), f"Connector IDs don't match {config_connector_id} vs {connector_helper_id}!"

        connector_helper.stop()
