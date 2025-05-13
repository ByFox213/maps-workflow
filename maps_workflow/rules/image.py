from genericpath import isfile
import hashlib
import os
from pathlib import Path
from posixpath import join

from pydantic import BaseModel
from maps_workflow.baserule import BaseRule
from maps_workflow.exceptions import RuleViolationError


class ValidParams(BaseModel):
    pass


class Valid(BaseRule):
    params: ValidParams
    __external_mapres: list = [Path(f).stem for f in os.listdir("./data/mapres") if isfile(join("./data/mapres", f))]
    __custom_mapres: list = [
        Path(f).stem for f in os.listdir("./data/custom_mapres") if isfile(join("./data/custom_mapres", f))
    ]

    def get_params_model(self):
        return ValidParams

    def evaluate(self):
        violations = []
        for image in self.map_file.images:
            if image.height() % 16 != 0:
                violations.append(
                    RuleViolationError(
                        message=f"{image.name} height is not divisable by 16, may encounter visual bugs",
                        errors=[image.height(), "%", 16],
                    )
                )

            if image.width() % 16 != 0:
                violations.append(
                    RuleViolationError(
                        message=f"{image.name} width is not divisable by 16, may encounter visual bugs",
                        errors=[image.width(), "%", 16],
                    )
                )

            if image.is_embedded():
                if image.data is not None and image.data.size > 0:
                    sha512_hash = hashlib.sha512()
                    sha512_hash.update(image.data.all().tobytes())

                    # print(image.name)
                    # print(sha512_hash.hexdigest())
                    # TODO: Check hash against known hashes otherwise ask for permission
                    if f"{image.name}-{sha512_hash.hexdigest()}" not in self.__custom_mapres:
                        violations.append(
                            RuleViolationError(
                                message=f"{image.name}-{sha512_hash.hexdigest()}.png is not an allowed custom mapres. "
                                f"Ask mappers to approve it first",
                                errors=[image.name, ">", 0],
                            )
                        )
                else:
                    violations.append(
                        RuleViolationError(
                            message=f"{image.name} is embedded but has no data.",
                            errors=[image.data.size, ">", 0],
                        )
                    )

            if image.is_external():
                if image.name not in self.__external_mapres:
                    violations.append(
                        RuleViolationError(
                            message=f"{image.name} is not a valid mapres, "
                            f"either the mapres is missing or you have used a wrong one",
                            errors=[image.name, ">", 0],
                        )
                    )

        return violations

    def explain(self):
        return ["setting", "in", None]
