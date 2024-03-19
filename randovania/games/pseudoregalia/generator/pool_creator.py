from __future__ import annotations

from typing import TYPE_CHECKING

from randovania.game_description.pickup import pickup_category
from randovania.game_description.pickup.pickup_entry import PickupEntry, PickupGeneratorParams, PickupModel
from randovania.game_description.resources.location_category import LocationCategory
from randovania.games.pseudoregalia.layout.pseudoregalia_configuration import (
    PseudoregaliaArtifactConfig,
    PseudoregaliaConfiguration,
)
from randovania.generator.pickup_pool import PoolResults
from randovania.layout.exceptions import InvalidConfiguration

if TYPE_CHECKING:
    from randovania.game_description.game_description import GameDescription
    from randovania.game_description.resources.resource_database import ResourceDatabase
    from randovania.layout.base.base_configuration import BaseConfiguration

MAJOR_KEY_CATEGORY = pickup_category.PickupCategory(
    name="key", long_name="Major Key", hint_details=("some ", "key"), hinted_as_major=False, is_key=True
)
MAJOR_KEYS = [
    {"long_name": "Major Key - Tower Remains", "short_name": "MajorKey_Tower"},
    {"long_name": "Major Key - Empty Bailey", "short_name": "MajorKey_EmptyBailey"},
    {"long_name": "Major Key - Samsa Keep", "short_name": "MajorKey_Keep"},
    {"long_name": "Major Key - The Underbelly", "short_name": "MajorKey_Underbelly"},
    {"long_name": "Major Key - Twilight Theatre", "short_name": "MajorKey_Twilight"},
]


def create_pseudoregalia_artifact(
    artifact_number: int,
    resource_database: ResourceDatabase,
) -> PickupEntry:
    return PickupEntry(
        name=MAJOR_KEYS[artifact_number]["long_name"],
        progression=((resource_database.get_item(MAJOR_KEYS[artifact_number]["short_name"]), 1),),
        model=PickupModel(game=resource_database.game_enum, name="bigKey"),
        pickup_category=MAJOR_KEY_CATEGORY,
        broad_category=pickup_category.GENERIC_KEY_CATEGORY,
        generator_params=PickupGeneratorParams(
            preferred_location_category=LocationCategory.MAJOR,
            probability_offset=0.25,
        ),
    )


def pool_creator(results: PoolResults, configuration: BaseConfiguration, game: GameDescription) -> None:
    assert isinstance(configuration, PseudoregaliaConfiguration)

    results.extend_with(artifact_pool(game, configuration.artifacts))


def artifact_pool(game: GameDescription, config: PseudoregaliaArtifactConfig) -> PoolResults:
    keys: list[PickupEntry] = [create_pseudoregalia_artifact(i, game.resource_database) for i in range(5)]

    # Check whether we have valid artifact requirements in configuration
    if config.required_artifacts > 5:
        raise InvalidConfiguration("More Major Keys than allowed!")

    keys_to_shuffle = keys[: config.required_artifacts]
    starting_keys = keys[config.required_artifacts :]

    return PoolResults(keys_to_shuffle, {}, starting_keys)
