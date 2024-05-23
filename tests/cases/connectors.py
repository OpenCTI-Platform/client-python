import os
import time
from datetime import datetime
from typing import Dict

import pika.exceptions
import stix2
import yaml

from pycti import (
    Identity,
    Malware,
    OpenCTIApiClient,
    OpenCTIConnectorHelper,
    Vulnerability,
    get_config_variable,
)
from pycti.utils.constants import ContainerTypes, IdentityTypes


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


class ExternalImportConnectorTest:
    @staticmethod
    def case_vulnerability_import() -> Dict:
        return {
            "data": [
                {
                    "type": IdentityTypes.ORGANIZATION.value,
                    "name": "Testing aaaaa",
                    "description": "OpenCTI Test Org",
                    "class": stix2.Identity,
                    "id": Identity.generate_id("Testing aaaaa", "organization"),
                },
                {
                    "type": "Vulnerability",
                    "name": "CVE-1979-1234",
                    "description": "evil evil evil",
                    "class": stix2.Vulnerability,
                    "id": Vulnerability.generate_id("CVE-1979-1234"),
                },
            ],
            "config": "tests/data/external_import_config.yml",
        }


class ExternalImportConnector:
    def __init__(self, config_file_path: str, api_client: OpenCTIApiClient, data: Dict):
        # set OPENCTI settings from fixture
        os.environ["OPENCTI_URL"] = api_client.api_url
        os.environ["OPENCTI_TOKEN"] = api_client.api_token
        os.environ["OPENCTI_SSL_VERIFY"] = str(api_client.ssl_verify)
        os.environ["OPENCTI_JSON_LOGGING"] = "true"
        os.environ["CONNECTOR_EXPOSE_METRICS"] = "true"
        os.environ["CONNECTOR_METRICS_PORT"] = "9096"

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
        return int(self.interval)

    def run(self):
        now = datetime.utcfromtimestamp(time.time())
        now_time = now.strftime("%Y-%m-%d %H:%M:%S")
        friendly_name = f"{self.helper.connect_name} run @ {now_time}"
        work_id = self.helper.api.work.initiate_work(
            self.helper.connect_id, friendly_name
        )

        bundle_objects = []
        for elem in self.data:
            sdo = elem["class"](
                id=elem["id"],
                name=elem["name"],
                description=elem["description"],
            )
            bundle_objects.append(sdo)

        # create stix bundle
        bundle = stix2.Bundle(objects=bundle_objects).serialize()
        # send data
        self.helper.send_stix2_bundle(
            bundle=bundle,
            entities_types=self.helper.connect_scope,
            update=True,
            work_id=work_id,
        )

        message = "Connector successfully run, storing last_run as " + str(now_time)
        self.helper.api.work.to_processed(work_id, message)

        return "Foo"

    def stop(self):
        self.helper.stop()

    def start(self):
        try:
            self.run()
        except pika.exceptions.AMQPConnectionError:
            self.stop()
            raise ValueError(
                "Connector was not able to establish the connection to RabbitMQ"
            )


class InternalEnrichmentConnectorTest:
    @staticmethod
    def case_ipv4_enrichment() -> Dict:
        return {
            "data": {
                "simple_observable_key": "IPv4-Addr.value",
                "simple_observable_value": "198.51.100.3",
                "x_opencti_score": 30,
            },
            "config": "tests/data/internal_enrichment_config.yml",
        }


