from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING

from PySide6 import QtCore

from randovania.games.pseudoregalia.layout.pseudoregalia_configuration import (
    PseudoregaliaArtifactConfig,
    PseudoregaliaConfiguration,
)
from randovania.gui.generated.preset_pseudoregalia_goal_ui import Ui_PresetPseudoregaliaGoal
from randovania.gui.preset_settings.preset_tab import PresetTab

if TYPE_CHECKING:
    from collections.abc import Callable

    from randovania.game_description.game_description import GameDescription
    from randovania.gui.lib.window_manager import WindowManager
    from randovania.interface_common.preset_editor import PresetEditor
    from randovania.layout.preset import Preset


class PresetPseudoregaliaGoal(PresetTab, Ui_PresetPseudoregaliaGoal):
    def __init__(self, editor: PresetEditor, game_description: GameDescription, window_manager: WindowManager):
        super().__init__(editor, game_description, window_manager)
        self.setupUi(self)

        self.goal_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.keys_slider.valueChanged.connect(self._on_keys_slider_changed)

    @classmethod
    def tab_title(cls) -> str:
        return "Goal"

    @classmethod
    def uses_patches_tab(cls) -> bool:
        return False

    def _edit_config(self, call: Callable[[PseudoregaliaArtifactConfig], PseudoregaliaArtifactConfig]) -> None:
        config = self._editor.configuration
        assert isinstance(config, PseudoregaliaConfiguration)

        with self._editor as editor:
            editor.set_configuration_field("artifacts", call(config.artifacts))

    def _on_keys_slider_changed(self) -> None:
        plural = "s" if self.keys_slider.value() > 1 else ""
        self.keys_slider_label.setText(f"{self.keys_slider.value()} Key{plural}")

        def edit(config: PseudoregaliaArtifactConfig) -> PseudoregaliaArtifactConfig:
            return dataclasses.replace(config, required_artifacts=self.keys_slider.value())

        self._edit_config(edit)

    def on_preset_changed(self, preset: Preset) -> None:
        assert isinstance(preset.configuration, PseudoregaliaConfiguration)
        artifacts = preset.configuration.artifacts
        self.keys_slider.setValue(artifacts.required_artifacts)
