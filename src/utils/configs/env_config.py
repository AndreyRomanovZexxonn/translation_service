from pydantic import BaseSettings, Field

from src.utils.enums import EnvType


class EnvConfig(BaseSettings):
    log_level: str = Field(env="LOG_LEVEL", default="DEBUG")
    env: EnvType = Field(env="ENV", default=EnvType.TEST)


ENV_CONFIG = EnvConfig()
