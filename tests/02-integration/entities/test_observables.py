# coding: utf-8
import json
from unittest.mock import Mock


def test_promote_observable_to_indicator_deprecated(api_client):
    # deprecated [>=6.2 & <6.8]
    obs1 = api_client.stix_cyber_observable.create(
        simple_observable_key="IPv4-Addr.value", simple_observable_value="55.55.55.55"
    )
    observable = api_client.stix_cyber_observable.promote_to_indicator(
        id=obs1.get("id")
    )
    assert observable is not None, "Returned observable is NoneType"
    assert observable.get("id") == obs1.get("id")


def test_certificate_creation_mapping(api_client):
    with open("./tests/data/certificate.json") as file:
        _input, _output = json.loads(file.read()).values()

    api_client.query = Mock(return_value={"data": {"stixCyberObservableAdd": {}}})

    api_client.stix_cyber_observable.create(**_input)
    assert api_client.query.call_args.args[1] == _output
