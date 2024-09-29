"""
AUTHOR: Joseph Thurlow <joseph.thurlow@protonmail.com>
"""

from PySide6.QtWidgets import QWidget
from copy import deepcopy
from typing import Generator, Tuple


class StyleTheme:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(StyleTheme, cls).__new__(cls)
        return cls._instance

    def __init__(
        self,
        boiler: dict[str, dict[str, str]] = None,
        colors: dict[str, str] = {},
        paths: dict[str, str] = {},
    ):
        if not hasattr(self, "initialized"):
            self.initialized = True
            self.boiler = boiler
            self.colors = colors
            self.paths = paths

    def get_boiler_from_list(
        self, comp_key: list[str]
    ) -> Generator[Tuple[str, dict[str, str]], None, None]:
        for k in comp_key:
            yield self.get_boiler(k)

    def get_boiler(self, comp_key: str) -> Tuple[str, dict[str, str]]:
        element, key = comp_key.split("|", maxsplit=2)

        if key not in self.boiler:
            raise KeyError(f"Key {key} not found in boiler")

        return element, self.boiler[key]


class StylerMixin:
    def __init__(
        self: QWidget,
        style_sheet: dict = None,
        theme_classes: list[str] = None,
        name: str = None,
        **kwargs,
    ):
        super().__init__(**kwargs)

        if name is not None:
            self.setObjectName(name)

        if theme_classes is None:
            theme_classes = []
        if style_sheet is None:
            style_sheet = {}

        if len(theme_classes) > 0:
            self.theme = StyleTheme()

            for element, boiler in self.theme.get_boiler_from_list(theme_classes):
                if element not in style_sheet:
                    style_sheet[element] = boiler
                else:
                    style_sheet[element] = deep_update(style_sheet[element], boiler)

        self.default_style_sheet_dict: dict = deepcopy(style_sheet)
        self.current_style_sheet_dict: dict = style_sheet

        self.setSheet()

    def resetSheet(self):
        if self.current_style_sheet_dict == self.default_style_sheet_dict:
            return

        self.current_style_sheet_dict = deepcopy(self.default_style_sheet_dict)
        self.setSheet()

    def modifySheet(self, style_sheet: dict):
        self.current_style_sheet_dict = deep_update(
            self.current_style_sheet_dict, style_sheet
        )
        self.setSheet()

    def hardModifySheet(self, style_sheet: dict):
        self.current_style_sheet_dict = deep_update(
            self.current_style_sheet_dict, style_sheet
        )
        self.default_style_sheet_dict = deepcopy(self.current_style_sheet_dict)
        self.setSheet()

    def setSheet(self):
        print(f"SET {self.objectName()} ({type(self)})", self.current_style_sheet_dict)

        self.setStyleSheet(dict_to_custom_string(self.current_style_sheet_dict))

    def getIconPath(self, icon: str) -> str:
        if icon not in self.theme.paths:
            raise KeyError(f"Icon {icon} not found in paths")

        return self.theme.paths[icon]


def deep_update(original: dict, updates: dict):
    for key, value in updates.items():
        if (
            isinstance(value, dict)
            and key in original
            and isinstance(original[key], dict)
        ):
            deep_update(original[key], value)
        else:
            original[key] = value

    return original


def dict_to_custom_string(d: dict) -> str:
    def format_dict(d: dict) -> str:
        items = []
        for k, v in d.items():
            if isinstance(v, dict):
                items.append(f"{k} {{{format_dict(v)}}}")
            else:
                items.append(f"{k}: {v};")
        return " ".join(items)

    return format_dict(d)