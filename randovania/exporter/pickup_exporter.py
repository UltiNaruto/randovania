import dataclasses
from random import Random

from randovania.exporter import item_names
from randovania.game_description.assignment import PickupTarget
from randovania.game_description.game_description import GameDescription
from randovania.game_description.game_patches import GamePatches
from randovania.game_description.resources.item_resource_info import ItemResourceInfo
from randovania.game_description.resources.pickup_entry import (PickupEntry, ConditionalResources, PickupModel,
                                                                ResourceConversion)
from randovania.game_description.resources.pickup_index import PickupIndex
from randovania.game_description.resources.resource_info import ResourceGainTuple
from randovania.game_description.world.pickup_node import PickupNode
from randovania.game_description.world.world_list import WorldList
from randovania.games.game import RandovaniaGame
from randovania.interface_common.players_configuration import PlayersConfiguration
from randovania.layout.base.pickup_model import PickupModelStyle, PickupModelDataSource

from randovania.gui.preset_settings.metroid_item_pool_tab import ICE_TRAP_SHOW_AS


"""
Link to the stackoverflow post : https://stackoverflow.com/questions/10492869/how-to-convert-words-to-leetspeak-with-python
"""
def _scramble_text(rng: Random, message: str):
    """Convert english string to leetspeak"""
    char_map = {
        "a": ["4", "A"],
        "b": ["I3", "8", "B"],
        "c": ["C", "("],
        "d": ["D"],
        "e": ["3", "E"],
        "f": ["F", "ph", "pH", "PH"],
        "g": ["G"],
        "h": ["H"],
        "i": ["1", "I", "!", "|"],
        "j": ["J"],
        "k": ["K"],
        "l": ["1", "L"],
        "m": ["M"],
        "n": ["N"],
        "o": ["0", "O"],
        "p": ["P"],
        "q": ["Q"],
        "r": ["R"],
        "s": ["$", "5", "S"],
        "t": ["7", "T"],
        "u": ["U"],
        "v": ["V"],
        "w": ["W"],
        "x": ["X"],
        "y": ["Y"],
        "z": ["2", "Z"],
    }
    leetspeak = ""
    for char in message:
        if char.lower() in char_map and rng.random() <= 0.30:  # 30% convert
            possible_replacements = char_map[char.lower()]
            leet_replacement = rng.choice(possible_replacements)
            leetspeak = leetspeak + leet_replacement
        else:
            leetspeak = leetspeak + char
    return leetspeak


def _conditional_resources_for_pickup(pickup: PickupEntry) -> list[ConditionalResources]:
    if len(pickup.progression) > 1:
        assert pickup.resource_lock is None, pickup.name
        return list(pickup.conditional_resources)

    else:
        resources = list(pickup.extra_resources)
        name = pickup.name
        if pickup.progression:
            name = pickup.progression[0][0].long_name
            resources.append(pickup.progression[0])

        lock = pickup.resource_lock
        # A lock that goes to the same item is ignored for the patcher, for simplification
        if (pickup.respects_lock and not pickup.unlocks_resource
                and lock is not None and lock.temporary_item != lock.item_to_lock):

            locked_resources = lock.convert_gain(resources)
            return [
                ConditionalResources(
                    name=f"Locked {name}",
                    item=None,
                    resources=tuple(locked_resources),
                ),
                ConditionalResources(
                    name=name,
                    item=lock.locked_by,
                    resources=tuple(resources),
                ),
            ]
        else:
            return [
                ConditionalResources(
                    name=name,
                    item=None,
                    resources=tuple(resources),
                ),
            ]


def _pickup_description(pickup: PickupEntry) -> str:
    if not pickup.item_category.is_expansion:
        if len(pickup.progression) > 1:
            return "Provides the following in order: {}.".format(
                ", ".join(conditional.name for conditional in pickup.conditional_resources)
            )
        else:
            return ""

    ammo_desc = [
        item_names.add_quantity_to_resource(item_names.resource_user_friendly_name(resource), quantity, True)
        for resource, quantity in pickup.extra_resources
    ]
    if ammo_desc:
        return "Provides {}{}{}.".format(
            ", ".join(ammo_desc[:-1]),
            " and " if len(ammo_desc) > 1 else "",
            ammo_desc[-1],
        )
    else:
        return ""


def _get_single_hud_text(pickup_name: str,
                         memo_data: dict[str, str],
                         resources: ResourceGainTuple,
                         ) -> str:
    return memo_data[pickup_name].format(**{
        item_names.resource_user_friendly_name(resource): quantity
        for resource, quantity in resources
    })


def _get_all_hud_text(conditionals: list[ConditionalResources],
                      memo_data: dict[str, str],
                      ) -> list[str]:
    return [
        _get_single_hud_text(conditional.name, memo_data, conditional.resources)
        for conditional in conditionals
    ]


