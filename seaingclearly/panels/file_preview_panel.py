import fnmatch
import os
from typing import List

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

from PySide6.QtCore import QObject, QRunnable, Signal, Slot, QThreadPool, QTimer

from components.widgets import (
    ImageLoaderManager,
    ImagePreview,
)
from config import colours

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


class DirectorySearchWorker(QRunnable):
    class Signals(QObject):
        finished = Signal(list)

    def __init__(self, path: str, file_match_patterns: List[str], batch_size: int = 50):
        super().__init__()
        self.path = path
        self.file_match_patterns = file_match_patterns
        self.batch_size = batch_size
        self.signals = self.Signals()

    @Slot()
    def run(self):
        file_list:list[str] = []
        for filename in os.listdir(self.path):
            full_path = os.path.join(self.path, filename)
            if os.path.isfile(full_path) and any(
                fnmatch.fnmatch(filename, pattern)
                for pattern in self.file_match_patterns
            ):
                file_list.append(full_path)
                
        self.signals.finished.emit(file_list)


class FilePreviewList(StylerMixin, QListWidget):
    def __init__(self):
        super().__init__(
            name="filepreviewlist", theme_classes=["QListWidget#filepreviewlist|border", "QListWidget#filepreviewlist::item:selected|ele-selected", "QListWidget#filepreviewlist::item:hover|ele-hover"]
        )
        self.file_match_patterns = Settings().getSetting("file_match_pattern")
        
        self.image_loader_manager = ImageLoaderManager()
        self.thread_pool = QThreadPool()
        self.file_path_list = []

        self.start = 0
        self.end = 0


        self.batch_len_limit = 2
        self.view_range = 20

        self.loading = False

        self.scroll_timer = QTimer()
        self.scroll_timer.setSingleShot(True)
        self.scroll_timer.timeout.connect(self._onScroll)

    def setDirectory(self, path: str):
        self.current_dir = path
        self.file_path_list = []

        worker = DirectorySearchWorker(path, self.file_match_patterns)
        worker.signals.finished.connect(self._setFiles)
        self.thread_pool.start(worker)

    @Slot(list)
    def _setFiles(self, files: List[str]):
        self.file_path_list = files

        self._enqueueItems()

    # BUG duplicates on the turn around 
    def _enqueueItems(self, reverse: bool = False):
        if self.loading:
            return
                
        self.loading = True

        if self.start == 0 and self.end == 0:
            add_start = 0
            add_end = self.view_range
            self.end = self.view_range
            increment = 1

        else: 
            if reverse: 
                if self.start <= 0: 
                    self.loading = False 
                    return 
                    
                add_start = self.start
                self.start = max(-1, self.start - self.batch_len_limit)
                add_end = self.start

                if self.end - self.start >=  self.view_range + 1:
                    self.end -= self.batch_len_limit

                if add_end == 0: 
                    add_end = -1

                increment = -1

            else: 
                if self.end >= len(self.file_path_list):
                    self.loading = False
                    return
                
                if self.end == -1: 
                    self.end = 0

                add_start = self.end
                self.end = min(self.end + self.batch_len_limit, len(self.file_path_list))
                add_end = self.end

                if self.end - self.start >=  self.view_range + 1:
                    self.start += self.batch_len_limit

                increment = 1

        for i in range(add_start, add_end, increment):
            file_path = self.file_path_list[i]
            worker = self.image_loader_manager.getImageWorker(file_path)
            item = FilePreviewListItem(file_path, worker)
            list_item = QListWidgetItem()
            list_item.setSizeHint(item.sizeHint())

            if reverse:
                self.insertItem(0, list_item)
                if self.count() > self.view_range:
                    self.takeItem(self.view_range)
            else:
                self.addItem(list_item)
                if self.count() > self.view_range:
                    self.takeItem(0)

            self.setItemWidget(list_item, item)

        print("Current Range:", self.count(), f"{self.start} - {self.end}", f"| {add_start} - {add_end}", increment)
        self.image_loader_manager.loadAll()

        self.loading = False
        
    def wheelEvent(self, event):
        super().wheelEvent(event)

        self.scroll_timer.start(25)

    def _onScroll(self):
        if self.loading:
            return 
        
        scroll_bar = self.verticalScrollBar()
        value = scroll_bar.value()
        if value == scroll_bar.maximum():
            self._enqueueItems()
        elif value == scroll_bar.minimum():
            self._enqueueItems(reverse=True)
        
class FilePreviewListItem(StylerMixin, QWidget):
    def __init__(self, file_path:str, image_loader, parent=None):
        super().__init__(
            name="filepreviewitem",
            parent=parent,
            theme_classes=["#filepreviewitem|border"],
        )
        self.path = file_path
        self.image_loader = image_loader

        self._setupLayout()

    def _setupLayout(self) -> None:
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(3, 3, 3, 3)

        self.image_preview = ImagePreview(image_loader=self.image_loader)
        main_layout.addWidget(self.image_preview)

        v_layout = QVBoxLayout()
        v_layout.setContentsMargins(0, 0, 0, 0)
                
        relative_path_label = Label(os.path.basename(self.path), name="pathlbl", theme_classes=["QLabel#pathlbl|label-header"])
        v_layout.addWidget(relative_path_label)

        file_size_str = getFileSize(self.path)
        file_size_label = Label(file_size_str, name="sizelbl", theme_classes=["QLabel#sizelbl|label-sub"])
        v_layout.addWidget(file_size_label)

        main_layout.addLayout(v_layout)

        self.setLayout(main_layout)
        




