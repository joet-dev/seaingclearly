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
    QStackedWidget,
    QWidget,
)

from PySide6.QtCore import QObject, QRunnable, Signal, Slot, QThreadPool, QTimer, Qt
from PySide6.QtGui import QImage

from components.widgets import (
    ImageLoaderManager,
    ImagePreview,
)


class FileSelectionPanel(Widget):
    fileSelected = Signal(str, QImage)    
    
    def __init__(self):
        super().__init__(name="fileselectionpanel")
        self._setupLayout()

    def _setupLayout(self):
        self.setContentsMargins(10, 10, 10, 10)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)


        self.file_preview_path = PathLineEdit(
            "filepreviewpath",
            title=None,
            placeholder="Enter the video or image directory",
        )
        self.file_preview_path.pathChanged.connect(self._onPathChanged)
        self.stacked_widget = QStackedWidget()

        self.file_preview_list = FileSelectionList()
        self.file_preview_list.currentItemChanged.connect(self._onFileChanged)
        self.file_preview_list.error.connect(self.displayError)

        self.error_element = ErrorElement()

        self.stacked_widget.addWidget(self.file_preview_list)
        self.stacked_widget.addWidget(self.error_element)

        main_layout.addWidget(self.file_preview_path)
        main_layout.addWidget(self.stacked_widget)

        self.setLayout(main_layout)

        # TODO Comment out
        self.file_preview_path.line_edit.setText(
            r"D:\Programming\_UNI\SEAING-CLEARLY\datasets\Underwater Marine Species.v6-marinedataset_v5.yolov8\test\images"
        )

    def _onPathChanged(self, response: ValidationResponse):
        self.file_preview_list.clear()

        if response.error is not None:
            self.displayError(response.error)
            return
        
        self.stacked_widget.setCurrentWidget(self.file_preview_list)

        self.file_preview_list.setDirectory(response.text)

    @Slot()
    def _onFileChanged(self, list_item: QListWidgetItem):
        if list_item is None:
            return 
        
        widget:FileSelectionListItem = self.file_preview_list.itemWidget(list_item)
        self.fileSelected.emit(widget.path, widget.image_preview.image)

    def displayError(self, error_message: str):
        self.error_element.setError(error_message)
        self.stacked_widget.setCurrentWidget(self.error_element)


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
        file_list: list[str] = []
        for filename in os.listdir(self.path):
            full_path = os.path.join(self.path, filename)
            if os.path.isfile(full_path) and any(
                fnmatch.fnmatch(filename, pattern)
                for pattern in self.file_match_patterns
            ):
                file_list.append(full_path)

        self.signals.finished.emit(file_list)


class ErrorElement(Widget):
    def __init__(self): 
        super().__init__(name="error", theme_classes=["QWidget#error|border"])

        vert_layout = QVBoxLayout() 

        self.error_label = Label("Error", name="errorlbl", theme_classes=["QLabel#errorlbl|label-header"])

        self.error_label.setAlignment(Qt.AlignCenter)

        vert_layout.addStretch()
        vert_layout.addWidget(self.error_label)
        vert_layout.addStretch()

        self.setLayout(vert_layout)

    def setError(self, error_message:str):
        self.error_label.setText(error_message) 


