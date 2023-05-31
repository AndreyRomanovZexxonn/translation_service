import os
from pathlib import Path
from typing import ClassVar, Callable, Any, Type, Iterable, Optional

import pydantic as pd
from omegaconf import OmegaConf, DictConfig, Resolver
from pydantic import BaseModel

from src.infra.repositories.mongodb.configuration import MongodbConfiguration
from src.utils.configs.env_config import ENV_CONFIG
from src.utils.enums import EnvType


class ServerConfig(BaseModel):
    port: int = 8000
    reload: bool = False


class AppConfiguration(BaseModel):
    env: EnvType
    mongodb: MongodbConfiguration
    server: ServerConfig


class ConfigManager:
    CONFIGURATION_KEY = "configuration"
    OUTPUT_ENV_VARS_KEY = "envs"
    resolvers: ClassVar[dict[str, "Resolver"]] = {}

    @classmethod
    def load_configuration(cls, env: Optional[EnvType] = None, as_dict: bool = False) -> dict | AppConfiguration:
        if env == EnvType.TEST:
            working_dir_path = os.getcwd()
            source_path = working_dir_path.split('tests')[0]
            config: DictConfig = cls._load_many(
                (
                    Path(f"{source_path}/configs/.env.base.yaml"),
                    Path(f"{source_path}/configs/.env.{env.value}.yaml")
                )
            )
        else:
            config: DictConfig = cls._load_many(
                (
                    Path(f"./configs/.env.base.yaml"),
                    env and Path(f"./configs/.env.{env.value}.yaml")
                )
            )
        return cls._convert(config, as_dict=as_dict)

    @classmethod
    def register_resolver(cls, name: str = None):
        def wrapper(func: "Callable"):
            cls.resolvers[name or func.__name__] = func
            return func
        return wrapper

    @classmethod
    def _convert(cls, config: DictConfig, as_dict: bool = True):
        if as_dict:
            return cls._as_dict(config)
        return pd.parse_obj_as(AppConfiguration, cls._as_dict(config)[cls.CONFIGURATION_KEY])

    @classmethod
    def register_resolvers(cls):
        OmegaConf.clear_resolvers()
        for name, resolver in cls.resolvers.items():
            OmegaConf.register_new_resolver(name, resolver, replace=False)

    @classmethod
    def _as_dict(cls, config: DictConfig) -> dict:
        return OmegaConf.to_container(config, resolve=True)

    @classmethod
    def _load(cls, data: str | Path) -> DictConfig:
        if not data:
            return DictConfig({})

        if isinstance(data, Path):
            return OmegaConf.load(data)
        if isinstance(data, str):
            return OmegaConf.create(data)
        raise ValueError(f"Unsupported data type {type(data)} to load config from")

    @classmethod
    def _load_many(cls, data: Iterable[Path | str]) -> DictConfig:
        config = DictConfig({})
        config.merge_with(*(cls._load(path) for path in data))
        return config


@ConfigManager.register_resolver()
def with_alias(value: Any, alias_name: str, aliases: "DictConfig"):
    setattr(aliases, alias_name, value)
    return value


def create_type_resolver(resolver_name, _class_type: Type):
    @ConfigManager.register_resolver(resolver_name)
    def resolver(value: Any) -> _class_type:
        return _class_type(value)


for class_type in (
        int, str, float, Path
):
    create_type_resolver(f"as_{class_type.__name__.lower()}", class_type)


APP_CONFIG: AppConfiguration = ConfigManager.load_configuration(env=ENV_CONFIG.env)
