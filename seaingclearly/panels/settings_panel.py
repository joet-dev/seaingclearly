from PySide6.QtWidgets import QWidget, QCheckBox, QVBoxLayout
from components import Widget


class SettingsPanel(QWidget): 
    def __init__(self): 
        super().__init__()

        self._setupLayout()
        
    def _setupLayout(self):
        self.setContentsMargins(0, 0, 0, 0)        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        main_widget = Widget(name="settingspanel", parent=self, theme_classes=["#settingspanel|primary-background", "QWidget|primary-colour"])
        virt_layout = QVBoxLayout()

        self.chk_box = QCheckBox("Show File Preview")

        virt_layout.addStretch()
        virt_layout.addWidget(self.chk_box)
        virt_layout.addStretch()

        main_widget.setLayout(virt_layout)
        main_layout.addWidget(main_widget)

        self.setLayout(main_layout)


        

