# coding: utf-8

from pycti import OpenCTIApiClient

# Variables
api_url = "http://localhost:4000"
api_token = "d434ce02-e58e-4cac-8b4c-42bf16748e84"

# OpenCTI initialization
opencti_api_client = OpenCTIApiClient(api_url, api_token)

# File to import
file_to_import = "./tests/data/DATA-TEST-STIX2_v2.json"


class TestLoader:
    def test_should_import_bundle_from_file(self):
        # Import the bundle
        imported = opencti_api_client.stix2.import_bundle_from_file(file_to_import, True)
        assert len(imported) == 69

