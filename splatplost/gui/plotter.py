import sys
import tempfile

from PIL import Image, ImageQt
from PyQt6 import QtWidgets
from PyQt6.QtCore import QMutex, QMutexLocker, QObject, QRunnable, QThreadPool, Qt, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QImage, QMouseEvent, QPixmap
from PyQt6.QtWidgets import QApplication, QDialog
from libnxctrl.bluetooth import get_backend
from libnxctrl.wrapper import Button, NXWrapper

from splatplost.generate_route import generate_route_file
from splatplost.gui.connect_to_switch_ui import Form_ConnectToSwitch
from splatplost.gui.plotter_ui import Form_plotter
from splatplost.plot import partial_erase_with_conn, partial_plot_with_conn
from splatplost.route_handler import RouteFile
from splatplost.version import __version__


class ConnectToSwitchUI(Form_ConnectToSwitch):
    def __init__(self, parent):
        super().__init__()
        self.parent: PlotterUI = parent
        self.current_pairing_guide_image = 0

    def start_pairing_clicked(self):
        if self.parent.connection is not None:
            self.parent.connection.disconnect()
        self.parent.connection = None
        self.start_pairing.setEnabled(False)
        self.start_pairing.setText("Pairing...")
        self.parent.start_pairing(success_callback=self.finished_pairing, fail_callback=self.error_pairing)

    def finished_pairing(self):
        self.start_pairing.setEnabled(True)
        self.Step2.setEnabled(True)
        self.Step1.setEnabled(False)

    def error_pairing(self):
        self.start_pairing.setEnabled(True)
        self.start_pairing.setText("Start Pairing")

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
    finish = pyqtSignal()
    error = pyqtSignal(str)


