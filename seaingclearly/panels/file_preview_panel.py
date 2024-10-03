import fnmatch
import os
from typing import Optional

import cv2
from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QLabel, QListWidgetItem, QHBoxLayout
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt, QObject, Signal, Slot, QThread

from components import Widget, StylerMixin, PathLineEdit
from components.validators import ValidationResponse
from components.settings import Settings
from components.common import Label
from components.util import getFileSize

from seaingclearly.config import colours


class FilePreviewPanel(QWidget):
    def __init__(self):
        super().__init__()
        self._setupLayout()

    def _setupLayout(self):
        self.setContentsMargins(0, 0, 0, 0)
        # self.setMaximumWidth(400)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0,0,0,0)

        main_widget = Widget(
            name="filepreviewpanel",
            parent=self,
            style_sheet={"QWidget#filepreviewpanel": {"border-right": f"3px solid {colours['border']}", "padding": "10px"}},
        )
        virt_layout = QVBoxLayout()

        self.file_preview_path = PathLineEdit(
            "filepreviewpath",
            title=None,
            placeholder="Enter the video or image directory",
        )
        self.file_preview_path.pathChanged.connect(self._onPathChanged)

        self.file_preview_list = FilePreviewList()

        virt_layout.addWidget(self.file_preview_path)
        virt_layout.addWidget(self.file_preview_list)

        main_widget.setLayout(virt_layout)
        main_layout.addWidget(main_widget)

        self.setLayout(main_layout)

        # TODO Comment out
        self.file_preview_path.line_edit.setText(
            r"C:\Users\JosephThurlow\OneDrive\Pictures\Facebook"
        )

    def _onPathChanged(self, response: ValidationResponse):
        self.file_preview_list.clear()

        if response.error is not None:
            # show error
            return

        self.file_preview_list.setDirectory(response.text)


class FilePreviewList(StylerMixin, QListWidget):
    def __init__(self):
        super().__init__(
            name="filepreviewlist", theme_classes=["QListWidget#filepreviewlist|border", "QListWidget#filepreviewlist::item:selected|ele-selected", "QListWidget#filepreviewlist::item:hover|ele-hover"]
        )
        self.file_match_patterns = Settings().getSetting("file_match_pattern")

    def setDirectory(self, path: str):
        self.currentDir = path

        rel_file_paths: list = self._searchDirectory(path)

        for rel_file_path in rel_file_paths:
            self._addItem(rel_file_path)

    def _addItem(self, rel_file_path: str):        
        item = QListWidgetItem(self)
        widget = FilePreviewListItem(self.currentDir, rel_file_path)
        item.setSizeHint(widget.sizeHint())
        self.addItem(item)
        self.setItemWidget(item, widget)

    def _searchDirectory(self, path: str) -> list[str]:
        matches: list[str] = []

        for filename in os.listdir(path):
            full_path = os.path.join(path, filename)
            if os.path.isfile(full_path) and any(
                fnmatch.fnmatch(filename, pattern)
                for pattern in self.file_match_patterns
            ):
                relative_path = full_path.removeprefix(f"{path}\\").replace("\\", "/")
                matches.append(relative_path)
        
        return matches


class FilePreviewListItem(StylerMixin, QWidget):
    def __init__(self, base_path: str, rel_path: str, parent=None):
        super().__init__(
            name="filepreviewitem",
            parent=parent,
            theme_classes=["#filepreviewitem|border"],
        )
        self.path = os.path.join(base_path, rel_path)
        self.rel_path = rel_path

        print("PATH:", self.path)
        self._setupLayout()

    def _setupLayout(self) -> None:
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(3, 3, 3, 3)

        self.image_preview = ImagePreview(self.path)
        main_layout.addWidget(self.image_preview)

        v_layout = QVBoxLayout()
        v_layout.setContentsMargins(0, 0, 0, 0)
                
        relative_path_label = Label(self.rel_path, name="pathlbl", theme_classes=["QLabel#pathlbl|label-header"])
        v_layout.addWidget(relative_path_label)

        file_size_str = getFileSize(self.path)
        file_size_label = Label(file_size_str, name="sizelbl", theme_classes=["QLabel#sizelbl|label-sub"])
        v_layout.addWidget(file_size_label)

        main_layout.addLayout(v_layout)

        self.setLayout(main_layout)
        
class ImagePreview(QLabel):
    def __init__(self, image_path: str, preview_size: int = 80, parent=None):
        super().__init__(parent)
        self.preview_size = preview_size
        self.path = image_path

        self.setFixedSize(preview_size, preview_size)
        self.setScaledContents(False)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("QLabel { background-color: #222; }")

        self._loadImageInThread()

    def _loadImageInThread(self) -> None:
        self.thread:QThread = QThread()
        self.worker = ImageLoaderWorker(self.path, self.preview_size)
        self.worker.moveToThread(self.thread)
        self.worker.imageLoaded.connect(self._onImageLoaded)
        self.thread.started.connect(self.worker.loadImage)
        self.thread.start()

    @Slot(QPixmap)
    def _onImageLoaded(self, pixmap: QPixmap) -> None:
        if pixmap is not None:
            scaled_pixmap = pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.setPixmap(scaled_pixmap)

        self.thread.quit()
        self.thread.wait()
        self.worker.deleteLater()
        self.thread.deleteLater()


class ImageLoaderWorker(QObject):
    imageLoaded = Signal(QPixmap)

    def __init__(self, path: str, preview_size: int):
        super().__init__()
        self.path = path
        self.preview_size = preview_size

    @Slot()
    def loadImage(self) -> None:
        pixmap = self._loadPreviewImage(self.path)

        self.imageLoaded.emit(pixmap)

    def _loadPreviewImage(self, content_path: str) -> QPixmap:
        pixmap = None
        if content_path.lower().endswith((".png", ".jpg", ".jpeg", ".gif")):
            pixmap = QPixmap(content_path)
        elif content_path.lower().endswith((".mp4", ".avi", ".mov")):
            pixmap = self._extractFrameFromVideo(content_path)

        if pixmap.isNull() or pixmap is None:
            return None
        
        return pixmap
        
    def _extractFrameFromVideo(self, video_path: str) -> Optional[QPixmap]:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"Failed to open video file: {video_path}")
            return QPixmap()

        ret, frame = cap.read()
        cap.release()

        if not ret:
            print(f"Failed to read frame from video file: {video_path}")
            return None

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        height, width, channel = frame_rgb.shape
        bytes_per_line = 3 * width
        q_image = QImage(frame_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888)

        pixmap = QPixmap.fromImage(q_image)
        return pixmap

