from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6 import QtWidgets

from randovania.games.planets_zebeth.layout import PlanetsZebethConfiguration
from randovania.gui.preset_settings.preset_tab import PresetTab

if TYPE_CHECKING:
    from randovania.game_description.game_description import GameDescription
    from randovania.gui.lib.window_manager import WindowManager
    from randovania.interface_common.preset_editor import PresetEditor
    from randovania.layout.preset import Preset

# TODO: add walljump, downward shooting and open missile doors with 1 missile patches


class PresetPlanetsZebethPatches(PresetTab):
    def __init__(self, editor: PresetEditor, game_description: GameDescription, window_manager: WindowManager):
        super().__init__(editor, game_description, window_manager)

        self.root_widget = QtWidgets.QWidget(self)
        self.root_layout = QtWidgets.QVBoxLayout(self.root_widget)

        self.include_extra_pickups_check = QtWidgets.QCheckBox(self.root_widget)
        self.include_extra_pickups_check.setEnabled(True)
        self.include_extra_pickups_check.setText("Include Extra Pickups")
        self.root_layout.addWidget(self.include_extra_pickups_check)

        self.setCentralWidget(self.root_widget)

        # Signals
        self.include_extra_pickups_check.stateChanged.connect(self._persist_option_then_notify("include_extra_pickups"))

    @classmethod
    def tab_title(cls) -> str:
        return "Other"

    @classmethod
    def uses_patches_tab(cls) -> bool:
        return True

    def on_preset_changed(self, preset: Preset):
        config = preset.configuration
        assert isinstance(config, PlanetsZebethConfiguration)
        self.include_extra_pickups_check.setChecked(config.include_extra_pickups)