class InternalEnrichmentConnector:
    def __init__(self, config_file_path: str, api_client: OpenCTIApiClient, data: Dict):
        # set OPENCTI settings from fixture
        os.environ["OPENCTI_URL"] = api_client.api_url
        os.environ["OPENCTI_TOKEN"] = api_client.api_token
        os.environ["OPENCTI_SSL_VERIFY"] = str(api_client.ssl_verify)

        config = (
            yaml.load(open(config_file_path), Loader=yaml.FullLoader)
            if os.path.isfile(config_file_path)
            else {}
        )

        self.helper = OpenCTIConnectorHelper(config)

    def _process_message(self, data: Dict) -> str:
        # set score to 100
        entity_id = data["entity_id"]
        observable = self.helper.api.stix_cyber_observable.read(id=entity_id)

        self.helper.api.stix_cyber_observable.update_field(
            id=observable["standard_id"],
            input={"key": "x_opencti_score", "value": ["100"]},
        )

        # now = datetime.utcfromtimestamp(time.time())
        # now_time = now.strftime("%Y-%m-%d %H:%M:%S")
        # friendly_name = f"{self.helper.connect_name} run @ {now_time}"
        # work_id = self.helper.api.work.initiate_work(
        #     self.helper.connect_id, friendly_name
        # )
        #
        # # set score to 100
        # entity_id = data["entity_id"]
        # observable = self.helper.api.stix_cyber_observable.read(id=entity_id)
        #
        # stix_observable = SimpleObservable(
        #     id=OpenCTIStix2Utils.generate_random_stix_id("x-opencti-simple-observable"),
        #     key="IPv4-Addr.value",
        #     value=observable['value'],
        #     x_opencti_score=100
        # )
        # bundle_objects = [stix_observable]
        # # create stix bundle
        # bundle = Bundle(objects=bundle_objects).serialize()
        # # send data
        # self.helper.send_stix2_bundle(
        #     bundle=bundle,
        #     update=True,
        # )
        #
        # message = "Connector successfully run, storing last_run as " + str(now_time)
        # self.helper.api.work.to_processed(work_id, message)

        return "Finished"

    def stop(self):
        self.helper.stop()

    def start(self):
        try:
            self.helper.listen(self._process_message)
        except pika.exceptions.AMQPConnectionError:
            self.stop()
            raise ValueError(
                "Connector was not able to establish the connection to RabbitMQ"
            )


class InternalImportConnectorTest:
    @staticmethod
    def case_txt_import() -> Dict:
        return {
            "import_file": "tests/data/internal_import_data.txt",
            "config": "tests/data/internal_import_config.yml",
            "observable": {
                "simple_observable_key": "IPv4-Addr.value",
                "simple_observable_value": "198.51.100.3",
                "x_opencti_score": 30,
            },
            "report": {
                "type": ContainerTypes.REPORT.value,
                "name": "The Black Vine Cyberespionage Group",
                "description": "A simple report with an indicator and campaign",
                "published": "2016-01-20T17:00:00.000Z",
                "report_types": ["campaign"],
                # "lang": "en",
                # "object_refs": [self.ipv4["id"], self.domain["id"]],
            },
        }


class InternalImportConnector:
    def __init__(self, config_file_path: str, api_client: OpenCTIApiClient, data: Dict):
        # set OPENCTI settings from fixture
        os.environ["OPENCTI_URL"] = api_client.api_url
        os.environ["OPENCTI_TOKEN"] = api_client.api_token
        os.environ["OPENCTI_SSL_VERIFY"] = str(api_client.ssl_verify)

        config = (
            yaml.load(open(config_file_path), Loader=yaml.FullLoader)
            if os.path.isfile(config_file_path)
            else {}
        )

        self.helper = OpenCTIConnectorHelper(config)
        self.data = data

    def _process_message(self, data: Dict) -> str:
        file_fetch = data["file_fetch"]
        file_uri = self.helper.opencti_url + file_fetch

        # Downloading and saving file to connector
        self.helper.connector_logger.info("Importing the file", {"file_uri": file_uri})

        # observable = SimpleObservable(
        #    id=OpenCTIStix2Utils.generate_random_stix_id("x-opencti-simple-observable"),
        #    key=self.data["simple_observable_key"],
        #    value=self.data["simple_observable_value"],
        # )
        observable = stix2.IPv4Address(
            value=self.data["simple_observable_value"],
        )
        bundle_objects = [observable]
        entity_id = data.get("entity_id", None)
        report = self.helper.api.report.read(id=entity_id)

        report = stix2.Report(
            id=report["standard_id"],
            name=report["name"],
            description=report["description"],
            published=self.helper.api.stix2.format_date(report["published"]),
            report_types=report["report_types"],
            object_refs=bundle_objects,
        )

        bundle_objects.append(report)
        # create stix bundle
        bundle = stix2.Bundle(objects=bundle_objects).serialize()
        # send data
        self.helper.send_stix2_bundle(bundle=bundle)
        return "foo"

    def stop(self):
        self.helper.stop()

    def start(self):
        try:
            self.helper.listen(self._process_message)
        except pika.exceptions.AMQPConnectionError:
            self.stop()
            raise ValueError(
                "Connector was not able to establish the connection to RabbitMQ"
            )


