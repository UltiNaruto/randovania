from __future__ import annotations

from typing import TYPE_CHECKING

import randovania
from randovania.games import game
from randovania.games.pseudoregalia import layout

if TYPE_CHECKING:
    from randovania.games.pseudoregalia.exporter.game_exporter import PseudoregaliaGameExporter
    from randovania.games.pseudoregalia.exporter.options import PseudoregaliaPerGameOptions
    from randovania.games.pseudoregalia.exporter.patch_data_factory import PseudoregaliaPatchDataFactory


def _options() -> type[PseudoregaliaPerGameOptions]:
    from randovania.games.pseudoregalia.exporter.options import PseudoregaliaPerGameOptions

    return PseudoregaliaPerGameOptions


def _gui() -> game.GameGui:
    from randovania.games.pseudoregalia import gui

    return game.GameGui(
        game_tab=gui.PseudoregaliaGameTabWidget,
        tab_provider=gui.preset_tabs,
        cosmetic_dialog=gui.PseudoregaliaCosmeticPatchesDialog,
        export_dialog=gui.PseudoregaliaGameExportDialog,
        progressive_item_gui_tuples=(),
        spoiler_visualizer=(),
    )


def _generator() -> game.GameGenerator:
    from randovania.games.pseudoregalia import generator
    from randovania.generator.hint_distributor import AllJokesHintDistributor

    return game.GameGenerator(
        pickup_pool_creator=generator.pool_creator,
        bootstrap=generator.PseudoregaliaBootstrap(),
        base_patches_factory=generator.PseudoregaliaBasePatchesFactory(),
        hint_distributor=AllJokesHintDistributor(),
    )


def _patch_data_factory() -> type[PseudoregaliaPatchDataFactory]:
    from randovania.games.pseudoregalia.exporter.patch_data_factory import PseudoregaliaPatchDataFactory

    return PseudoregaliaPatchDataFactory


def _exporter() -> PseudoregaliaGameExporter:
    from randovania.games.pseudoregalia.exporter.game_exporter import PseudoregaliaGameExporter

    return PseudoregaliaGameExporter()


game_data: game.GameData = game.GameData(
    short_name="Pseudoregalia",
    long_name="Pseudoregalia",
    development_state=game.DevelopmentState.EXPERIMENTAL,
    presets=[
        {"path": "starter_preset.rdvpreset"},
    ],
    faq=[
        (
            "Which versions of Metroid Planets are supported?",
            "Only version 1.27g is supported. "
            "Later versions are embedding code in the executable "
            "which prevents modifying the code.",
        )
    ],
    layout=game.GameLayout(
        configuration=layout.PseudoregaliaConfiguration,
        cosmetic_patches=layout.PseudoregaliaCosmeticPatches,
        preset_describer=layout.PseudoregaliaPresetDescriber(),
    ),
    options=_options,
    gui=_gui,
    generator=_generator,
    patch_data_factory=_patch_data_factory,
    exporter=_exporter,
    multiple_start_nodes_per_area=False,
    defaults_available_in_game_sessions=randovania.is_dev_version(),
)
