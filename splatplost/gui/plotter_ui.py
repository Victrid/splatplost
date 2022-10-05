from PyQt6 import uic

from splatplost.gui.bundler import ui_path

Form_plotter, Dialog_plotter = uic.loadUiType(ui_path("plotter.ui"))
