# coding: utf-8

from pycti import OpenCTIApiClient

# Variables
api_url = "http://opencti:4000"
api_token = "bfa014e0-e02e-4aa6-a42b-603b19dcf159"

# OpenCTI initialization
opencti_api_client = OpenCTIApiClient(api_url, api_token)

opencti_api_client.stix_cyber_observable.create(
    observableData={"type": "SSH-Key", "fingerprint_sha256": "sha256_test"}
)

observable_sshkey = opencti_api_client.stix_cyber_observable.read(
    filters={
        "mode": "and",
        "filters": [{"key": "fingerprint_sha256", "values": ["sha256_test"]}],
        "filterGroups": [],
    }
)

opencti_api_client.stix_cyber_observable.delete(id=observable_sshkey.get("id"))
