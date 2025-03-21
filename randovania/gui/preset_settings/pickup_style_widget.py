from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QDialog, QWidget

from randovania.gui.generated.widget_pickup_style_ui import Ui_PickupStyleWidget
from randovania.gui.lib import signal_handling
from randovania.layout.base.pickup_model import PickupModelDataSource, PickupModelStyle

if TYPE_CHECKING:
    from PySide6 import QtWidgets

    from randovania.interface_common.preset_editor import PresetEditor
    from randovania.layout.base.base_configuration import BaseConfiguration


class PickupStyleWidget(QDialog, Ui_PickupStyleWidget):
    Changed = Signal()

    def __init__(self, parent: QWidget | None, editor: PresetEditor):
        super().__init__(parent)
        self.setupUi(self)
        self._editor = editor

        # Item Data
        for i, value in enumerate(PickupModelStyle):
            self.pickup_model_combo.setItemData(i, value)
        for i, value in enumerate(PickupModelDataSource):
            self.pickup_data_source_combo.setItemData(i, value)

        # TODO: implement the LOCATION data source
        self.pickup_data_source_combo.removeItem(self.pickup_data_source_combo.findData(PickupModelDataSource.LOCATION))
        self.pickup_model_combo.currentIndexChanged.connect(
            self._persist_enum(self.pickup_model_combo, "pickup_model_style")
        )
        self.pickup_data_source_combo.currentIndexChanged.connect(
            self._persist_enum(self.pickup_data_source_combo, "pickup_model_data_source")
        )

    def _persist_enum(self, combo: QtWidgets.QComboBox, attribute_name: str):
        def persist(index: int):
            with self._editor as options:
                options.set_configuration_field(attribute_name, combo.itemData(index))

        return persist

    def update(self, layout: BaseConfiguration):
        signal_handling.set_combo_with_value(self.pickup_model_combo, layout.pickup_model_style)
        signal_handling.set_combo_with_value(self.pickup_data_source_combo, layout.pickup_model_data_source)
        self.pickup_data_source_combo.setEnabled(layout.pickup_model_style != PickupModelStyle.ALL_VISIBLE)
