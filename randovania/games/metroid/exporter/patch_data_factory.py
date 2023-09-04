from __future__ import annotations

from randovania.exporter.patch_data_factory import BasePatchDataFactory
from randovania.games.game import RandovaniaGame


class MetroidPatchDataFactory(BasePatchDataFactory):
    def game_enum(self) -> RandovaniaGame:
        return RandovaniaGame.METROID

    def create_data(self) -> dict:
        return {}
