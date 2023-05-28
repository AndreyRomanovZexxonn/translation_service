from enum import Enum, auto


class AutoName(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name


class AutoLowerName(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name.lower()


class EnvType(str, AutoLowerName):
    PROD = auto()  # Deployment on Production
    STG = auto()  # Deployment on Staging
    TEST = auto()  # Unit and Integration Tests in CI
    DEV = auto()  # Custom env for debugging
