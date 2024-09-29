"""
COPYRIGHT: University of Sunshine Coast 2024

AUTHOR: Joseph Thurlow <joseph.thurlow@protonmail.com>
"""

import os
import sys
from importlib import metadata

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QLabel, QWidget
from PySide6.QtCore import QSettings, QSize

from panels import SettingsPanel, FilePreviewPanel
from components import StyleTheme, StylerMixin,Widget
from components.settings import Settings


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


template_styles = {
    "border": {
        "border": "1px solid #636363",
        "border-radius": "5px",
        "padding": "5px",
    },
    "border-focus": {
        "border": "1px solid #333",
    },
    "button": {
        "padding": "4px",
        "border": "1px solid #636363",
        "border-radius": "5px",
        "background-color": "#636363",
    },
    "button-hover": {
        "background-color": "#ff0099",
    },
    "primary-background" : {
        "background-color": "#c4c4c4"
    },
    "list-item-selected" : {
        "background-color": "#ff0099",
        "border": "1px solid #ff0099",
        "border-radius": "5px",
    },
    "list-item-hover" : {
        "background-color": "#ff0099",
        "border": "1px solid #ff0099",
        "border-radius": "5px",
    },
    "primary-colour": {
        "color": "#ff0099"
    },
    "checkbox": {
        "color": "#c4c4c4",
        "background-color": "transparent",
        "border": "1px solid #262626",
        "font-size": "12px",
        "font-weight": "normal",
        "margin": "3px 0px 3px 0px",
    },
        "scrollbar": {
        "border": "1px solid grey",
        "border-radius": "5px",
        "background": "#1a1a1a",
        "margin": "0px 0px 0px 0px",
    },
    "hor-scrollbar": {
        "height": "10px",
    },
    "vert-scrollbar": {
        "width": "10px",
    },
    "scrollbar-thumb": {
        "background": "#2b2b2b",
        "border-radius": "5px",
    },
    "scrollbar-add-line": {
        "background": "none",
        "width": "0px",
        "height": "0px",
        "subcontrol-position": "bottom",
        "subcontrol-origin": "margin",
    },
    "scrollbar-sub-line": {
        "background": "none",
        "width": "0px",
        "height": "0px",
        "subcontrol-position": "top",
        "subcontrol-origin": "margin",
    },
    "label": {
        "background-color": "transparent",
        "font-size": "12px",
        "font-weight": "normal",
        "margin": "0px 0px 6px 0px",
    }
}

asset_paths = {
    "prawn": r"assets\prawn\prawn.png",
    "folder": r"assets\folder.png",
}

settings = {
    "file_match_pattern" : [r"*.mp4", r"*.avi", r"*.mov", r"*.jpg", r"*.jpeg", r"*.png", r"*.gif"],
}


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
        self.setWindowTitle(f"SeaingClearly - Workbench v{__version__}")
        self.setMinimumWidth(600)
        self.setMinimumHeight(800)
        self.setGeometry(0, 0, 1000, 800)
        self.setContentsMargins(0, 0, 0, 0)

        icon = QIcon(r"assets\prawn\prawn.png")
        self.setWindowIcon(icon)

        self._setupLayout()

        self.loadSettings()


    def _setupLayout(self): 
        central_widget = Widget(name="centralwidget", style_sheet={"QWidget#centralwidget": "background-color: #262626; color: #c4c4c4;"})

        hori_layout = QHBoxLayout()
        hori_layout.setContentsMargins(0, 0, 0, 0)
        
        self.left_settings_panel = SettingsPanel()
        self.left_preview_panel = FilePreviewPanel()
        self.label = QLabel("Hello World")

        hori_layout.addWidget(self.left_preview_panel)
        hori_layout.addWidget(self.label)

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
    