def _calculate_collection_text(pickup: PickupEntry,
                               visual_pickup: PickupEntry,
                               model_style: PickupModelStyle,
                               memo_data: dict[str, str],
                               ) -> list[str]:
    """
    Calculates what the hud_text for a pickup should be
    :param pickup:
    :param visual_pickup:
    :param model_style:
    :param memo_data:
    :return:
    """

    if model_style == PickupModelStyle.HIDE_ALL:
        hud_text = _get_all_hud_text(_conditional_resources_for_pickup(visual_pickup), memo_data)
        num_conditional = len(_conditional_resources_for_pickup(pickup))
        if len(hud_text) == num_conditional:
            return hud_text
        else:
            return [hud_text[0]] * num_conditional

    else:
        return _get_all_hud_text(_conditional_resources_for_pickup(pickup), memo_data)


@dataclasses.dataclass(frozen=True)
class ExportedPickupDetails:
    index: PickupIndex
    name: str
    description: str
    collection_text: list[str]
    conditional_resources: list[ConditionalResources]
    conversion: list[ResourceConversion]
    model: PickupModel
    other_player: bool
    original_pickup: PickupEntry


class PickupExporter:
    def create_details(self,
                       original_index: PickupIndex,
                       pickup_target: PickupTarget,
                       visual_pickup: PickupEntry,
                       model_style: PickupModelStyle,
                       name: str,
                       description: str,
                       model: PickupModel) -> ExportedPickupDetails:
        raise NotImplementedError()

    def export(self,
               original_index: PickupIndex,
               pickup_target: PickupTarget,
               visual_pickup: PickupEntry,
               model_style: PickupModelStyle,
               ) -> ExportedPickupDetails:
        model_pickup = pickup_target.pickup if model_style == PickupModelStyle.ALL_VISIBLE else visual_pickup

        if model_style in {PickupModelStyle.ALL_VISIBLE, PickupModelStyle.HIDE_MODEL}:
            name = pickup_target.pickup.name
            description = _pickup_description(pickup_target.pickup)
        else:
            name = visual_pickup.name
            description = ""

        return self.create_details(original_index, pickup_target, visual_pickup,
                                   model_style, name, description, model_pickup.model)


class PickupExporterSolo(PickupExporter):
    def __init__(self, rng: Random, memo_data: dict[str, str], player_config: PlayersConfiguration):
        self.rng = rng
        self.memo_data = memo_data
        self.player_config = player_config

    def create_details(self,
                       original_index: PickupIndex,
                       pickup_target: PickupTarget,
                       visual_pickup: PickupEntry,
                       model_style: PickupModelStyle,
                       name: str,
                       description: str,
                       model: PickupModel) -> ExportedPickupDetails:
        game = self.player_config.player_games[0]
        pickup = pickup_target.pickup

        scan_text = name
        collection_text = _calculate_collection_text(pickup, visual_pickup, model_style, self.memo_data)
        final_description = ""
        final_model = model

        if game == RandovaniaGame.METROID_PRIME:
            ice_trap_show_as_val = ICE_TRAP_SHOW_AS[self.player_config.get_item_state_from_player(0, "Ice Trap").extra["show_as"]]
            if pickup.name == "Ice Trap":
                scan_text = "FOOL!"
                collection_text = ["You're a FOOL!"]
                if ice_trap_show_as_val != "Ice Trap":
                    fake_pickups = [
                        item_name for item_name, item_state in self.player_config.player_items_state[0].items()
                        if item_state.num_shuffled_pickups > 0 and not item_name in ["Missile Launcher", "Ice Trap"]
                    ]
                    fake_pickup = fake_pickups[self.rng.randint(0, len(fake_pickups) - 1)]
                    final_model = PickupModel(game, fake_pickup)
                    if ice_trap_show_as_val == "Shuffled Model/Text":
                        scan_text = f"{_scramble_text(self.rng, fake_pickup)}."
                        if fake_pickup == "Missile Expansion" or fake_pickup == "Power Bomb Expansion":
                            ammo_count, _ = self.player_config.get_ammo_state_from_player(0, fake_pickup.long_name).ammo_count
                            fake_pickup_ammo = fake_pickup[:-10]
                            if ammo_count > 1:
                                fake_pickup_ammo += "s"
                            final_description = f"Provides {ammo_count} {fake_pickup_ammo}."

        return ExportedPickupDetails(
            index=original_index,
            name=scan_text,
            description=final_description,
            collection_text=collection_text,
            conditional_resources=_conditional_resources_for_pickup(pickup),
            conversion=list(pickup.convert_resources),
            model=final_model,
            other_player=False,
            original_pickup=pickup,
        )