class ConnectorRegisteringMarkingsTest:
    @staticmethod
    def case_no_markings() -> Dict:
        """Adding no markings works as expected"""
        author_id = Identity.generate_id("Anyhack", "organization")

        return {
            "add_markings": False,
            "add_markings_author": True,
            "data": [
                {
                    "connector_marking_expected": False,
                    "connector_marking_should_be_default": False,
                    "author_marking_expected": False,
                    "author_marking_should_be_default": False,
                    "expected_author_name": "",
                    "class": stix2.Identity,
                    "standard_id": author_id,
                    "name": "Anyhack",
                    "description": "Hack the world!",
                },
                {
                    "connector_marking_expected": False,
                    "connector_marking_should_be_default": False,
                    "author_marking_expected": False,
                    "author_marking_should_be_default": False,
                    "expected_author_name": "",
                    "class": stix2.Malware,
                    "standard_id": Malware.generate_id("HackersSoftware"),
                    "name": "HackersSoftware",
                    "description": "A very malicious software.",
                    "type": "malware",
                    "is_family": False,
                    "created_by_ref": author_id,
                },
            ],
            "config": "tests/data/external_import_with_markings_config.yml",
        }

    @staticmethod
    def case_valid_only_connector() -> Dict:
        """Adding markings for the connector works as expected"""
        return {
            "add_markings": True,
            "add_markings_author": False,
            "data": [
                {
                    "connector_marking_expected": True,
                    "connector_marking_should_be_default": False,
                    "author_marking_expected": False,
                    "author_marking_should_be_default": False,
                    "expected_author_name": "",
                    "class": stix2.Malware,
                    "standard_id": Malware.generate_id("Malwyo"),
                    "name": "Malwyo",
                    "description": "A very malicious malware.",
                    "type": "malware",
                    "is_family": False,
                    "created_by_ref": None,
                },
            ],
            "config": "tests/data/external_import_with_markings_config.yml",
        }

    @staticmethod
    def case_valid_connector_and_author() -> Dict:
        """Adding markings for the connector and authors works as expected"""
        author_1_name = "SuperHackers"
        author_2_name = "ChildrenOfTheScript"
        author_1_id = Identity.generate_id(author_1_name, "organization")
        author_2_id = Identity.generate_id(author_2_name, "organization")

        return {
            "add_markings": True,
            "add_markings_author": True,
            "data": [
                {
                    "connector_marking_expected": True,
                    "connector_marking_should_be_default": False,
                    "author_marking_expected": True,
                    "author_marking_should_be_default": True,
                    "expected_author_name": "",
                    "class": stix2.Identity,
                    "standard_id": author_1_id,
                    "name": author_1_name,
                    "description": "Hack the world!",
                },
                {
                    "connector_marking_expected": True,
                    "connector_marking_should_be_default": False,
                    "author_marking_expected": True,
                    "author_marking_should_be_default": True,
                    "expected_author_name": "",
                    "class": stix2.Identity,
                    "standard_id": author_2_id,
                    "name": author_2_name,
                    "description": "We use ChatGPT.",
                },
                {
                    "connector_marking_expected": True,
                    "connector_marking_should_be_default": False,
                    "author_marking_expected": True,
                    "author_marking_should_be_default": False,
                    "expected_author_name": author_1_name,
                    "class": stix2.Malware,
                    "standard_id": Malware.generate_id("MaliciousMalware"),
                    "name": "MaliciousMalware",
                    "description": "A very malicious malware.",
                    "type": "malware",
                    "is_family": False,
                    "created_by_ref": author_1_id,
                },
                {
                    "connector_marking_expected": True,
                    "connector_marking_should_be_default": False,
                    "author_marking_expected": True,
                    "author_marking_should_be_default": False,
                    "expected_author_name": author_1_name,
                    "class": stix2.Malware,
                    "standard_id": Malware.generate_id("SuperMaliciousMalware"),
                    "name": "SuperMaliciousMalware",
                    "description": "A super malicious malware.",
                    "type": "malware",
                    "is_family": False,
                    "created_by_ref": author_1_id,
                },
                {
                    "connector_marking_expected": True,
                    "connector_marking_should_be_default": False,
                    "author_marking_expected": True,
                    "author_marking_should_be_default": False,
                    "expected_author_name": author_2_name,
                    "class": stix2.Malware,
                    "standard_id": Malware.generate_id("SophisticatedScript"),
                    "name": "SophisticatedScript",
                    "description": "A very sophisticated script.",
                    "type": "malware",
                    "is_family": False,
                    "created_by_ref": author_2_id,
                },
            ],
            "config": "tests/data/external_import_with_markings_config.yml",
        }

    @staticmethod
    def case_default_author() -> Dict:
        """Adding a marking for an author that does not exist uses the default
        marking.
        When no author is specified, a default marking is added.
        """
        return {
            "add_markings": True,
            "add_markings_author": True,
            "data": [
                {
                    "connector_marking_expected": True,
                    "connector_marking_should_be_default": False,
                    "author_marking_expected": True,
                    "author_marking_should_be_default": True,
                    "expected_author_name": "",
                    "class": stix2.Malware,
                    "standard_id": Malware.generate_id("RandomInternetPoC"),
                    "name": "RandomInternetPoC",
                    "description": "Just a PoC that was used maliciously.",
                    "type": "malware",
                    "is_family": False,
                    "created_by_ref": Identity.generate_id(
                        "idontexist", "organization"
                    ),
                },
                {
                    "connector_marking_expected": True,
                    "connector_marking_should_be_default": False,
                    "author_marking_expected": True,
                    "author_marking_should_be_default": True,
                    "expected_author_name": "",
                    "class": stix2.Malware,
                    "standard_id": Malware.generate_id("MalwareBySuperSensitiveGroup"),
                    "name": "MalwareBySuperSensitiveGroup",
                    "description": "Written by skilled engineers.",
                    "type": "malware",
                    "is_family": False,
                    "created_by_ref": None,
                },
            ],
            "config": "tests/data/external_import_with_markings_config.yml",
        }


