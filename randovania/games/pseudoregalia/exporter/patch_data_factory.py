from __future__ import annotations

from randovania.exporter.patch_data_factory import PatchDataFactory
from randovania.games.game import RandovaniaGame


class PseudoregaliaPatchDataFactory(PatchDataFactory):
    def game_enum(self) -> RandovaniaGame:
        return RandovaniaGame.PSEUDOREGALIA

    def create_data(self) -> dict:
        return {}
