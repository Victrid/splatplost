import sys
import tempfile
from functools import partial
from pathlib import Path
from typing import Optional

import PIL
from PIL import Image, ImageQt
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import QLocale, QMutex, QMutexLocker, QObject, QRunnable, QThreadPool, Qt, \
    pyqtSignal, pyqtSlot
from PyQt6.QtGui import QImage, QMouseEvent, QPixmap
from PyQt6.QtWidgets import QApplication, QDialog, QMessageBox
from libnxctrl.backend import get_available_backend, get_backend
from libnxctrl.wrapper import Button, NXWrapper

from splatplost.generate_route import generate_route_file
from splatplost.gui.bugreport_ui import spawn_error_dialog
from splatplost.gui.connect_to_switch_ui import ConnectToSwitchUI
from splatplost.gui.plotter_ui import Form_plotter
from splatplost.keybindings import Splatoon2KeyBinding, Splatoon3KeyBinding
from splatplost.plot import partial_erase_with_conn, partial_plot_with_conn
from splatplost.route_handler import RouteFile
from splatplost.version import __version__


class WorkerSignals(QObject):
    finish: pyqtSignal = pyqtSignal()
    error: pyqtSignal = pyqtSignal(Exception)


class AsyncWorker(QRunnable):
    def __init__(self, parent: 'PlotterUI', working_function):
        super().__init__()
        self.parent: PlotterUI = parent
        self.mutex = QMutex()
        self.signal = WorkerSignals()
        self.working_function = working_function

    @pyqtSlot()
    def run(self) -> None:
        try:
            with QMutexLocker(self.mutex):
                self.working_function()
        except Exception as e:
            self.signal.error.emit(e)
            return
        self.signal.finish.emit()


