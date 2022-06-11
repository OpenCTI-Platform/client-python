import json

from pydantic import BaseModel, Extra

from pycti import OpenCTIApiClient, ConnectorType
from pycti.connector.v2.connectors.connector import Connector
from stix2 import IPv4Address, Bundle

from pycti.connector.v2.libs.orchestrator_schemas import ConnectorCreate, Config

PROCESSING_COUNT: int = 5
MAX_PROCESSING_COUNT: int = 30


class StixWorker(Connector):
    class StixRunConfig(BaseModel):
        token: str

        class Config:
            extra = Extra.forbid

    def __init__(self):
        settings = ConnectorCreate(
            uuid="f005a115-1139-491a-a1e6-7f93971648f3",
            name="StixWorker2",
            type="STIX_IMPORT",
            queue="queue_stix_worker",
            config_schema=self.StixRunConfig,
        )
        super().__init__(settings)

    def run(self, bundle: Bundle, config: StixRunConfig) -> Bundle:
        print("Started stix worker")
        api = OpenCTIApiClient(
            self.environment_config["opencti"], config.token, self.base_config.log_level
        )
        bundel = {
            "type": "bundle",
            "id": "bundle--177c6477-2dee-43d5-b4c9-8b7f3f5ec517",
            "objects": [
                {
                    "type": "indicator",
                    "spec_version": "2.1",
                    "id": "indicator--a862ff86-68d9-42e5-8095-cd80c040e112",
                    "created": "2020-06-24T15:04:40.048932Z",
                    "modified": "2020-06-24T15:04:40.048932Z",
                    "name": "File hash for malware variant",
                    "pattern": "[file:hashes.md5 = 'd41d8cd98f00b204e9800998ecf8427e']",
                    "pattern_type": "stix",
                    "pattern_version": "2.1",
                    "valid_from": "2020-06-24T15:04:40.048932Z",
                },
                {
                    "type": "malware",
                    "spec_version": "2.1",
                    "id": "malware--389c934c-258c-44fb-ae4b-14c6c12270f6",
                    "created": "2020-06-24T14:53:20.156644Z",
                    "modified": "2020-06-24T14:53:20.156644Z",
                    "name": "Poison Ivy",
                    "is_family": False,
                },
                {
                    "type": "relationship",
                    "spec_version": "2.1",
                    "id": "relationship--2f6a8785-e27b-487e-b870-b85a2121502d",
                    "created": "2020-06-24T15:05:18.250605Z",
                    "modified": "2020-06-24T15:05:18.250605Z",
                    "relationship_type": "indicates",
                    "source_ref": "indicator--a862ff86-68d9-42e5-8095-cd80c040e112",
                    "target_ref": "malware--389c934c-258c-44fb-ae4b-14c6c12270f6",
                },
            ],
        }
        api.stix2.import_bundle_from_json(json.dumps(bundel), True)
        return bundle


class TestExternalImport(Connector):
    class TestExternalImportRunConfig(BaseModel):
        ip: str

        class Config:
            extra = Extra.forbid

    def __init__(self):
        settings = ConnectorCreate(
            uuid="f985a12e-2639-498a-b1e6-7f93971648f1",
            name="TextExternalImport",
            type=ConnectorType.EXTERNAL_IMPORT.value,
            queue="queue_test_external_import",
            config_schema=self.TestExternalImportRunConfig,
        )
        super().__init__(settings)

    def run(self, bundle: Bundle, config: TestExternalImportRunConfig) -> Bundle:
        ip = IPv4Address(value=config.ip)
        bundle = Bundle(ip)
        return bundle

    # def run(self, message: str, data: Dict, delivery_tag):
    #     applicant_id = data.get("applicant_id", None)
    #     if applicant_id is None:
    #         raise ValueError("applicant_id empty")
    #     self.api.set_applicant_id_header(applicant_id)
    #     work_id = data.get("work_id", None)
    #     # Execute the import
    #     processing_count = 1
    #     try:
    #         content = message
    #         tmp_types = data.get("entities_types", [])
    #         types = tmp_types if len(tmp_types) > 0 else None
    #         update = data.get("update", False)
    #         # processing_count = self.processing_count
    #         if processing_count == PROCESSING_COUNT:
    #             processing_count = None  # type: ignore
    #
    #         self.api.stix2.import_bundle_from_json(
    #             content, update, types, processing_count
    #         )
    #
    #         if work_id is not None:
    #             self.api.work.report_expectation(work_id, None)
    #         self.processing_count = 0
    #     except Timeout as te:
    #         self.logger.warning(f"A connection timeout occurred: {{ {te} }}")
    #         # Platform is under heavy load: wait for unlock & retry almost indefinitely.
    #         sleep_jitter = round(random.uniform(10, 30), 2)
    #         time.sleep(sleep_jitter)
    #         # TODO initiate rerun!
    #     except RequestException as re:
    #         # https://docs.python-requests.org/en/master/_modules/requests/exceptions/
    #         self.logger.error(f"A connection error occurred: {{ {re} }}")
    #         time.sleep(60)
    #         self.logger.info(
    #             f"Message (delivery_tag={delivery_tag}) NOT acknowledged"
    #         )
    #         # TODO figure out what to do here, Rerun or simple error?
    #         # cb = functools.partial(self.nack_message, channel, delivery_tag)
    #         # connection.add_callback_threadsafe(cb)
    #     # TODO handle exceptions from here opencti-platform/graphql/src/config/error.js
    #