class FileSelectionList(StylerMixin, QListWidget):
    error = Signal(str)

    def __init__(self):
        super().__init__(
            name="filepreviewlist",
            theme_classes=[
                "QListWidget#filepreviewlist|border",
                "QListWidget#filepreviewlist::item:selected|ele-selected",
                "QListWidget#filepreviewlist::item:hover|ele-hover",
            ],
        )
        self.file_match_patterns = Settings().getSetting("file_match_pattern")
        
        self.setSelectionMode(QListWidget.SingleSelection)

        self.image_loader_manager = ImageLoaderManager()
        self.thread_pool = QThreadPool()
        self.file_path_list = []

        self.start = 0
        self.end = 0
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
        if len(files) == 0: 
            self.error.emit("No supported files found in the directory")
            return 
        
        self.file_path_list = files
        self.start = 0
        self.end = 0

        self._enqueueItems()
        self.verticalScrollBar().setValue(0) 

    def _createItem(self, file_path: str):
        worker = self.image_loader_manager.getImageWorker(file_path)
        item = FileSelectionListItem(file_path, worker)
        list_item = QListWidgetItem()
        list_item.setSizeHint(item.sizeHint())

        return list_item, item

    def _enqueueItems(self, count:int = 2, reverse: bool = False):
        if self.loading:
            return

        self.loading = True

        if self.start == 0 and self.end == 0:
            add_start = 0
            add_end = min(self.view_range, len(self.file_path_list))
            self.end = add_end
            increment = 1

        else:
            if reverse:
                if self.start <= 0:
                    self.loading = False
                    return

                add_start = self.start - 1
                self.start = max(0, self.start - count)
                add_end = self.start - 1

                if self.end - self.start >= self.view_range + 1:
                    self.end -= count

                if add_end == 0:
                    add_end = -1
                    self.start = -1

                increment = -1

            else:
                if self.end >= len(self.file_path_list):
                    self.loading = False
                    return

                if self.end == -1:
                    self.end = 0

                add_start = self.end
                self.end = min(
                    self.end + count, len(self.file_path_list)
                )
                add_end = self.end

                if self.end - self.start >= self.view_range + 1:
                    self.start += count

                increment = 1

        for i in range(add_start, add_end, increment):
            file_path = self.file_path_list[i]
            
            list_item, item = self._createItem(file_path)

            if reverse:
                self.insertItem(0, list_item)
                if self.count() > self.view_range:
                    self.takeItem(self.view_range)
            else:
                self.addItem(list_item)
                if self.count() > self.view_range:
                    self.takeItem(0)

            self.setItemWidget(list_item, item)
        
        scroll_pos = self.verticalScrollBar().minimum() if reverse else self.verticalScrollBar().maximum() - 1
        self.verticalScrollBar().setValue(scroll_pos + -increment)
        self.image_loader_manager.loadAll()

        self.loading = False

    def wheelEvent(self, event):
        super().wheelEvent(event)

        self.scroll_timer.start(25)

    def getSelectedPosition(self): 
        selected_items = self.selectedItems()

        if not selected_items:
            self.setCurrentRow(0)
            return 0
        
        selected_item = selected_items[0]

        return self.row(selected_item)

    def keyPressEvent(self, event):
        super().keyPressEvent(event)

        if event.key() == Qt.Key_Up:
            if self.getSelectedPosition() < 3:
                self._enqueueItems(count=1, reverse=True)
        elif event.key() == Qt.Key_Down:
            if self.getSelectedPosition() > self.count() - 3:
                self._enqueueItems(count=1)

    def _onScroll(self):
        scroll_bar = self.verticalScrollBar()
        value = scroll_bar.value()
        if value == scroll_bar.maximum():
            self._enqueueItems() 
        elif value == scroll_bar.minimum():
            self._enqueueItems(reverse=True)



class FileSelectionListItem(StylerMixin, QWidget):
    def __init__(self, file_path: str, image_loader, parent=None):
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

        self.image_preview = ImagePreview(preview_size=80, image_loader=self.image_loader)
        main_layout.addWidget(self.image_preview)

        v_layout = QVBoxLayout()
        v_layout.setContentsMargins(0, 0, 0, 0)

        max_chars = 50
        full_text = os.path.basename(self.path)
        display_text = (
            full_text if len(full_text) <= max_chars else full_text[:max_chars] + "..."
        )
        relative_path_label = Label(
            display_text,
            name="pathlbl",
            theme_classes=["QLabel#pathlbl|label-header"],
        )
        relative_path_label.setToolTip(full_text)
        v_layout.addWidget(relative_path_label)

        file_size_str = getFileSize(self.path)
        file_size_label = Label(
            file_size_str, name="sizelbl", theme_classes=["QLabel#sizelbl|label-sub"]
        )
        v_layout.addWidget(file_size_label)

        main_layout.addLayout(v_layout)

        self.setLayout(main_layout)
