"""Navigation laterale."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QButtonGroup, QFrame, QLabel, QPushButton, QVBoxLayout


class Sidebar(QFrame):
    page_requested = Signal(str)
    theme_toggle_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("sidebar")
        self.setFixedWidth(225)

        layout = QVBoxLayout(self)
        logo = QLabel("♫  JONATHAN")
        logo.setObjectName("logo")
        layout.addWidget(logo)
        layout.addSpacing(16)
        self._button_group = QButtonGroup(self)
        self._button_group.setExclusive(True)
        self._page_buttons: dict[str, QPushButton] = {}

        for label, page in (
            ("⌂   Accueil", "home"),
            ("♫   En lecture", "now_playing"),
            ("♫   Bibliothèque", "library"),
            ("▦   Albums", "albums"),
            ("♙   Artistes", "artists"),
            ("≡   File de lecture", "queue"),
        ):
            button = QPushButton(label)
            button.setObjectName("navigationButton")
            button.setCheckable(True)
            button.clicked.connect(
                lambda checked=False, target=page: self.page_requested.emit(target)
            )
            self._button_group.addButton(button)
            layout.addWidget(button)
            self._page_buttons[page] = button

        layout.addStretch()
        self.theme_button = QPushButton()
        self.theme_button.setObjectName("themeToggleButton")
        self.theme_button.clicked.connect(self.theme_toggle_requested.emit)
        layout.addWidget(self.theme_button)

        self.set_active_page("library")
        self.set_theme("dark")

    def set_active_page(self, page: str) -> None:
        button = self._page_buttons.get(page)
        if button is not None:
            button.setChecked(True)

    def set_theme(self, theme: str) -> None:
        if theme == "light":
            self.theme_button.setText("☾  Passer au mode sombre")
            self.theme_button.setAccessibleName("Passer au mode sombre")
        else:
            self.theme_button.setText("☀  Passer au mode clair")
            self.theme_button.setAccessibleName("Passer au mode clair")
