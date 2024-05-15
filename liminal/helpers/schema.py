"""Define schema helpers."""

from mashumaro import DataClassDictMixin
from mashumaro.config import BaseConfig


class BaseResponseSchema(DataClassDictMixin):
    """Define a base response schema."""

    class Config(BaseConfig):  # pylint: disable=too-few-public-methods
        """Define the configuration."""

        code_generation_options = ["TO_DICT_ADD_BY_ALIAS_FLAG"]  # noqa: RUF012
