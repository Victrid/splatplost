import os
import sys
from pathlib import Path


# Helps the PyInstaller to find extra files

def ui_path(relative_path: str) -> str:
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # noinspection PyProtectedMember
        base_path = sys._MEIPASS
        return str(os.path.join(base_path, "splatplost", relative_path))
    else:
        base_path = Path(__file__).parent
        return str(os.path.join(base_path, relative_path))


def lang_path(relative_path: str) -> str:
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # noinspection PyProtectedMember
        base_path = sys._MEIPASS
        return str(os.path.join(base_path, "splatplost", relative_path))
    else:
        base_path = Path(__file__).parent
        return str(os.path.join(base_path, "i18n", relative_path))
