from typing import Dict, List, Optional
from enum import Enum
from pydantic import BaseModel
import twmap


class BaseRule:
    raw_file: str
    map_file: twmap.Map | None
    params: dict

    def __init__(self, raw_file, map_file: twmap.Map | None, params) -> None:
        self.raw_file = raw_file
        self.map_file = map_file

        if params:
            self.params = self.get_params_model()(**params)

    def get_params_model(self):
        raise NotImplementedError

    def evaluate(self):
        raise NotImplementedError

    def explain(self) -> str:
        raise NotImplementedError


class BaseRuleConfig(BaseModel):
    name: str
    module: str
    class_name: str
    description: str
    type: str
    depends_on: List[str]
    params: Dict | None


class Status(Enum):
    FAILED = 0
    COMPLETED = 1
    WARN = 2
    SKIP = 3


class RuleStatus(BaseModel):
    status: Status
    explain: Optional[str]
    rule: Optional["BaseRuleConfig"] = None
    violations: list

    class Config:
        arbitrary_types_allowed = True
