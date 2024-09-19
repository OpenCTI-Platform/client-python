import json
import uuid

from stix2 import Report

from pycti.utils.opencti_stix2_splitter import OpenCTIStix2Splitter


def test_split_bundle():
    stix_splitter = OpenCTIStix2Splitter()
    with open("./tests/data/enterprise-attack.json") as file:
        content = file.read()
    expectations, bundles = stix_splitter.split_bundle_with_expectations(content)
    assert expectations == 7016


def test_split_mono_bundle():
    stix_splitter = OpenCTIStix2Splitter()
    with open("./tests/data/mono-bundle.json") as file:
        content = file.read()
    expectations, bundles = stix_splitter.split_bundle_with_expectations(content)
    assert expectations == 1


def test_split_capec_bundle():
    stix_splitter = OpenCTIStix2Splitter()
    with open("./tests/data/mitre_att_capec.json") as file:
        content = file.read()
    expectations, bundles = stix_splitter.split_bundle_with_expectations(content)
    assert expectations == 2610


def test_split_cyclic_bundle():
    stix_splitter = OpenCTIStix2Splitter()
    with open("./tests/data/cyclic-bundle.json") as file:
        content = file.read()
    expectations, bundles = stix_splitter.split_bundle_with_expectations(content)
    assert expectations == 6
    for bundle in bundles:
        json_bundle = json.loads(bundle)
        object_json = json_bundle["objects"][0]
        if object_json["id"] == "report--a445d22a-db0c-4b5d-9ec8-e9ad0b6dbdd7":
            assert (
                len(object_json["external_references"]) == 1
            )  # References are duplicated
            assert len(object_json["object_refs"]) == 2  # Cleaned cyclic refs
            assert len(object_json["object_marking_refs"]) == 1
            assert (
                object_json["object_marking_refs"][0]
                == "marking-definition--78ca4366-f5b8-4764-83f7-34ce38198e27"
            )


def test_create_bundle():
    stix_splitter = OpenCTIStix2Splitter()
    report = Report(
        report_types=["campaign"],
        name="Bad Cybercrime",
        published="2016-04-06T20:03:00.000Z",
        object_refs=["indicator--a740531e-63ff-4e49-a9e1-a0a3eed0e3e7"],
    ).serialize()
    observables = [report]

    bundle = stix_splitter.stix2_create_bundle(
        "bundle--" + str(uuid.uuid4()),
        0,
        observables,
        use_json=False,
        event_version=None,
    )

    for key in ["type", "id", "spec_version", "objects", "x_opencti_seq"]:
        assert key in bundle
    assert len(bundle.keys()) == 5

    bundle = stix_splitter.stix2_create_bundle(
        "bundle--" + str(uuid.uuid4()), 0, observables, use_json=False, event_version=1
    )
    for key in [
        "type",
        "id",
        "spec_version",
        "objects",
        "x_opencti_event_version",
        "x_opencti_seq",
    ]:
        assert key in bundle
    assert len(bundle.keys()) == 6
