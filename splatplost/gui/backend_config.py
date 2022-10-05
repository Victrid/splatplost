from PyQt6 import uic

from splatplost.gui.bundler import ui_path

Form_nxbt, _ = uic.loadUiType(ui_path("nxbt.ui"))

Form_SUSB, _ = uic.loadUiType(ui_path("splatplost_USB.ui"))

Form_Remote, _ = uic.loadUiType(ui_path("remote.ui"))


class NxbtConfigWidget(Form_nxbt):
    def get_connection_args(self):
        return {
            "press_duration_ms": int(self.press_ms.value()),
            "delay_ms":          int(self.delay_ms.value()),
            }


# noinspection PyPep8Naming
class SplatplostUSBConfigWidget(Form_SUSB):
    def setupUi(self, config_widget):
        super().setupUi(config_widget)
        # Get available serial ports
        from serial.tools.list_ports import comports
        for port in comports():
            self.serial_port.addItem(port.device)

    def get_connection_args(self):
        return {
            "serial_port":       self.serial_port.currentText(),
            "press_duration_ms": int(self.press_ms.value()),
            }


class RemoteConfigWidget(Form_Remote):
    def get_connection_args(self):
        return {
            "conn_str":          self.server_addr.text(),
            "press_duration_ms": int(self.press_ms.value()),
            "delay_ms":          int(self.delay_ms.value()),
            }
