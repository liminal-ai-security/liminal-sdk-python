"""Define model helpers."""

from mashumaro import DataClassDictMixin
from mashumaro.config import BaseConfig


class BaseModel(DataClassDictMixin):
    """Define a base model."""

    class Config(BaseConfig):
        """Define the configuration."""

        code_generation_options = ["TO_DICT_ADD_BY_ALIAS_FLAG"]  # noqa: RUF012
