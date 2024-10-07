"""
COPYRIGHT: University of Sunshine Coast 2024

AUTHOR: Joseph Thurlow <joseph.thurlow@protonmail.com>
"""

import os
import sys
from importlib import metadata

from PySide6.QtGui import QIcon, QImage
from PySide6.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QLabel, QVBoxLayout, QSizePolicy, QSplitter
from PySide6.QtCore import QSettings, QSize, Qt

from panels import SettingsPanel, FilePreviewPanel
from components import StyleTheme, StylerMixin,Widget
from components.settings import Settings
from config import template_styles, asset_paths, settings, colours


try:
    __package_name__ = metadata.metadata("seaingclearly")["Name"]
    __version__ = metadata.version("seaingclearly")
except Exception:
    __package_name__ = "seaingclearly"
    __version__ = "N/A"

try:
    from ctypes import windll

    myappid = f"{__package_name__}_v{__version__}"
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass


class SeaingClearly(StylerMixin, QMainWindow): 
    def __init__(self): 
        super().__init__(
            theme_classes=[
                "QScrollBar:horizontal|hor-scrollbar",
                "QScrollBar:vertical|vert-scrollbar",
                "QScrollBar|scrollbar",
                "QScrollBar::handle|scrollbar-thumb",
                "QScrollBar::add-line|scrollbar-add-line",
                "QScrollBar::sub-line|scrollbar-sub-line",
            ]
        )
        self.setWindowTitle(f"SeaingClearly - WorkBench v{__version__}")
        self.setMinimumWidth(600)
        self.setMinimumHeight(800)
        self.setGeometry(0, 0, 1000, 800)
        self.setContentsMargins(0, 0, 0, 0)

        icon = QIcon(r"assets\prawn\prawn.png")
        self.setWindowIcon(icon)

        self._setupLayout()

        self.loadApplicationSettings()

        self.current_settings = None

    def _setupLayout(self): 
        central_widget = Widget(name="centralwidget", parent=self, theme_classes=["QWidget|primary-background", "QWidget|primary-colour"])

        hori_layout = QHBoxLayout()
        hori_layout.setContentsMargins(0, 0, 0, 0)
        
        vert_container = Widget(name="vertcontainer", parent=self)
        vert_container.setMaximumWidth(550)
        vert_container.setMinimumWidth(400)
        vert_layout = QVBoxLayout(vert_container)
        vert_layout.setContentsMargins(0, 0, 0, 0)
        
        self.preview_panel = FilePreviewPanel()
        self.preview_panel.fileSelected.connect(self.onFileSelected)
        self.settings_panel = SettingsPanel()
        self.settings_panel.settingsChanged.connect(self.onSettingsChanged)
        self.label = QLabel("Hello World")

        vert_layout.addWidget(self.preview_panel)
        vert_layout.addWidget(self.settings_panel)

        h_divider = QSplitter()
        h_divider.setStyleSheet(f"QSplitter::handle {{ background-color: {colours['border']}; }}")
        h_divider.setLineWidth(1)
        h_divider.setOrientation(Qt.Horizontal)

        vert_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        h_divider.addWidget(vert_container)
        h_divider.addWidget(self.label)
        h_divider.setCollapsible(0, False)
        h_divider.setCollapsible(1, False)
        hori_layout.addWidget(h_divider)
        hori_layout.addStretch()

        central_widget.setLayout(hori_layout)
        self.setCentralWidget(central_widget)

    def onFileSelected(self, file_path:str, image:QImage):
        self.label.setText(file_path)
        pass

    def onSettingsChanged(self, options:dict):
        self.current_settings = options

    def loadApplicationSettings(self):
        settings = QSettings("USC", __package_name__)
        self.resize(settings.value("windowSize", QSize(1000, 800)))

        window_position = settings.value("windowPosition", None)

        if window_position is not None:
            self.move(window_position)
            return 
        
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

    def closeEvent(self, event):
        settings = QSettings("USC", __package_name__)
        settings.setValue("windowSize", self.size())
        settings.setValue("windowPosition", self.pos())
        super().closeEvent(event)


def main():
    system_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(system_dir)

    app = QApplication(sys.argv)

    Settings(settings=settings)
    StyleTheme(boiler=template_styles, paths=asset_paths)

    window = SeaingClearly()
    window.show()
    
    sys.exit(app.exec())


# if __name__ == '__main__':
#     main()
    