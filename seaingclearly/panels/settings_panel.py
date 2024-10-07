from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Signal, Slot
from components import Widget, BoolDashboard


class SettingsPanel(QWidget):
    settingsChanged = Signal(dict)

    def __init__(self):
        super().__init__()

        self._setupLayout()

    def _setupLayout(self):
        self.setContentsMargins(0, 0, 0, 0)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        main_widget = Widget(
            name="settingspanel",
            parent=self,
            theme_classes=[
                "#settingspanel|primary-background",
                "QWidget|primary-colour",
            ],
        )
        virt_layout = QVBoxLayout()

        dash = BoolDashboard(
            "enhancement",
            "Enhancements",
            {
                "enh_1": {"lbl": "Enhancement 1", "tt": "TEST ENHANCEMENT 1"},
                "enh_2": {"lbl": "Enhancement 2", "tt": "TEST ENHANCEMENT 2"},
                "enh_3": {"lbl": "Enhancement 3", "tt": ""},
            },
        )
        dash.optionsChanged.connect(self.onSettingsChanged)

        virt_layout.addWidget(dash)

        main_widget.setLayout(virt_layout)
        main_layout.addWidget(main_widget)

        self.setLayout(main_layout)

    @Slot()
    def onSettingsChanged(self, options: dict):
        self.settingsChanged.emit(options)
