from pycti.connector.connector_types.connector_settings import ConnectorBaseSettings


def test_yaml_settings():
    config = ConnectorBaseSettings()

    assert config.token == "7f175acc-811b-465d-8a07-47ef11b92392"
    assert config.url == "https://opencti.io"
    assert config.broker == "default"
    assert config.ssl_verify is False
    assert config.json_logging is False
    assert config.log_level == "DEBUG"
