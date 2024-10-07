from typing import Callable, Tuple
import os

from PySide6.QtCore import QSize, Signal, Slot
from PySide6.QtGui import QIcon, QPainter
from PySide6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QStyle,
    QStyleOption,
    QWidget,
    QFileDialog,
    QGroupBox,
    QVBoxLayout,
)

from .styler import StylerMixin
from .validators import validate_path, ValidationResponse


class Widget(StylerMixin, QWidget):
    def __init__(
        self,
        name: str,
        parent=None,
        style_sheet: dict = None,
        theme_classes: list[str] = None,
    ):
        super().__init__(
            name=name,
            style_sheet=style_sheet,
            theme_classes=theme_classes,
            parent=parent,
        )

    def paintEvent(self, event):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, p, self)


class Checkbox(StylerMixin, QCheckBox):
    def __init__(self, text: str = "", name: str = None):
        super().__init__(text=text, name=name, theme_classes=["QCheckBox|checkbox"])


class LabelledInput(QWidget):
    def __init__(self, label, parent=None):
        super().__init__(parent)
        self.label = QLabel(label)
        layout = QHBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.input)
        self.setLayout(layout)


class Button(StylerMixin, QPushButton):
    def __init__(
        self,
        name, 
        text:str = "",
        custom_style: dict = None,
        icon: str = None,
    ):
        super().__init__(
            text=text,
            name=name,
            theme_classes=[f"QPushButton#{name}|ele", f"QPushButton#{name}:hover|ele-hover", f"QPushButton#{name}|button"],
        )

        if custom_style is not None:
            self.modifySheet(custom_style)

        if icon:
            self.setIcon(QIcon(self.getIconPath(icon)))
            self.setIconSize(QSize(20, 20))


class LineEdit(StylerMixin, QLineEdit):
    def __init__(
        self, parent=None, custom_style: dict[str, dict[str, str]] = None, name=None
    ):
        super().__init__(
            parent=parent,
            theme_classes=["QLineEdit|border", "QLineEdit:focus|border-focus"],
            name=name,
        )

        if custom_style:
            self.hardModifySheet(custom_style)

        self.validate_func: Callable[[str], Tuple[bool, str]] = None
        self.textChanged.connect(self.reset_border)

    def reset_border(self):
        self.resetSheet()

    def setValidator(self, validation_function: Callable[[str], Tuple[bool, str]]):
        self.validate_func = validation_function

    def textWithValidation(self) -> ValidationResponse:
        if self.validate_func is None:
            return ValidationResponse(self.text(), None)

        text_str: str = self.text()
        is_valid, error_message = self.validate_func(text_str)

        return ValidationResponse(text_str, error_message if not is_valid else None)


class PathLineEdit(QWidget):
    pathChanged = Signal(ValidationResponse)   

    def __init__(
        self,
        name: str = None,
        title: str = "Path:",
        placeholder: str = "Input Path",
        button_text: str = "",
    ):
        super().__init__()

        hlayout = QHBoxLayout()
        hlayout.setContentsMargins(0, 0, 0, 0)

        if title:
            hlayout.addWidget(QLabel(title))

        self.line_edit = LineEdit(self, name=name)
        self.line_edit.setPlaceholderText(placeholder)
        self.line_edit.setValidator(validation_function=validate_path)

        self.line_edit.textChanged.connect(self.triggerChange)

        self.browse_btn = Button(
            name="filebrowse",
            text=button_text,
            icon="folder",
        )
        self.browse_btn.clicked.connect(self.browse)

        hlayout.addWidget(self.line_edit)
        hlayout.addWidget(self.browse_btn)

        self.setLayout(hlayout)

    def triggerChange(self): 
        response:ValidationResponse = self.line_edit.textWithValidation()

        self.pathChanged.emit(response)

    def browse(self):
        folder_path = self.line_edit.text()
        if os.path.exists(folder_path):
            folder_path = os.path.dirname(folder_path)
        else:
            folder_path = os.path.join(os.path.expanduser("~"), "Downloads")
                
        dialog = QFileDialog(
            self, "Select Image/Video Folder", folder_path
        )

        dialog.setFileMode(QFileDialog.Directory)

        if dialog.exec():
            folder_path = dialog.selectedFiles()[0]
            self.line_edit.setText(folder_path)

    def lineEdit(self):
        return self.line_edit
    

class Label(StylerMixin, QLabel):
    def __init__(
        self,
        text: str,
        name: str = None,
        font_size: int = None,
        custom_style: dict = None,
        theme_classes: list[str] = ["QLabel|label"],
    ):
        super().__init__(text=text, name=name, theme_classes=theme_classes)

        if font_size:
            self.hardModifySheet({"QLabel": {"font-size": f"{font_size}px"}})

        if custom_style:
            self.hardModifySheet(custom_style)


class BoolDashboard(StylerMixin, QGroupBox):
    optionsChanged = Signal(dict)

    def __init__(self, name: str, label: str, items: dict):
        super().__init__(
            title=label,
            name=name,
            style_sheet={f"QGroupBox#{name}::title": {"subcontrol-origin": "margin", "subcontrol-position": "top center", "padding-bottom": "5px"}},
            theme_classes=[f"QGroupBox#{name}|border", f"QGroupBox#{name}|group-box"],
        )

        self.group_layout = QVBoxLayout(self)
        self.group_layout.setContentsMargins(5, 5, 5,5)

        for key, value in items.items():
            self.add_checkbox(key, value, True)

    def add_checkbox(self, key: str, value: dict, checked: bool = True):
        label = value.get("lbl", "")
        tooltip = value.get("tt", "")
        
        checkbox = Checkbox(label)
        checkbox.setChecked(checked)
        checkbox.setObjectName(key)
        
        if tooltip:
            checkbox.setToolTip(tooltip)

        checkbox.stateChanged.connect(self.onCheckboxStateChanged)

        self.group_layout.addWidget(checkbox)

    @Slot()
    def onCheckboxStateChanged(self):
        self.optionsChanged.emit(self.validate_input())

    def validate_input(self) -> dict:
        res: dict = {}
        count = self.group_layout.count()

        for i in range(count):
            item = self.group_layout.itemAt(i)
            child: QCheckBox = item.widget()
            res[child.objectName()] = child.isChecked()

        return res

