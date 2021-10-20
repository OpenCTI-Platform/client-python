from pathlib import Path
import os

from pycti.connector.opencti_connector_helper import load_config

CONFIG_PATH = Path(__file__).parent.parent.parent.resolve() / "data" / "config_test.yml"


def test_load_no_env():
    """Test the loading of the file without any env variables set."""
    config = load_config(CONFIG_PATH)
    assert config["connector"]["id"] == "ChangeMe"
    # Number should be loaded as int if present in the config file.
    assert config["connectorabc"]["interval_sec"] == 6400
    assert isinstance(config["connectorabc"]["interval_sec"], int)


def test_load_with_env():
    """Test the loading with an environment variable set."""
    envs = {
        "CONNECTOR_ID": "E1C88E69-972E-43C0-B089-47DF906B810A",
        "CONNECTOR_CONFIDENCE_LEVEL": "16",
    }
    os.environ.update(envs)
    config = load_config(CONFIG_PATH)
    assert config["connector"]["id"] == "E1C88E69-972E-43C0-B089-47DF906B810A"
    # Number are always string if loaded from the environment variables.
    assert config["connector"]["confidence_level"] == "16"
    assert isinstance(config["connector"]["confidence_level"], str)
    # Remove the created variables.
    for i in envs:
        os.environ.pop(i)


def test_load_wrong_env():
    """
    Test the loading with an environment variable that does not exist.

    If an environment variable does not exist, it should not influence the loading.
    """
    envs = {"MY_NEW_ENV": "Test", "connector_id": "should not replace"}
    os.environ.update(envs)
    config = load_config(CONFIG_PATH)
    assert config["connector"]["id"] == "ChangeMe"
    assert "MY_NEW_ENV" not in config.keys()
    for i in envs:
        os.environ.pop(i)
