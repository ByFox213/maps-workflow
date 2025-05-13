from typing import Optional
import numpy as np
from pydantic import BaseModel, PositiveInt

from maps_workflow.baserule import BaseRule
from maps_workflow.exceptions import RuleError, RuleViolationError


class ExistParams(BaseModel):
    expected_tile: int
    humanized: str
    expected_layer: Optional[str] = None
    min_occurances: Optional[PositiveInt] = None
    max_occurances: Optional[PositiveInt] = None


class Exist(BaseRule):
    params: ExistParams

    def get_params_model(self):
        return ExistParams

    def evaluate(self):
        violations = []
        found_tile = []

        self.find_tiles(found_tile, violations)

        self.check_tile_occurrences(found_tile)

        return violations

    def find_tiles(self, found_tile, violations):
        for group in self.map_file.groups:
            for layer in group.layers:
                if layer.kind() != "Tiles":
                    continue

                for tile_layer in layer.tiles:
                    self.check_tile_layer(tile_layer, layer, found_tile, violations)

    def check_tile_layer(self, tile_layer, layer, found_tile, violations):
        tile_layer_np = np.array(tile_layer)
        matching_indices = np.where(tile_layer_np == self.params.expected_tile)

        for h, w in zip(*matching_indices):
            found_tile.append([tile_layer, h, w])
            self.check_layer_name(layer, h, w, violations)

    def check_layer_name(self, layer, h, w, violations):
        if self.params.expected_layer and layer.name != self.params.expected_layer:
            violations.append(
                RuleViolationError(
                    message=f'Found tile "{self.params.humanized}" at position ({h}, {w}) '
                    f'in layer "{layer.name}" instead of "{self.params.expected_layer}" layer.',
                    errors=[],
                )
            )

    def check_tile_occurrences(self, found_tile):
        if len(found_tile) < 1:
            raise RuleError(message=f'Expected "{self.params.humanized}" is not on the map at all')

        if self.params.min_occurances and len(found_tile) < self.params.min_occurances:
            raise RuleError(
                message=f'Expected "{self.params.humanized}" to be at least {self.params.min_occurances} on the map.'
            )

        if self.params.max_occurances and len(found_tile) > self.params.max_occurances:
            raise RuleError(
                message=f'Expected "{self.params.humanized}" to be max {self.params.max_occurances} on the map.'
            )

    def explain(self):
        return f'Check if map has tile \\"{self.params.humanized}\\" (TileID: {self.params.expected_tile})'
