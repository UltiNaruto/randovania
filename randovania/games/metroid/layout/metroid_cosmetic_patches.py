from __future__ import annotations

import dataclasses

from randovania.games.game import RandovaniaGame
from randovania.layout.base.cosmetic_patches import BaseCosmeticPatches


@dataclasses.dataclass(frozen=True)
class MetroidCosmeticPatches(BaseCosmeticPatches):
    @classmethod
    def game(cls):
        return RandovaniaGame.METROID
