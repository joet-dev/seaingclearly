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

        self.dash = BoolDashboard(
            "enhancement",
            "Enhancements",
            {
                "white_balance": {"lbl": "White Balance Correction", "tt": "Applies white balance correction to the image by adjusting color channels in the LAB color space, neutralizing color casts for a more balanced appearance."},
                "super_res": {"lbl": "Super Resolution Upscaling", "tt": "Applies super-resolution to upscale the image using the EDSR model, increasing the image size by 4x for enhanced detail and resolution."},
                "richard_lucy": {"lbl": "Richardson-Lucy Deconvolution", "tt": "Applies Richardson-Lucy deconvolution to each color channel of the upscaled image to reduce blur and restore finer details, using a 5x5 point spread function and 30 iterations."},
                "adaptive_hist_eq": {"lbl": "Adaptive Histogram Equalization", "tt": "Enhances local contrast in the deconvolved image by applying adaptive histogram equalization to each color channel, improving detail in both bright and dark areas while limiting noise with a clip limit of 0.01."},
            },
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
