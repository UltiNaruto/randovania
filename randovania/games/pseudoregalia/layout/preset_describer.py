from __future__ import annotations

from typing import TYPE_CHECKING

from randovania.games.pseudoregalia.layout.pseudoregalia_configuration import (
    PseudoregaliaArtifactConfig,
    PseudoregaliaConfiguration,
)
from randovania.layout.preset_describer import (
    GamePresetDescriber,
    fill_template_strings_from_tree,
    message_for_required_mains,
)

if TYPE_CHECKING:
    from randovania.layout.base.base_configuration import BaseConfiguration


def describe_artifacts(artifacts: PseudoregaliaArtifactConfig) -> list[dict[str, bool]]:
    return [
        {
            f"{artifacts.required_artifacts} Major Keys and defeat Princess": True,
        },
    ]


class PseudoregaliaPresetDescriber(GamePresetDescriber):
    def format_params(self, configuration: BaseConfiguration) -> dict[str, list[str]]:
        assert isinstance(configuration, PseudoregaliaConfiguration)

        template_strings = super().format_params(configuration)

        extra_message_tree = {
            "Game Changes": [
                message_for_required_mains(
                    configuration.ammo_pickup_configuration,
                    {
                        "Air Kicks need Sun Greaves": "Air Kick",
                    },
                ),
            ],
            "Goal": describe_artifacts(configuration.artifacts),
        }

        fill_template_strings_from_tree(template_strings, extra_message_tree)

        return template_strings
