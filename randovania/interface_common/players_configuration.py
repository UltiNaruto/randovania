from dataclasses import dataclass

from randovania.games.game import RandovaniaGame
from randovania.layout.base.ammo_state import AmmoState
from randovania.layout.base.major_item_state import MajorItemState


@dataclass(frozen=True)
class PlayersConfiguration:
    player_index: int
    player_names: dict[int, str]
    player_games: dict[int, RandovaniaGame]
    player_items_state: dict[int, dict[str, MajorItemState]]
    player_ammos_state: dict[int, dict[str, AmmoState]]

    @property
    def is_multiworld(self) -> int:
        return len(self.player_names) > 1

    def get_item_state_from_player(self, idx: int, item_name: str) -> MajorItemState:
        if idx > len(self.player_names) - 1:
            raise IndexError(f"Cannot get player {idx}! (Index : {idx} > {len(self.player_names) - 1})")

        if not item_name in self.player_items_state[idx].keys():
            raise Exception(f"Cannot find item state of {item_name}!")

        return self.player_items_state[idx][item_name]

    def get_ammo_state_from_player(self, idx: int, ammo_name: str) -> AmmoState:
        if idx > len(self.player_names) - 1:
            raise IndexError(f"Cannot get player {idx}! (Index : {idx} > {len(self.player_names) - 1})")

        if not ammo_name in self.player_ammos_state[idx].keys():
            raise Exception(f"Cannot find ammo state of {ammo_name}!")

        return self.player_ammos_state[idx][ammo_name]
