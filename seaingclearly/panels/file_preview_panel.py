import fnmatch
import os
from typing import Tuple

from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QLabel, QListWidgetItem
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

from components import Widget, StylerMixin, PathLineEdit
from components.validators import ValidationResponse
from components.settings import Settings


class FilePreviewPanel(QWidget):
    def __init__(self):
        super().__init__()
        self._setupLayout()

    def _setupLayout(self):
        self.setContentsMargins(0, 0, 0, 0)
        self.setMaximumWidth(400)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        main_widget = Widget(
            name="filepreviewpanel",
            parent=self,
            style_sheet={"QWidget#filepreviewpanel": {"border-right": "1px solid #636363"}},
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
            r"C:\Users\JosephThurlow\OneDrive\Pictures"
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
            name="filepreviewlist", theme_classes=["QListWidget#filepreviewlist|border", "QListWidget#filepreviewlist|primary-background", "QListWidget#filepreviewlist::item:selected|list-item-selected", "QListWidget#filepreviewlist::item:hover|list-item-hover"]
        )
        self.file_match_patterns = Settings().getSetting("file_match_pattern")

    def setDirectory(self, path: str):
        self.currentDir = path

        rel_file_paths: list = self._searchDirectory(path)

        for rel_file_path in rel_file_paths:
            self._addItem(rel_file_path)

    def _addItem(self, rel_file_path: str):
        item = QListWidgetItem(self)
        widget = FilePreviewItem(self.currentDir, rel_file_path)
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


class FilePreviewItem(StylerMixin, QWidget):
    def __init__(self, base_path: str, rel_path: str, parent=None):
        super().__init__(
            name="filepreviewitem",
            parent=parent,
            theme_classes=["#filepreviewitem|border"],
        )
        self.path = os.path.join(base_path, rel_path)
        print(self.path)
        self.rel_path = rel_path
        self._setupLayout()

    def _setupLayout(self):
        layout = QVBoxLayout()

        # File name
        file_name = os.path.basename(self.path)
        file_name_label = QLabel(file_name)
        layout.addWidget(file_name_label)

        relative_path_label = QLabel(self.rel_path)
        layout.addWidget(relative_path_label)

        # Preview image
        preview_label = QLabel()
        preview_pixmap = self._loadPreviewImage(self.path)
        if preview_pixmap:
            preview_label.setPixmap(preview_pixmap)
        layout.addWidget(preview_label)

        self.setLayout(layout)

    def _loadPreviewImage(self, path: str) -> QPixmap:
        if path.lower().endswith((".png", ".jpg", ".jpeg", ".gif")):
            return QPixmap(path).scaled(100, 100, Qt.KeepAspectRatio)
        elif path.lower().endswith((".mp4", ".avi", ".mov")):
            # For simplicity, using a placeholder image for video files
            # You can use a library like OpenCV to extract a frame from the video
            return QPixmap("video_placeholder.png").scaled(100, 100, Qt.KeepAspectRatio)

        return None
