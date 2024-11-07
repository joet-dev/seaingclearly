"""
COPYRIGHT: University of Sunshine Coast 2024

AUTHOR: Joseph Thurlow <joseph.thurlow@protonmail.com>
"""

import os
import sys
import logging
from importlib import metadata

from PySide6.QtGui import QIcon, QImage
from PySide6.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QVBoxLayout, QSizePolicy, QSplitter, QMessageBox
from PySide6.QtCore import QSettings, QSize, Qt

from panels import SettingsPanel, FileSelectionPanel, FilePreviewPanel
from components import StyleTheme, StylerMixin,Widget
from components.settings import Settings
from config import template_styles, asset_paths, settings, colours
from iot.service import SeaingService


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

API_HOST = os.environ.get("API_HOST")

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
        
        self.api_service = SeaingService()
        
        # TODO: UNCOMMENT
        try: 
            self.api_service.authenticate()
        except Exception as e:
            diag = QMessageBox()
            diag.setWindowTitle("SeaingClearly - Error")
            diag.setIcon(QMessageBox.Critical)
            diag.setText(str(e))
            diag.exec()
            sys.exit(1)

        self.options = self.api_service.getOptions()

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
        vert_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        vert_layout = QVBoxLayout(vert_container)
        vert_layout.setContentsMargins(0, 0, 0, 0)
        
        self.file_selection_panel = FileSelectionPanel()
        self.file_selection_panel.fileSelected.connect(self.onFileSelected)
        self.settings_panel = SettingsPanel(options=self.options)
        self.settings_panel.settingsChanged.connect(self.onSettingsChanged)
        self.settings_panel.triggerSettingsChanged()

        self.preview_panel = FilePreviewPanel(api_service=self.api_service)

        vert_layout.addWidget(self.file_selection_panel)
        vert_layout.addWidget(self.settings_panel)

        h_divider = QSplitter()
        h_divider.setStyleSheet(f"QSplitter::handle {{ background-color: {colours['border']}; }}")
        h_divider.setHandleWidth(3)
        h_divider.setOrientation(Qt.Horizontal)
        h_divider.addWidget(vert_container)
        h_divider.addWidget(self.preview_panel)
        h_divider.setCollapsible(0, False)
        h_divider.setCollapsible(1, False)

        hori_layout.addWidget(h_divider)

        central_widget.setLayout(hori_layout)
        self.setCentralWidget(central_widget)

    def onFileSelected(self, file_path:str, image:QImage):
        self.preview_panel.setPreview(file_path, image)

    def onSettingsChanged(self, options:dict):
        self.api_service.setConfig(options)

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
    
    # Setup Logger
    log_path = "./logs"
    log_file = "seaingclearly.log"

    os.makedirs(log_path, exist_ok=True)
    log_full_path = os.path.join(log_path, log_file)

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_full_path)
        ]
    )
    # logging.getLogger("urllib3").setLevel(logging.WARNING)

    app = QApplication(sys.argv)

    Settings(settings=settings)
    StyleTheme(boiler=template_styles, paths=asset_paths)

    window = SeaingClearly()
    window.show()
    
    sys.exit(app.exec())