class PlotterUI(Form_plotter):

    def __init__(self, app, form):
        super().__init__()
        self.tempdir = tempfile.TemporaryDirectory(prefix="splatplost")
        self.RouteFile = None
        self.connection: Optional[NXWrapper] = None
        self.thread_pool: QThreadPool = QThreadPool()
        self.app = app
        self.form = form
        self.trans: QtCore.QTranslator = QtCore.QTranslator()
        self.current_key_binding = None

        self.thread_pool.setMaxThreadCount(1)

    def __del__(self):
        self.tempdir.cleanup()

    def update_image(self, image: Image.Image) -> None:
        self.image.setPixmap(QPixmap.fromImage(ImageQt.ImageQt(image)))

    def __validate_before_drawing(self) -> bool:
        if self.RouteFile is None:
            spawn_error_dialog(ValueError(QApplication.translate("@default", "No file loaded")),
                               QApplication.translate("@default", "No file loaded"),
                               reportable=False
                               )
            return False
        if self.splatoon_ver.currentText() not in ["Splatoon 2", "Splatoon 3"] or self.current_key_binding is None:
            spawn_error_dialog(ValueError(QApplication.translate("@default", "Splatoon version not selected")),
                               QApplication.translate("@default", "Splatoon version not selected"),
                               reportable=False
                               )
            return False
        if not self.switch_connected.isChecked() or self.connection is None:
            spawn_error_dialog(ValueError(QApplication.translate("@default", "Switch not connected")),
                               QApplication.translate("@default", "Switch not connected"),
                               reportable=False
                               )
            return False
        return True

    def start_pairing(self, backend_type, parameters, success_callback, fail_callback):
        # If we are already connected, hint the user.
        reconnect_confirm_dialog = QMessageBox()
        reconnect_confirm_dialog.setText(
                QApplication.translate("@default",
                                       "The switch seems to be connected. Are you sure you want to reconnect?"
                                       )
                )
        reconnect_confirm_dialog.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        reconnect_confirm_dialog.setDefaultButton(QMessageBox.StandardButton.No)
        if self.connection is not None:
            if reconnect_confirm_dialog.exec() == QMessageBox.StandardButton.No:
                success_callback()
                return
            self.connection.disconnect()
            self.connection = None

        def pairing():
            try:
                backend = get_backend(backend_name=backend_type)
                connection = backend(**parameters)
                connection.connect()
                self.connection = connection
            except Exception as e:
                self.connection = None
                raise e

        worker = AsyncWorker(self, pairing)

        worker.signal.finish.connect(lambda: (success_callback(), self.thread_pool.waitForDone()))
        worker.signal.error.connect(lambda e: (fail_callback(e), self.thread_pool.waitForDone()))
        self.thread_pool.start(worker)

    def ready_for_drawing(self):
        self.switch_connected.setChecked(True)

    def press_a(self):
        self.connection.button_press(Button.A)

    def press_shoulder_l(self):
        self.connection.button_press(Button.SHOULDER_L)

    def press_shoulder_r(self):
        self.connection.button_press(Button.SHOULDER_R)

    def connect_switch(self):
        try:
            ui = ConnectToSwitchUI(self, backend=self.backend_selector.currentText())
            dialog = QDialog()
            ui.setupUi(dialog)
            dialog.exec()
        except ValueError:
            spawn_error_dialog(ValueError(QApplication.translate("@default", "No backend selected")),
                               QApplication.translate("@default", "No backend selected"),
                               reportable=False
                               )
        except Exception as e:
            spawn_error_dialog(e, QApplication.translate("@default", "Error when connecting to switch"))

    def open_file_clicked(self):
        dialog = QtWidgets.QFileDialog()
        dialog.setFileMode(QtWidgets.QFileDialog.FileMode.ExistingFile)
        dialog.setMimeTypeFilters(["image/png", "image/jpeg"])
        dialog.exec()

        self.selected_label.setEnabled(False)
        self.image.setEnabled(False)
        self.progress.setValue(0)
        if dialog.result() == QtWidgets.QDialog.DialogCode.Accepted:
            self.file_loc.setText(dialog.selectedFiles()[0])
            self.progress.setValue(20)
            try:
                image = QImage(self.file_loc.text())
                self.image.setPixmap(QPixmap.fromImage(image))
                self.progress.setValue(100)
            except Exception as e:
                self.progress.setValue(0)
                self.file_loc.setText("")
                spawn_error_dialog(e, QApplication.translate("@default", "Error when loading image"))
                return

    def read_file_clicked(self):
        try:
            if self.file_loc.text() == "":
                spawn_error_dialog(ValueError(QApplication.translate("@default", "No file loaded")),
                                   QApplication.translate("@default", "No file loaded"),
                                   reportable=False
                                   )
                return
            generate_route_file(self.file_loc.text(), f"{self.tempdir.name}/plot_file.json")
        except Exception as e:
            self.progress.setValue(0)
            self.file_loc.setText("")
            spawn_error_dialog(e, QApplication.translate("@default", "Error when reading file"))
            return
        self.progress.setValue(75)
        self.RouteFile = RouteFile(f"{self.tempdir.name}/plot_file.json")
        image = self.RouteFile.generate_image_of_selected()

        self.update_image(image)
        self.selected_label.setEnabled(True)
        self.image.setEnabled(True)
        self.progress.setValue(100)
        self.statusBar.showMessage(QApplication.translate("@default", "File read successfully"))

    def load_white_clicked(self):
        image = PIL.Image.new("RGB", (320, 120), (255, 255, 255))
        image.save(f"{self.tempdir.name}/white.png")
        self.file_loc.setText(f"{self.tempdir.name}/white.png")
        self.read_file_clicked()

    def image_clicked(self, event: QMouseEvent) -> None:
        """
        Handles the click event on the image, update the selected blocks.

        :param event: The event that triggered this function
        """
        # Need to be reversed because the image have different implementation
        x = event.pos().x()
        y = event.pos().y()
        mouse_button = event.button()

        if self.RouteFile is None:
            return

        if mouse_button == Qt.MouseButton.LeftButton:
            self.RouteFile.select_block_from_pixel(x, y)
        elif mouse_button == Qt.MouseButton.RightButton:
            self.RouteFile.deselect_block_from_pixel(x, y)
        else:
            return
        self.update_image(self.RouteFile.generate_image_of_selected())
        return

    def select_all_clicked(self):
        """
        Select all the blocks in the image.

        """
        if self.RouteFile is None:
            spawn_error_dialog(FileNotFoundError(), QApplication.translate("@default", "No file loaded"),
                               reportable=False
                               )
            return
        self.RouteFile.select_all_blocks()
        image = self.RouteFile.generate_image_of_selected()
        self.update_image(image)

    def deselect_all_clicked(self):
        """
        Deselect all the blocks in the image.

        """
        if self.RouteFile is None:
            spawn_error_dialog(FileNotFoundError(), QApplication.translate("@default", "No file loaded"),
                               reportable=False
                               )
            return
        self.RouteFile.deselect_all_blocks()
        image = self.RouteFile.generate_image_of_selected()
        self.update_image(image)

    def draw_selected_clicked(self):
        if not self.__validate_before_drawing():
            return

        def draw_func():
            partial_plot_with_conn(self.connection, self.RouteFile.blocks.items(), key_binding=self.current_key_binding,
                                   cursor_reset=not self.skip_cal.isChecked(),
                                   cursor_reset_time=1000 * int(self.cal_time.value()),
                                   stable_mode=self.stable_mode.isChecked(),
                                   clear_drawing=self.clear_drawing.isChecked(),
                                   plot_blocks=self.RouteFile.get_selected_blocks()
                                   )

        worker = AsyncWorker(self, draw_func)

        self.draw_selected.setEnabled(False)
        self.erase_selected.setEnabled(False)

        def success():
            self.draw_selected.setEnabled(True)
            self.erase_selected.setEnabled(True)
            self.statusBar.showMessage(QApplication.translate("@default", "Drawing finished"))
            self.thread_pool.waitForDone()

        def fail(e: Exception):
            self.draw_selected.setEnabled(True)
            self.erase_selected.setEnabled(True)
            spawn_error_dialog(e, QApplication.translate("@default", "Error when drawing"))
            self.thread_pool.waitForDone()

        worker.signal.finish.connect(success)
        worker.signal.error.connect(fail)
        self.thread_pool.start(worker)

    def erase_selected_clicked(self):
        if not self.__validate_before_drawing():
            return

        def draw_func():
            partial_erase_with_conn(self.connection, key_binding=self.current_key_binding,
                                    horizontal_divider=self.RouteFile.horizontal_divider,
                                    vertical_divider=self.RouteFile.vertical_divider,
                                    cursor_reset=not self.skip_cal.isChecked(),
                                    cursor_reset_time=1000 * int(self.cal_time.value()),
                                    stable_mode=self.stable_mode.isChecked(),
                                    clear_drawing=self.clear_drawing.isChecked(),
                                    plot_blocks=self.RouteFile.get_selected_blocks()
                                    )

        worker = AsyncWorker(self, draw_func)

        self.draw_selected.setEnabled(False)
        self.erase_selected.setEnabled(False)

        def success():
            self.draw_selected.setEnabled(True)
            self.erase_selected.setEnabled(True)
            self.statusBar.showMessage(QApplication.translate("@default", "Drawing finished"))
            self.thread_pool.waitForDone()

        def fail(e: Exception):
            self.draw_selected.setEnabled(True)
            self.erase_selected.setEnabled(True)
            spawn_error_dialog(e, QApplication.translate("@default", "Error when erasing"))
            self.thread_pool.waitForDone()

        worker.signal.finish.connect(success)
        worker.signal.error.connect(fail)
        self.thread_pool.start(worker)

    def language_clicked(self, language_code: str) -> None:
        """
        Change the language of the application.

        :param language_code: The language code to change to
        """
        self.trans.load(str(Path(__file__).parent / "i18n" / "{}.qm".format(language_code)))
        QtWidgets.QApplication.instance().installTranslator(self.trans)
        self.retranslateUi(self.form)

    def splatoon_ver_changed(self, text: str):
        if text == "Splatoon 3":
            self.current_key_binding = Splatoon3KeyBinding()
        elif text == "Splatoon 2":
            self.current_key_binding = Splatoon2KeyBinding()
        else:
            return

    def retranslateUi(self, plotter):
        super().retranslateUi(plotter)
        # Set information
        self.info.setText(QApplication.translate("@default", "**Splatplost version {}**").format(__version__))

    def setupUi(self, plotter):
        super().setupUi(plotter)

        # File loading
        self.open_file.clicked.connect(self.open_file_clicked)
        self.read_file.clicked.connect(self.read_file_clicked)
        self.load_white.clicked.connect(self.load_white_clicked)

        # Pixel clicking
        self.image.mousePressEvent = self.image_clicked

        # Selecting
        self.select_all.clicked.connect(self.select_all_clicked)
        self.deselect_all.clicked.connect(self.deselect_all_clicked)

        # Drawing
        self.draw_selected.clicked.connect(self.draw_selected_clicked)
        self.erase_selected.clicked.connect(self.erase_selected_clicked)

        # Connection
        self.switch_connected.setChecked(False)
        self.switch_conn.clicked.connect(self.connect_switch)

        # Splatoon version
        self.splatoon_ver.addItems(["Splatoon 2", "Splatoon 3"])
        self.splatoon_ver.currentTextChanged.connect(self.splatoon_ver_changed)

        # Language
        self.language_zhCN.triggered.connect(partial(self.language_clicked, "zh_CN"))
        self.language_enUS.triggered.connect(partial(self.language_clicked, "en_US"))
        self.language_jaJP.triggered.connect(partial(self.language_clicked, "ja_JP"))
        self.language_zhTW.triggered.connect(partial(self.language_clicked, "zh_TW"))

        # Init available backend
        self.backend_selector.addItems(get_available_backend())

        # Press
        self.press_l.clicked.connect(self.press_shoulder_l)
        self.press_r.clicked.connect(self.press_shoulder_r)


def main():
    app = QApplication(sys.argv)

    form = QtWidgets.QMainWindow()

    t = QtCore.QTranslator()
    t.load(str(Path(__file__).parent / "i18n" / (QLocale.system().name() + ".qm")))
    app.installTranslator(t)

    window = PlotterUI(app, form)
    window.setupUi(form)
    form.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
