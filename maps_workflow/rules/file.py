from typing import Optional
from pydantic import BaseModel
import operator
import os

from maps_workflow.baserule import BaseRule
from maps_workflow.exceptions import RuleViolationError


class FileSizeParams(BaseModel):
    max_file_size: Optional[str] = None
    min_file_size: Optional[str] = None


class FileSize(BaseRule):
    params: FileSizeParams

    def get_params_model(self):
        return FileSizeParams

    @staticmethod
    def convert_size_to_bytes(size_str: str):
        size_str = size_str.strip().upper()
        units = {"BYTE": 1, "KB": 1024**1, "MB": 1024**2, "GB": 1024**3}

        for unit in units:
            if size_str.endswith(unit):
                return float(size_str[: -len(unit)]) * units[unit]

        raise ValueError("Unknown size unit. Please use Byte, KB, MB or GB.")

    def evaluate(self):
        violations = []
        file_size = None
        op = None

        if self.params.max_file_size:
            file_size = self.params.max_file_size
            op = operator.gt
        elif self.params.min_file_size:
            file_size = self.params.min_file_size
            op = operator.lt

        allowed_size = self.convert_size_to_bytes(file_size)
        stat = os.stat(self.raw_file)
        if op(stat.st_size, allowed_size):
            violations.append(
                RuleViolationError(
                    message=f"The filesize is above the allowed limit of {allowed_size}.",
                    errors=[stat.st_size, operator, file_size],
                )
            )
        return violations

    def explain(self):
        file_size = None
        op = None

        if self.params.max_file_size:
            file_size = self.params.max_file_size
            op = "is not more than"
        elif self.params.min_file_size:
            file_size = self.params.min_file_size
            op = "is not less than"

        return f"File {op} {file_size}"
