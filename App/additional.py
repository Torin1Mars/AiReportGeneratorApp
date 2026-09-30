import sys
from pathlib import Path

APP_NAME = "Ai Report generator"
APP_VERSION = "v.1.0.3"

#Building with Pyinstaller
def get_app_path():
    if getattr(sys, "frozen", False):
        # Directory containing the .exe
        return Path(sys.executable).resolve().parent
    else:
        # Directory containing main.py
        return Path(__file__).resolve().parent


def get_resource_path(relative_path):
    if getattr(sys, "frozen", False):
        # Files bundled by PyInstaller
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).resolve().parent

    return base_path / relative_path