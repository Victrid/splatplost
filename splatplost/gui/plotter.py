import sys
import tempfile
from functools import partial
from pathlib import Path

import PIL
from PIL import Image, ImageQt
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import QLocale, QMutex, QMutexLocker, QObject, QRunnable, QThreadPool, Qt, \
    pyqtSignal, pyqtSlot
from PyQt6.QtGui import QImage, QMouseEvent, QPixmap
from PyQt6.QtWidgets import QApplication, QDialog, QMessageBox
from libnxctrl.bluetooth import get_backend
from libnxctrl.wrapper import Button, NXWrapper

from splatplost.generate_route import generate_route_file
from splatplost.gui.bugreport_ui import BugReportDialog
from splatplost.gui.connect_to_switch_ui import Form_ConnectToSwitch
from splatplost.gui.plotter_ui import Form_plotter
from splatplost.keybindings import Splatoon2KeyBinding, Splatoon3KeyBinding
from splatplost.plot import partial_erase_with_conn, partial_plot_with_conn
from splatplost.route_handler import RouteFile
from splatplost.version import __version__


def spawn_error_dialog(error: Exception, description: str, reportable: bool = True) -> int:
    """
    Create a dialog to show error message.

    :param error: The error object.
    :param description: The description of the error.
    :param reportable: Whether to allow user to report the error.
    """
    dialog = QtWidgets.QMessageBox()
    dialog.setText("**{}**\n\n"
                   "```\n"
                   "{}\n"
                   "{}\n"
                   "```".format(description,
                                error.__class__.__name__, error.what() if hasattr(error, "what") else str(error)
                                )
                   )
    dialog.setWindowTitle(QApplication.translate("@default", "Error happened"))
    dialog.setTextFormat(Qt.TextFormat.MarkdownText)
    if reportable:
        dialog.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok | QtWidgets.QMessageBox.StandardButton.Help)
        dialog.setDefaultButton(QtWidgets.QMessageBox.StandardButton.Ok)
        result = dialog.exec()

        if result == QMessageBox.StandardButton.Help:
            ui = BugReportDialog(error)
            dialog = QDialog()
            ui.setupUi(dialog)
            dialog.exec()
            result = QMessageBox.StandardButton.Ok

        return result
    else:
        dialog.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
        dialog.setDefaultButton(QtWidgets.QMessageBox.StandardButton.Ok)
        return dialog.exec()


class ConnectToSwitchUI(Form_ConnectToSwitch):
    def __init__(self, parent):
        super().__init__()
        self.parent: PlotterUI = parent
        self.current_pairing_guide_image = 0

    def start_pairing_clicked(self):
        self.start_pairing.setEnabled(False)
        self.start_pairing.setText(QApplication.translate("@default", "Pairing..."))
        self.parent.start_pairing(success_callback=self.finished_pairing, fail_callback=self.error_pairing)

    def finished_pairing(self):
        self.start_pairing.setEnabled(True)
        self.Step2.setEnabled(True)
        self.Step1.setEnabled(False)

    def error_pairing(self, err: Exception):
        self.start_pairing.setEnabled(True)
        self.start_pairing.setText(QApplication.translate("@default", "Start Pairing"))
        if isinstance(err, PermissionError):
            return spawn_error_dialog(err, QApplication.translate("@default", "Permission Error (Run as root?)"),
                                      reportable=False
                                      )
        return spawn_error_dialog(err, QApplication.translate("@default", "Error when pairing"))

    def done_clicked(self):
        self.parent.ready_for_drawing()
        self.parent_dialog.close()

    def press_a_clicked(self):
        self.parent.press_a()

    def setupUi(self, connect_to_switch):
        super().setupUi(connect_to_switch)
        self.start_pairing.clicked.connect(self.start_pairing_clicked)
        self.done.clicked.connect(self.done_clicked)
        self.press_a.clicked.connect(self.press_a_clicked)
        self.parent_dialog = connect_to_switch


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
        self.connection: NXWrapper | None = None
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

    def start_pairing(self, success_callback, fail_callback):
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
                backend = get_backend("nxbt")
                connection = backend(press_duration_ms=int(self.key_press_ms.value()),
                                     delay_ms=int(self.delay_ms.value())
                                     )
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

    def connect_switch(self):
        ui = ConnectToSwitchUI(self)
        dialog = QDialog()
        ui.setupUi(dialog)
        dialog.exec()

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
            partial_plot_with_conn(self.connection, self.RouteFile.blocks.items(),
                                   stable_mode=self.stable_mode.isChecked(),
                                   clear_drawing=self.clear_drawing.isChecked(),
                                   key_binding=self.current_key_binding,
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
            partial_erase_with_conn(self.connection,
                                    horizontal_divider=self.RouteFile.horizontal_divider,
                                    vertical_divider=self.RouteFile.vertical_divider,
                                    stable_mode=self.stable_mode.isChecked(),
                                    clear_drawing=self.clear_drawing.isChecked(),
                                    key_binding=self.current_key_binding,
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
