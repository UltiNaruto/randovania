from __future__ import annotations

import dataclasses

from randovania.bitpacking.bitpacking import BitPackDataclass
from randovania.bitpacking.json_dataclass import JsonDataclass
from randovania.games.game import RandovaniaGame
from randovania.layout.base.base_configuration import BaseConfiguration

# TODO: add entrance rando and wall rando


@dataclasses.dataclass(frozen=True)
class PseudoregaliaArtifactConfig(BitPackDataclass, JsonDataclass):
    required_artifacts: int = dataclasses.field(metadata={"min": 0, "max": 5, "precision": 1})


@dataclasses.dataclass(frozen=True)
class PseudoregaliaConfiguration(BaseConfiguration):
    artifacts: PseudoregaliaArtifactConfig
    include_extra_pickups: bool

    @classmethod
    def game_enum(cls) -> RandovaniaGame:
        return RandovaniaGame.PSEUDOREGALIA

    def active_layers(self) -> set[str]:
        result = super().active_layers()

        # if self.include_extra_pickups:
        #    result.add("extra_pickups")

        return result
