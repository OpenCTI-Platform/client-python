from pathlib import Path
from typing import Any, Dict
import yaml
from pydantic import BaseSettings


class ConnectorBaseConfig(BaseSettings):
    scheduler: str
    log_level: str = "INFO"

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


def yml_config_setting(settings: BaseSettings) -> Dict[str, Any]:
    encoding = settings.__config__.env_file_encoding
    path = Path("config.yml")
    content = {}
    if path.exists():
        with open(path, "r", encoding=encoding) as f:
            content = yaml.safe_load(f)
    return content


class RunException(Exception):
    pass


#
# class InternalImportArguments(ConnectorArguments):
#     file_id: str
#     file_mime: str
#     file_fetch: str
#     entity_id: str
#
#
# class StixImportArgument(ConnectorArguments):
#     token: str
#
#
# class InternalEnrichmentArgument(ConnectorArguments):
#     entity_id: str
#
#
# class InternalExportArgument(ConnectorArguments):
#     export_scope: str
#     export_type: str
#     file_name: str
#     max_marking: str
#     entity_type: str
#     entity_id: Optional[str]
#     list_params: Optional[List[str]]
