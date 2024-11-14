from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Signal, Slot
from seaingclearly.components import Widget, BoolDashboard


class SettingsPanel(QWidget):
    settingsChanged = Signal(dict)

    def __init__(self, options:dict):
        super().__init__()

        self.options = options

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

        self.dash = BoolDashboard(
            "enhancement",
            "Enhancements",
            self.options.get("enhancements", {}),
        )
        self.dash.optionsChanged.connect(self.onSettingsChanged)

        virt_layout.addWidget(self.dash)

        main_widget.setLayout(virt_layout)
        main_layout.addWidget(main_widget)

        self.setLayout(main_layout)

    @Slot()
    def onSettingsChanged(self, options: dict):
        self.settingsChanged.emit(options)

    def triggerSettingsChanged(self):
        self.dash.onCheckboxStateChanged()
