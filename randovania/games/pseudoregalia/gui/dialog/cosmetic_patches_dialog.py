from __future__ import annotations

from typing import TYPE_CHECKING

from randovania.games.pseudoregalia.layout.pseudoregalia_cosmetic_patches import PseudoregaliaCosmeticPatches
from randovania.gui.dialog.base_cosmetic_patches_dialog import BaseCosmeticPatchesDialog
from randovania.gui.generated.pseudoregalia_cosmetic_patches_dialog_ui import Ui_PseudoregaliaCosmeticPatchesDialog

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget

    from randovania.layout.base.cosmetic_patches import BaseCosmeticPatches


class PseudoregaliaCosmeticPatchesDialog(BaseCosmeticPatchesDialog, Ui_PseudoregaliaCosmeticPatchesDialog):
    _cosmetic_patches: PseudoregaliaCosmeticPatches

    def __init__(self, parent: QWidget, current: BaseCosmeticPatches):
        super().__init__(parent)
        self.setupUi(self)

        assert isinstance(current, PseudoregaliaCosmeticPatches)
        self._cosmetic_patches = current

        self.on_new_cosmetic_patches(current)
        self.connect_signals()

    def connect_signals(self) -> None:
        super().connect_signals()
        # More signals here!

    def on_new_cosmetic_patches(self, patches: PseudoregaliaCosmeticPatches) -> None:
        # Update fields with the new values
        pass

    @property
    def cosmetic_patches(self) -> PseudoregaliaCosmeticPatches:
        return self._cosmetic_patches

    def reset(self) -> None:
        self.on_new_cosmetic_patches(PseudoregaliaCosmeticPatches())
