from components.widgets import ImagePreview, EnhancedImageLoaderWorker
from components import Widget
from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QSizePolicy, 
    QLabel
)

from PySide6.QtGui import QImage, Qt
from PySide6.QtCore import QThread


from seaingclearly.iot.service import SeaingService


class FilePreviewPanel(Widget):
    def __init__(self, api_service: SeaingService):
        super().__init__(name="filepreviewpanel")
        self._setupLayout()

        self.api_service: SeaingService = api_service

        self.thread:QThread = QThread()
        self.enhanced_image_worker = EnhancedImageLoaderWorker()
        self.enhanced_image_worker.moveToThread(self.thread)
        self.enhanced_image_worker.signals.image_loaded.connect(self.setEnhancedPreview)
        self.thread.start()

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
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def setPreview(self, path:str, image: QImage): 
        self.current_img = image
        self.current_path = path

        if self.current_img is None:
            return
        
        self.original_view.loadImage(image)
        
        # TODO: LOAD ENHANCED IMAGE IS NOT THREADED
        self.enhanced_image_worker.loadImage(path=path, api_service=self.api_service)
        

    def setEnhancedPreview(self, enhanced_image: QImage):
        self.enhanced_view.loadImage(enhanced_image)