class PickupExporterMulti(PickupExporter):
    def __init__(self, rng: Random, solo_creator: PickupExporter, multiworld_item: ItemResourceInfo,
                 players_config: PlayersConfiguration):
        self.rng = rng
        self.solo_creator = solo_creator
        self.multiworld_item = multiworld_item
        self.players_config = players_config

    def create_details(self,
                       original_index: PickupIndex,
                       pickup_target: PickupTarget,
                       visual_pickup: PickupEntry,
                       model_style: PickupModelStyle,
                       name: str,
                       description: str,
                       model: PickupModel) -> ExportedPickupDetails:
        if pickup_target.player == self.players_config.player_index:
            details = self.solo_creator.create_details(original_index, pickup_target, visual_pickup,
                                                       model_style, name, description, model)
            return dataclasses.replace(details, name=f"Your {details.name}")
        else:
            other_game = self.players_config.player_games[pickup_target.player]
            other_name = self.players_config.player_names[pickup_target.player]
            if self.multiworld_item is not None:
                resources = ((self.multiworld_item, original_index.index + 1),)
            else:
                resources = tuple()

            scan_text = f"{other_name}'s {name}"
            collection_text = [f"Sent {name} to {other_name}!"]
            final_description = ""
            final_model = model

            if other_game == RandovaniaGame.METROID_PRIME:
                ice_trap_show_as_val = ICE_TRAP_SHOW_AS[self.players_config.get_item_state_from_player(pickup_target.player, "Ice Trap").extra["show_as"]]
                if pickup_target.pickup.name == "Ice Trap":
                    scan_text = "FOOL!"
                    collection_text = ["You're a FOOL!"]
                    if ice_trap_show_as_val != "Ice Trap":
                        fake_pickups = [
                            item_name for item_name, item_state in
                            self.players_config.player_items_state[pickup_target.player].items()
                            if item_state.num_shuffled_pickups > 0 and not item_name in ["Missile Launcher", "Ice Trap"]
                        ]
                        fake_pickup = fake_pickups[self.rng.randint(0, len(fake_pickups) - 1)]
                        final_model = PickupModel(other_game, fake_pickup)
                        if ice_trap_show_as_val == "Shuffled Model/Text":
                            scan_text = f"{other_name}'s {_scramble_text(self.rng, fake_pickup)}"
                            if fake_pickup in self.players_config.player_ammos_state[pickup_target.player].keys():
                                ammo_count, _ = self.players_config.get_ammo_state_from_player(pickup_target.player, fake_pickup.long_name).ammo_count
                                fake_pickup_ammo = fake_pickup[:-10]
                                if ammo_count > 1:
                                    fake_pickup_ammo += "s"
                                final_description = f"Provides {ammo_count} {fake_pickup_ammo}.".strip()

            return ExportedPickupDetails(
                index=original_index,
                name=scan_text,
                description=final_description,
                collection_text=collection_text,
                conditional_resources=[ConditionalResources(
                    name=None,
                    item=None,
                    resources=resources,
                )],
                conversion=[],
                model=final_model,
                other_player=True,
                original_pickup=pickup_target.pickup,
            )


def _get_visual_model(original_index: int,
                      pickup_list: list[PickupTarget],
                      data_source: PickupModelDataSource,
                      visual_etm: PickupEntry,
                      ) -> PickupEntry:
    if data_source == PickupModelDataSource.ETM:
        return visual_etm
    elif data_source == PickupModelDataSource.RANDOM:
        return pickup_list[original_index % len(pickup_list)].pickup
    elif data_source == PickupModelDataSource.LOCATION:
        raise NotImplementedError()
    else:
        raise ValueError(f"Unknown data_source: {data_source}")


def export_all_indices(patches: GamePatches,
                       useless_target: PickupTarget,
                       world_list: WorldList,
                       rng: Random,
                       model_style: PickupModelStyle,
                       data_source: PickupModelDataSource,
                       exporter: PickupExporter,
                       visual_etm: PickupEntry,
                       ) -> list[ExportedPickupDetails]:
    """
    Creates the patcher data for all pickups in the game
    :param patches:
    :param useless_target:
    :param world_list:
    :param rng:
    :param model_style:
    :param data_source:
    :param exporter:
    :param visual_etm:
    :return:
    """
    pickup_assignment = patches.pickup_assignment

    pickup_list = list(pickup_assignment.values())
    rng.shuffle(pickup_list)

    indices = sorted(
        node.pickup_index
        for node in world_list.iterate_nodes()
        if isinstance(node, PickupNode)
    )

    pickups = [
        exporter.export(index,
                        pickup_assignment.get(index, useless_target),
                        _get_visual_model(i, pickup_list, data_source, visual_etm),
                        model_style,
                        )
        for i, index in enumerate(indices)
    ]

    return pickups


class GenericAcquiredMemo(dict):
    def __missing__(self, key):
        return f"{key} acquired!"


def create_pickup_exporter(rng: Random, game: GameDescription, memo_data: dict, players_config: PlayersConfiguration):
    exporter = PickupExporterSolo(rng, memo_data, players_config)
    if players_config.is_multiworld:
        exporter = PickupExporterMulti(rng, exporter, game.resource_database.multiworld_magic_item,
                                       players_config)
    return exporter
