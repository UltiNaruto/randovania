from __future__ import annotations

from randovania.games.game import RandovaniaGame
from randovania.gui.generated.games_tab_pseudoregalia_widget_ui import Ui_PseudoregaliaGameTabWidget
from randovania.gui.widgets.base_game_tab_widget import BaseGameTabWidget


class PseudoregaliaGameTabWidget(BaseGameTabWidget, Ui_PseudoregaliaGameTabWidget):
    def setup_ui(self) -> None:
        self.setupUi(self)

    @classmethod
    def game(cls) -> RandovaniaGame:
        return RandovaniaGame.PSEUDOREGALIA