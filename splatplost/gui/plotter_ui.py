from pathlib import Path

from PyQt6 import uic

file_path = Path(__file__).parent / "plotter.ui"

Form_plotter, Dialog_plotter = uic.loadUiType(str(file_path))
