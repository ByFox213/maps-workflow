from typing import List, Optional
from pydantic import BaseModel
from maps_workflow.baserule import BaseRule
from maps_workflow.exceptions import RuleViolationError


class ValidParams(BaseModel):
    field: str
    type: str
    regex: Optional[str] = None
    values: Optional[List[str]] = []


class Valid(BaseRule):
    params: ValidParams

    def get_params_model(self):
        return ValidParams

    def __handle_noop(self, value):
        return

    def __handle_regex(self, value):
        print(value)

    def __handle_list(self, value: str):
        values = value.split(",")
        for val in values:
            if val not in self.params.values:
                return RuleViolationError(message=f"{val} is not in {self.params.values}", errors=[])
        return None

    def evaluate(self):
        violations = []

        if hasattr(self.map_file.info.settings, self.params.field):
            value = getattr(self.map_file.info.settings, self.params.field)
            value_type = {
                "list": self.__handle_list,
                "regex": self.__handle_regex,
            }
            violations.append(value_type.get(self.params.type, self.__handle_noop)(value))

        return violations

    def explain(self):
        if hasattr(self.map_file.info.settings, self.params.field):
            value = getattr(self.map_file.info.settings, self.params.field)
            return f"Setting '{value}' in '{self.params.field}' is not a valid option"
        else:
            return f"Setting '{self.params.field}' does not exist, but is required"
