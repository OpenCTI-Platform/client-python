from pathlib import Path
from typing import Any, Dict
import yaml
from pydantic import BaseSettings, Field


class ConnectorBaseSettings(BaseSettings):
    class Config:
        @classmethod
        def customise_sources(
            cls,
            init_settings,
            env_settings,
            file_secret_settings,
        ):
            return (
                init_settings,
                yml_config_setting,
                # json_config_setting,
                env_settings,
                file_secret_settings,
            )


class ConnectorBaseConfig(ConnectorBaseSettings):
    url: str = Field(env="opencti_url")
    token: str = Field(env="opencti_token")
    ssl_verify: bool = Field(env="opencti_ssl_verify", default=True)
    json_logging: bool = Field(env="opencti_json_logging", default=False)
    broker: str = Field(env="opencti_broker", default="pika")

    id: str = Field(env="connector_id")
    name: str = Field(env="connector_name")
    confidence_level: int = Field(env="connector_confidence_level", default=100)
    # scope: list[str] = Field(env="connector_scope")
    scope: str | None = Field(env="connector_scope")
    auto: bool = Field(env="connector_auto", default=False)
    type: str = Field(env="connector_type")
    contextual_only: bool = Field(env="connector_only_contextual", default=False)
    log_level: str = Field(env="connector_log_level", default="INFO")
    run_and_terminate: bool = Field(env="connector_run_and_terminate", default=False)
    validate_before_import: bool = Field(
        env="connector_validate_before_import", default=False
    )


class ExternalImportConfig(ConnectorBaseConfig):
    interval: int = Field(env="connector_interval", default=60)


class StreamInputSetting(ConnectorBaseConfig):
    live_stream_id: str = Field(env="connector_live_stream_id")
    live_stream_listen_delete: str = Field(env="connector_live_stream_listen_delete")
    live_stream_no_dependencies: str = Field(
        env="connector_live_stream_no_dependencies"
    )
    live_stream_with_inferences: str = Field(
        env="connector_live_stream_with_inferences"
    )


class ConnectorConfig(ConnectorBaseSettings):
    class Config:
        env_prefix = "app_"


def yml_config_setting(settings: BaseSettings) -> Dict[str, Any]:
    encoding = settings.__config__.env_file_encoding
    path = Path("config.yml")
    content = {}
    if path.exists():
        with open(path, "r", encoding=encoding) as f:
            content = yaml.safe_load(f)
    return content