class PlotterUI(Form_plotter):
    class ConnectWorker(QRunnable):
        def __init__(self, parent):
            super().__init__()
            self.parent: PlotterUI = parent
            self.mutex = QMutex()
            self.signal = WorkerSignals()

        @pyqtSlot()
        def run(self) -> None:
            try:
                with QMutexLocker(self.mutex):
                    backend = get_backend("nxbt")
                    connection = backend(press_duration_ms=int(self.parent.key_press_ms.value()),
                                         delay_ms=int(self.parent.delay_ms.value())
                                         )
                    connection.connect()
                    self.parent.connection = connection
            except Exception as e:
                self.parent.connection = None
                self.signal.error.emit(str(e))
                return
            self.signal.finish.emit()

    class PlotWorker(QRunnable):
        def __init__(self, parent: 'PlotterUI', plotfunc):
            super().__init__()
            self.parent: PlotterUI = parent
            self.mutex = QMutex()
            self.signal = WorkerSignals()
            self.plotfunc = plotfunc

        @pyqtSlot()
        def run(self) -> None:
            try:
                with QMutexLocker(self.mutex):
                    self.plotfunc()
            except Exception as e:
                self.signal.error.emit(str(e))
                return
            self.signal.finish.emit()

    def __init__(self):
        super().__init__()
        self.tempdir = tempfile.TemporaryDirectory(prefix="splatplost")
        self.RouteFile = None
        self.connection: NXWrapper | None = None
        self.thread_pool = QThreadPool()
        self.thread_pool.setMaxThreadCount(1)

    def __del__(self):
        self.tempdir.cleanup()

    def update_image(self, image: Image.Image) -> None:
        self.image.setPixmap(QPixmap.fromImage(ImageQt.ImageQt(image)))

    def __validate_before_drawing(self) -> bool:
        if self.RouteFile is None:
            self.statusBar.showMessage("No file loaded", 2000)
            return False
        if self.splatoon_ver.currentText() not in ["Splatoon 2", "Splatoon 3"]:
            self.statusBar.showMessage("Splatoon version not selected")
            return False
        if not self.switch_connected.isChecked() or self.connection is None:
            self.statusBar.showMessage("Not connected to switch")
            return False
        return True

    def start_pairing(self, success_callback, fail_callback):
        worker = self.ConnectWorker(self)

        def success():
            success_callback()
            self.thread_pool.waitForDone()

        def fail():
            fail_callback()
            self.thread_pool.waitForDone()

        worker.signal.finish.connect(success)
        worker.signal.error.connect(fail)
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
                self.statusBar.showMessage("ERROR: {}".format(e))
                self.file_loc.setText("")
                return

    def read_file_clicked(self):
        try:
            if self.file_loc.text() == "":
                raise FileNotFoundError("No file selected")
            generate_route_file(self.file_loc.text(), f"{self.tempdir.name}/plot_file.json")
        except Exception as e:
            self.progress.setValue(0)
            self.statusBar.showMessage("ERROR: {}".format(e))
            self.file_loc.setText("")
            return
        self.progress.setValue(75)
        self.RouteFile = RouteFile(f"{self.tempdir.name}/plot_file.json")
        image = self.RouteFile.generate_image_of_selected()

        self.update_image(image)
        self.selected_label.setEnabled(True)
        self.image.setEnabled(True)
        self.progress.setValue(100)
        self.statusBar.showMessage("File read successfully", 5000)

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
            self.statusBar.showMessage("No file loaded", 500)
            return
        self.RouteFile.select_all_blocks()
        image = self.RouteFile.generate_image_of_selected()
        self.update_image(image)

    def deselect_all_clicked(self):
        """
        Deselect all the blocks in the image.

        """
        if self.RouteFile is None:
            self.statusBar.showMessage("No file loaded", 500)
            return
        self.RouteFile.deselect_all_blocks()
        image = self.RouteFile.generate_image_of_selected()
        self.update_image(image)

    def draw_selected_clicked(self):
        if not self.__validate_before_drawing():
            return

        def draw_func():
            splatoon_3 = self.splatoon_ver.currentText() == "Splatoon 3"

            partial_plot_with_conn(self.connection, self.RouteFile.blocks.items(),
                                   stable_mode=self.stable_mode.isChecked(),
                                   clear_drawing=self.clear_drawing.isChecked(), splatoon3=splatoon_3,
                                   plot_blocks=self.RouteFile.get_selected_blocks()
                                   )

        worker = self.PlotWorker(self, draw_func)

        self.draw_selected.setEnabled(False)
        self.erase_selected.setEnabled(False)

        def success():
            self.draw_selected.setEnabled(True)
            self.erase_selected.setEnabled(True)
            self.statusBar.showMessage("Drawing finished")
            self.thread_pool.waitForDone()

        def fail(e: str):
            self.draw_selected.setEnabled(True)
            self.erase_selected.setEnabled(True)
            self.statusBar.showMessage("ERROR: {}".format(e))
            self.thread_pool.waitForDone()

        worker.signal.finish.connect(success)
        worker.signal.error.connect(fail)
        self.thread_pool.start(worker)

    def erase_selected_clicked(self):
        if not self.__validate_before_drawing():
            return

        def draw_func():
            splatoon_3 = self.splatoon_ver.currentText() == "Splatoon 3"

            partial_erase_with_conn(self.connection, self.RouteFile.blocks.items(),
                                    stable_mode=self.stable_mode.isChecked(),
                                    clear_drawing=self.clear_drawing.isChecked(), splatoon3=splatoon_3,
                                    plot_blocks=self.RouteFile.get_selected_blocks()
                                    )

        worker = self.PlotWorker(self, draw_func)

        self.draw_selected.setEnabled(False)
        self.erase_selected.setEnabled(False)

        def success():
            self.draw_selected.setEnabled(True)
            self.erase_selected.setEnabled(True)
            self.statusBar.showMessage("Drawing finished")
            self.thread_pool.waitForDone()

        def fail(e: str):
            self.draw_selected.setEnabled(True)
            self.erase_selected.setEnabled(True)
            self.statusBar.showMessage("ERROR: {}".format(e))
            self.thread_pool.waitForDone()

        worker.signal.finish.connect(success)
        worker.signal.error.connect(fail)
        self.thread_pool.start(worker)

    def setupUi(self, plotter):
        super().setupUi(plotter)

        # File loading
        self.open_file.clicked.connect(self.open_file_clicked)
        self.read_file.clicked.connect(self.read_file_clicked)

        # Pixel clicking
        self.image.mousePressEvent = self.image_clicked

        # Selecting
        self.select_all.clicked.connect(self.select_all_clicked)
        self.deselect_all.clicked.connect(self.deselect_all_clicked)

        # Drawing
        self.draw_selected.clicked.connect(self.draw_selected_clicked)
        self.erase_selected.clicked.connect(self.draw_selected_clicked)

        # Connection
        self.switch_connected.setChecked(False)
        self.switch_conn.clicked.connect(self.connect_switch)

        # Splatoon version
        self.splatoon_ver.addItems(["Splatoon 2", "Splatoon 3"])

        # Set information
        self.info.setText("**Splatplost version {}**".format(__version__))


def main():
    app = QApplication(sys.argv)

    form = QtWidgets.QMainWindow()

    window = PlotterUI()
    window.setupUi(form)
    form.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
