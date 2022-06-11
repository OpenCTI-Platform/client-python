# coding: utf-8

import json


# Commented out since OpenCTI requires at least 100 indicators
# for this test to work
#
# def test_get_100_indicators_with_pagination(api_client):
#     # Get 100 Indicators using the pagination
#     custom_attributes = """
#         id
#         revoked
#         created
#     """
#
#     final_indicators = []
#     data = api_client.indicator.list(
#         first=50, customAttributes=custom_attributes, withPagination=True
#     )
#     final_indicators = final_indicators + data["entities"]
#
#     assert len(final_indicators) == 50
#
#     after = data["pagination"]["endCursor"]
#     data = api_client.indicator.list(
#         first=50,
#         after=after,
#         customAttributes=custom_attributes,
#         withPagination=True,
#     )
#     final_indicators = final_indicators + data["entities"]
#
#     assert len(final_indicators) == 100


def test_indicator_stix_marshall(api_client):
    with open("tests/e2e/support_data/indicator_stix.json", "r") as content_file:
        content = content_file.read()

    json_data = json.loads(content)

    for indic in json_data["objects"]:
        imported_indicator = api_client.indicator.import_from_stix2(
            stixObject=indic, update=True
        )
        assert imported_indicator is not None


def test_import_stix_2_0(api_client):
    api_client.stix2.import_bundle_from_file("tests/e2e/support_data/stix_2_0.json")

    observable = api_client.stix_cyber_observable.read(
        filters={
            "key": "name",
            "values": ["C:\\Users\\<USER>\\AppData\\Local\\libcqppj\\cmd.exe"],
        }
    )
    assert observable is not None
    assert "id" in observable
