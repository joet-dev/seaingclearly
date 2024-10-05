import fnmatch
import os
from typing import Generator

from components import PathLineEdit, StylerMixin, Widget
from components.common import Label
from components.settings import Settings
from components.util import getFileSize
from components.validators import ValidationResponse
from PySide6.QtWidgets import (
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)

from seaingclearly.components.widgets import (
    ImageLoaderManager,
    ImageLoaderWorker,
    ImagePreview,
)
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
            r"D:\Programming\_UNI\SEAING-CLEARLY\datasets\Underwater Marine Species.v6-marinedataset_v5.yolov8\test\images"
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
        
        self.image_loader_manager = ImageLoaderManager()

    def setDirectory(self, path: str):
        self.current_dir = path

        for rel_file_path in self._searchDirectory(path):
            self._addItem(rel_file_path)

        self.image_loader_manager.signals.request_img_load.emit()

    def _addItem(self, rel_file_path: str):        
        item = QListWidgetItem(self)

        image_worker = self.image_loader_manager.getImageWorker(os.path.join(self.current_dir, rel_file_path))
        widget = FilePreviewListItem(self.current_dir, rel_file_path, image_worker)
        item.setSizeHint(widget.sizeHint())
        self.addItem(item)
        self.setItemWidget(item, widget)

    def _searchDirectory(self, path: str) -> Generator[str, None, None]:
        for filename in os.listdir(path):
            full_path = os.path.join(path, filename)
            if os.path.isfile(full_path) and any(
                fnmatch.fnmatch(filename, pattern)
                for pattern in self.file_match_patterns
            ):
                relative_path = full_path.removeprefix(f"{path}\\").replace("\\", "/")
                yield relative_path
        
class FilePreviewListItem(StylerMixin, QWidget):
    def __init__(self, base_path: str, rel_path: str, image_loader:ImageLoaderWorker, parent=None):
        super().__init__(
            name="filepreviewitem",
            parent=parent,
            theme_classes=["#filepreviewitem|border"],
        )
        self.path = os.path.join(base_path, rel_path)
        self.rel_path = rel_path
        self.image_loader = image_loader

        self._setupLayout()

    def _setupLayout(self) -> None:
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(3, 3, 3, 3)

        self.image_preview = ImagePreview(self.path, image_loader=self.image_loader)
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
        




