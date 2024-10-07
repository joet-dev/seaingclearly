import logging
from typing import Optional

import cv2
from PySide6.QtCore import (
    QObject,
    Qt,
    Signal,
    Slot,
    QThread
)
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QLabel

logging.basicConfig(level=logging.DEBUG)



class WorkerSignals(QObject):
    image_loaded = Signal(QImage)

class ImageLoaderWorker(QObject):
    def __init__(self, path: str):
        super().__init__()
        self.path = path
        self.signals = WorkerSignals()

    def loadImage(self):
        image = self._loadPreviewImage(self.path)
        self.signals.image_loaded.emit(image)

    def _loadPreviewImage(self, content_path: str) -> QImage:
        if content_path.lower().endswith((".png", ".jpg", ".jpeg", ".gif")):
            return QImage(content_path)
        elif content_path.lower().endswith((".mp4", ".avi", ".mov")):
            return QImage.fromData(self._extractFrameFromVideo(content_path))
        return None

    def _readImageAsBytes(self,image_path: str) -> Optional[bytes]:
        image = cv2.imread(image_path)
        if image is None:
            logging.error(f"Failed to read image file: {image_path}")
            return None
        _, buffer = cv2.imencode(".png", image)
        return buffer.tobytes()

    def _extractFrameFromVideo(self, video_path: str) -> Optional[bytes]:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            logging.error(f"Failed to open video file: {video_path}")
            return None

        ret, frame = cap.read()
        cap.release()

        if not ret:
            logging.error(f"Failed to read frame from video file: {video_path}")
            return None

        _, buffer = cv2.imencode(".png", frame)
        return buffer.tobytes()


class ManagerSignals(QObject):
    request_img_load = Signal()

class ImageLoaderManager(QObject): 
    def __init__(self):
        super().__init__()
        
        self.bg_thread = QThread()
        self.bg_thread.start()

        self.signals = ManagerSignals()

    def getImageWorker(self, file_path:str) -> ImageLoaderWorker:
        loader = ImageLoaderWorker(file_path)
        self.signals.request_img_load.connect(loader.loadImage)
        loader.moveToThread(self.bg_thread)

        return loader

    def loadAll(self): 
        self.signals.request_img_load.emit()
        self.signals.request_img_load.disconnect()
    
    def __del__(self):
        self.bg_thread.quit()


class ImagePreview(QLabel):
    def __init__(self, image_loader:ImageLoaderWorker, preview_size: int = 80, parent=None):
        super().__init__(parent)
        self.preview_size = preview_size
        self.image = None
        
        self.setFixedSize(preview_size, preview_size)
        self.setScaledContents(False)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("QLabel { background-color: #222; }")

        image_loader.signals.image_loaded.connect(self._onImageLoaded)

    @Slot(QImage)
    def _onImageLoaded(self, image: QImage) -> None:
        self.image = image

        if image:
            pixmap = QPixmap.fromImage(image)
            scaled_pixmap = pixmap.scaled(
                self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.setPixmap(scaled_pixmap)

        else: 
            image = None
