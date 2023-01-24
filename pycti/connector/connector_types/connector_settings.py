from pathlib import Path
from typing import Any, Dict

import yaml
from pydantic import BaseSettings, Extra, Field
from pydantic.env_settings import EnvSettingsSource

from pycti.connector.libs.connector_utils import merge_dict


class ConnectorBaseSettingConfig(BaseSettings):
    class Config:
        env_file_encoding = "utf-8"
        extra = Extra.ignore

        @classmethod
        def customise_sources(
            cls,
            init_settings,
            env_settings,
            file_secret_settings,
        ):
            return (
                init_settings,
                YamlSettingsSource(env_settings).__call__,
                env_settings,
                file_secret_settings,
            )


class YamlSettingsSource:
    # A BaseSettings hack to get the path declared in the constructor
    # for running the test cases
    __slots__ = ("env_settings",)

    def __init__(self, env_settings: EnvSettingsSource):
        self.env_settings = env_settings

    def __call__(self, settings: BaseSettings) -> Dict[str, Any]:
        encoding = settings.__config__.env_file_encoding

        if self.env_settings.env_file:
            paths = [Path(self.env_settings.env_file)]
        else:
            paths = [Path("config.yml"), Path("../config.yml")]
        content = {}
        for path in paths:
            if path.exists():
                with open(path, "r", encoding=encoding) as f:
                    content = yaml.safe_load(f)
                    break

        content = merge_dict(content)
        return content

    def __repr__(self) -> str:
        return f"YamlSettingsSource(yaml_path={self.env_settings.env_file!r})"


class ConnectorConfig(ConnectorBaseSettingConfig):
    class Config:
        env_prefix = "app_"
        extra = Extra.ignore


class ConnectorBaseSettings(ConnectorBaseSettingConfig):
    url: str = Field(env="opencti_url", alias="opencti_url")
    token: str = Field(env="opencti_token", alias="opencti_token")
    ssl_verify: bool = Field(
        env="opencti_ssl_verify", alias="opencti_ssl_verify", default=True
    )
    json_logging: bool = Field(
        env="connector_json_logging", alias="connector_json_logging", default=False
    )
    broker: str = Field(env="opencti_broker", alias="opencti_broker", default="pika")
    log_level: str = Field(
        env="connector_log_level", alias="connector_log_level", default="INFO"
    )


class ConnectorBaseConfig(ConnectorBaseSettings):
    id: str = Field(env="connector_id", alias="connector_id")
    name: str = Field(env="connector_name", alias="connector_name")
    testing: bool = Field(
        env="connector_testing", alias="connector_testing", default=False
    )
    confidence_level: int = Field(
        env="connector_confidence_level",
        alias="connector_confidence_level",
        default=100,
    )
    # scope: list[str] = Field(env="connector_scope")
    scope: str = Field(env="connector_scope", alias="connector_scope")
    auto: bool = Field(env="connector_auto", alias="connector_auto", default=False)
    # deprecated field, as there is no use in manually defining the connector type anymore
    connector_type: str = Field(
        env="connector_type",
        deprecated=True,
        description="No need to define the connector type anymore",
        default=None,
    )
    # Type is hardcoded in the connectors
    type: str
    contextual_only: bool = Field(
        env="connector_only_contextual",
        alias="connector_only_contextual",
        default=False,
    )
    run_and_terminate: bool = Field(
        env="connector_run_and_terminate",
        alias="connector_run_and_terminate",
        default=False,
    )
    validate_before_import: bool = Field(
        env="connector_validate_before_import",
        alias="connector_validate_before_import",
        default=False,
    )


class InternalEnrichmentConfig(ConnectorBaseConfig):
    max_tlp: str = Field(
        env="connector_max_tlp", alias="connector_max_tlp", default="TLP:CLEAR"
    )


class ExternalImportConfig(ConnectorBaseConfig):
    interval: int = Field(
        env="connector_interval", alias="connector_interval", default=60
    )


class StreamInputConfig(ConnectorBaseConfig):
    live_stream_id: str = Field(
        env="connector_live_stream_id", alias="connector_live_stream_id", default=None
    )
    live_stream_listen_delete: bool = Field(
        env="connector_live_stream_listen_delete",
        alias="connector_live_stream_listen_delete",
        default=True,
    )
    live_stream_no_dependencies: bool = Field(
        env="connector_live_stream_no_dependencies",
        alias="connector_live_stream_no_dependencies",
        default=False,
    )
    live_stream_with_inferences: bool = Field(
        env="connector_live_stream_with_inferences",
        alias="connector_live_stream_with_inferences",
        default=False,
    )
    live_stream_recover_iso_date: str = Field(
        env="connector_live_stream_recover_iso_date",
        alias="connector_live_stream_recover_iso_date",
        default=None,
    )
    live_stream_start_timestamp: str = Field(
        env="connector_live_stream_start_timestamp",
        alias="connector_live_stream_start_timestamp",
        default=None,
    )


class WorkerConfig(ConnectorBaseSettings):
    pass
