import os
from typing import Dict
import yaml
from stix2 import Vulnerability, Bundle

from pycti import OpenCTIConnectorHelper, get_config_variable, OpenCTIApiClient


class SimpleConnectorTest:
    @staticmethod
    def case_simple_connector() -> Dict:
        return {
            "connector_id": "a5d89a53-3101-4ebe-8915-bd0480f488b3",
            "connector_name": "TestConnector",
            "connector_type": "EXTERNAL_IMPORT",
            "scope": "vulnerability",
            "auto": True,
            "only_contextual": False,
        }


class ExternalEnrichmentConnector:
    def __init__(self, config_file_path: str, api_client: OpenCTIApiClient, data: Dict):
        os.environ["OPENCTI_URL"] = api_client.api_url
        os.environ["OPENCTI_TOKEN"] = api_client.api_token
        os.environ["OPENCTI_SSL_VERIFY"] = str(api_client.ssl_verify)

        config = (
            yaml.load(open(config_file_path), Loader=yaml.FullLoader)
            if os.path.isfile(config_file_path)
            else {}
        )

        self.helper = OpenCTIConnectorHelper(config)
        self.interval = get_config_variable(
            "INTERVAL", ["test", "interval"], config, True
        )

        self.data = data

    def get_interval(self):
        return int(self.interval) * 60 * 60 * 24

    def run(self):
        self.helper.api.identity.create(**self.data["api"])

        vulnerability = Vulnerability(
            name=self.data["bundle"]["name"],
            description=self.data["bundle"]["description"],
        )
        bundle_objects = [vulnerability]
        # create stix bundle
        bundle = Bundle(objects=bundle_objects).serialize()

        # send data
        out = self.helper.send_stix2_bundle(bundle=bundle)
        print(out)

        self.stop()

    def stop(self):
        self.helper.stop()


# class InternalExportConnector:
