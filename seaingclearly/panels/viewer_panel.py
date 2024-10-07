from components.widgets import ImagePreview
from components import Widget
from PySide6.QtWidgets import (
    QVBoxLayout,
)

from PySide6.QtGui import QImage



class FilePreviewPanel(Widget):
    def __init__(self):
        super().__init__(name="filepreviewpanel")
        self._setupLayout()

        self.current_path = None
        self.current_img:QImage = None

    def _setupLayout(self):
        self.setContentsMargins(10, 10, 10, 10)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.original_view:ImagePreview = ImagePreview()
        self.enhanced_view:ImagePreview = ImagePreview()

        main_layout.addWidget(self.original_view)
        main_layout.addWidget(self.enhanced_view)

        self.setLayout(main_layout)

    def setPreview(self, path:str, image: QImage): 
        self.current_img = image
        self.current_path = path

        if self.current_img is None:
            return
        
        self.original_view.loadImage(image)
        self.enhanced_view.loadImage(image)