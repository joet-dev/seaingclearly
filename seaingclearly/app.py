"""
COPYRIGHT: University of Sunshine Coast 2024

AUTHOR: Joseph Thurlow <joseph.thurlow@protonmail.com>
"""

import os
import sys
from importlib import metadata

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QLabel
from PySide6.QtCore import QSettings, QSize

from panels import SettingsPanel, FilePreviewPanel
from components import StyleTheme, StylerMixin,Widget
from components.settings import Settings
from config import template_styles, asset_paths, settings


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

        self.loadSettings()


    def _setupLayout(self): 
        central_widget = Widget(name="centralwidget", parent=self, theme_classes=["QWidget|primary-background", "QWidget|primary-colour"])

        hori_layout = QHBoxLayout()
        hori_layout.setContentsMargins(0, 0, 0, 0)
        
        self.left_settings_panel = SettingsPanel()
        self.left_preview_panel = FilePreviewPanel()
        self.label = QLabel("Hello World")

        hori_layout.addWidget(self.left_preview_panel)
        hori_layout.addWidget(self.label)
        hori_layout.addStretch()

        central_widget.setLayout(hori_layout)
        self.setCentralWidget(central_widget)


    def loadSettings(self):
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
    