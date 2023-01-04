from pycti.connector.connector_types.connector_settings import ConnectorBaseSettings


def test_yaml_settings():
    config = ConnectorBaseSettings("tests/integration/support_data/test_config.yml")

    assert config.token == "7f175acc-811b-465d-8a07-47ef11b92392"
    assert config.url == "https://opencti.io"
    assert config.broker == "default"
    assert config.ssl_verify is False
    assert config.json_logging is False
    assert config.log_level == "DEBUG"


def test_env_settings(monkeypatch):
    monkeypatch.setenv("opencti_token", "7f175acc-811b-465d-8a07-47ef11b92392")
    monkeypatch.setenv("opencti_url", "https://opencti.io")
    monkeypatch.setenv("opencti_broker", "default")
    monkeypatch.setenv("opencti_ssl_verify", "False")
    monkeypatch.setenv("connector_json_logging", "False")
    monkeypatch.setenv("connector_log_level", "DEBUG")

    config = ConnectorBaseSettings()

    assert config.token == "7f175acc-811b-465d-8a07-47ef11b92392"
    assert config.url == "https://opencti.io"
    assert config.broker == "default"
    assert config.ssl_verify is False
    assert config.json_logging is False
    assert config.log_level == "DEBUG"
