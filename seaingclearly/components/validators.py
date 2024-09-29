from typing import Tuple
import os




class ValidationResponse:
    def __init__(self, text: str, error: str = None):
        self.text = text
        self.error = error


def validate_not_empty(text: str) -> Tuple[bool, str]:
    if text.strip() == "":
        return False, "Field cannot be empty"

    return True, None

def validate_path(text: str) -> Tuple[bool, str]:
    if text.strip() == "":
        return False, "Field cannot be empty"

    path_exists:bool = os.path.exists(text)
    return path_exists, None if path_exists else "Path or directory does not exist"