import logging
from typing import Optional

import cv2
from numpy import dtype, frombuffer, ndarray, uint8
from PySide6.QtCore import QBuffer, QByteArray, QObject, Qt, QThread, Signal, Slot
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QLabel

from seaingclearly.iot.service import SeaingService


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


class EnhancedImageLoaderWorker(QObject):
    load_image = Signal(str, SeaingService)

    def __init__(self):
        super().__init__()
        self.signals = WorkerSignals()

        self.load_image.connect(self.loadImage)

    @Slot(str, SeaingService)
    def loadImage(self, path:str, api_service: SeaingService):
        self.signals.image_loaded.emit(None)
        image = cv2.imread(path)
        _, img_encoded = cv2.imencode('.jpg', image) 
        image_bytes = img_encoded.tobytes()

        enhanced_image_bytes = api_service.enhanceImage(image_bytes)
        byte_array = QByteArray(enhanced_image_bytes)
        buffer = QBuffer(byte_array)
        buffer.open(QBuffer.ReadOnly)

        qimage = QImage()
        qimage.loadFromData(byte_array)

        self.signals.image_loaded.emit(qimage)

    def _qimageToNumpy(self, image: QImage) -> ndarray[any, dtype[uint8]]:    
        buffer = image.bits().tobytes()
    
        return frombuffer(buffer, dtype=uint8).reshape(image.height(), image.width(), 4)


class ImagePreview(QLabel):
    def __init__(self, image_loader:ImageLoaderWorker = None, preview_size: int = None, parent=None):
        super().__init__(parent)
        self.preview_size = preview_size
        self.image = None
        
        if preview_size:
            self.setFixedSize(preview_size, preview_size)
            
        self.setScaledContents(False)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("QLabel { background-color: #222; }")

        if image_loader:
            image_loader.signals.image_loaded.connect(self._onImageLoaded)

    @Slot(QImage)
    def _onImageLoaded(self, image: QImage) -> None:
        self.loadImage(image)

    def loadImage(self, image: QImage):
        self.image = image
        self.updatePixmap()

    def resizeEvent(self, event):
            self.updatePixmap()
            super().resizeEvent(event)

    def updatePixmap(self):
        if self.image:
            pixmap = QPixmap.fromImage(self.image)
            scaled_pixmap = pixmap.scaled(
                self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.setPixmap(scaled_pixmap)
        else:
            self.setPixmap(QPixmap())


