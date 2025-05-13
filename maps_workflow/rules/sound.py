import hashlib

from pydantic import BaseModel
from maps_workflow.baserule import BaseRule


class ValidParams(BaseModel):
    field: str


class Valid(BaseRule):
    params: ValidParams

    def get_params_model(self):
        return ValidParams

    def evaluate(self):
        violations = []
        for sound in self.map_file.sounds:
            print(sound.name)
            data_str = str(sound.data).encode("utf-8")
            sha512_hash = hashlib.sha512()
            sha512_hash.update(data_str)
            print(sha512_hash.hexdigest())
        return violations

    def explain(self):
        return ["setting", "in", None]
