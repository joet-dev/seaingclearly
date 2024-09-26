"""
COPYRIGHT: University of Sunshine Coast 2024

AUTHOR: Joseph Thurlow <joseph.thurlow@protonmail.com>
"""

import os
import sys
from importlib import metadata

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMainWindow


try:
    __package_name__ = metadata.metadata("seaingclearly")["Name"]
    __version__ = metadata.version("seaingclearly")
except Exception:
    __package_name__ = "seaingclearly"
    __version__ = "N/A"

try:
    from ctypes import windll

    myappid = f"{__package_name__}_v{__version__}"
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass


class SeaingClearly(QMainWindow): 

    def __init__(self): 
        super().__init__()
        self.setWindowTitle("Seaing Clearly")
        self.setGeometry(100, 100, 800, 600)

        print(os.path.isfile(r"./assets/prawn-16.png"))
        icon = QIcon(r"D:\Programming\_UNI\seaingclearly\app\assets\prawn-16.png")
        print(icon)
        self.setWindowIcon(icon)
        
        self.show()

if __name__ == '__main__':
    system_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(system_dir)

    print(system_dir)

    app = QApplication(sys.argv)

    window = SeaingClearly()

    sys.exit(app.exec())