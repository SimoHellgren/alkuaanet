from typing import Any
from pydantic import BaseModel


class Opus(BaseModel):
    pk: str
    sk: str
    opus: Any  # this should probably be handled better, see: https://docs.pydantic.dev/latest/concepts/types/#handling-third-party-types
