from typing import Callable, Tuple
import os

from PySide6.QtCore import QSize, Signal
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
            theme_classes=[f"QPushButton#{name}|button", f"QPushButton#{name}:hover|button-hover"],
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
        downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
        folder_path = QFileDialog.getExistingDirectory(
            self, "Select Extraction Folder", downloads_folder
        )

        if folder_path:
            self.line_edit.setText(folder_path)

    def lineEdit(self):
        return self.line_edit
    

class Label(StylerMixin, QLabel):
    def __init__(
        self,
        text: str,
        font_size: int = None,
        custom_style: dict = None,
        theme_classes: list[str] = ["QLabel|label"],
    ):
        super().__init__(text=text, theme_classes=theme_classes)

        if font_size:
            self.hard_modify_sheet({"QLabel": {"font-size": f"{font_size}px"}})

        if custom_style:
            self.hard_modify_sheet(custom_style)