class ConnectorRegisteringMarkings:
    def __init__(
        self,
        config_file_path: str,
        api_client: OpenCTIApiClient,
        data: Dict,
        random_uuid: str,
        add_marking: bool,
        add_author_marking: bool,
    ):
        # set OPENCTI settings from fixture
        os.environ["OPENCTI_URL"] = api_client.api_url
        os.environ["OPENCTI_TOKEN"] = api_client.api_token
        os.environ["OPENCTI_SSL_VERIFY"] = str(api_client.ssl_verify)
        if add_marking:
            os.environ["CONNECTOR_ADD_MARKINGS"] = "true"
        else:
            os.environ["CONNECTOR_ADD_MARKINGS"] = "false"
        if add_author_marking:
            os.environ["CONNECTOR_ADD_AUTHOR_MARKINGS"] = "true"
        else:
            os.environ["CONNECTOR_ADD_AUTHOR_MARKINGS"] = "false"

        config = (
            yaml.load(open(config_file_path), Loader=yaml.FullLoader)
            if os.path.isfile(config_file_path)
            else {}
        )

        # add randomness to prevent concurrency issues during testing
        config["connector"]["id"] = random_uuid
        config["connector"]["name"] = "_".join(
            [config["connector"]["name"], random_uuid]
        )

        self.helper = OpenCTIConnectorHelper(config)
        self.interval = get_config_variable(
            "INTERVAL", ["test", "interval"], config, True
        )

        self.data = data

    def get_interval(self):
        return int(self.interval)

    def run(self):
        now = datetime.fromtimestamp(time.time())
        now_time = now.strftime("%Y-%m-%d %H:%M:%S")
        friendly_name = f"{self.helper.connect_name} run @ {now_time}"
        work_id = self.helper.api.work.initiate_work(
            self.helper.connect_id, friendly_name
        )

        bundle_objects = []
        for elem in self.data:
            cls = elem["class"]

            match cls:
                case stix2.Malware:
                    sdo = cls(
                        id=elem["standard_id"],
                        name=elem["name"],
                        description=elem["description"],
                        created_by_ref=elem["created_by_ref"],
                        is_family=elem["is_family"],
                    )
                case stix2.Identity:
                    sdo = cls(
                        id=elem["standard_id"],
                        name=elem["name"],
                        description=elem["description"],
                    )
                case _:
                    raise Exception(
                        f"This test implementation does not support this stix2 class, you have to add it: {cls}"
                    )

            bundle_objects.append(sdo)

        # create stix bundle
        bundle = stix2.Bundle(objects=bundle_objects).serialize()
        # send data
        self.helper.send_stix2_bundle(
            bundle=bundle,
            entities_types=self.helper.connect_scope,
            update=True,
            work_id=work_id,
        )

        message = "Connector successfully run, storing last_run as " + str(now_time)
        self.helper.api.work.to_processed(work_id, message)

        return "Foo"

    def stop(self):
        self.helper.stop()

    def start(self):
        try:
            self.run()
        except pika.exceptions.AMQPConnectionError:
            self.stop()
            raise ValueError(
                "Connector was not able to establish the connection to RabbitMQ"
            )
