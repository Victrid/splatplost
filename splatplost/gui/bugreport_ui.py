import platform
import subprocess
import sys
import traceback
from pathlib import Path

from PyQt6 import QtWidgets, uic
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QDialog, QMessageBox

file_path = Path(__file__).parent / "bugreport.ui"

Form_bugreport, Dialog_bugreport = uic.loadUiType(str(file_path))

from splatplost.version import __version__


class BugReportDialog(Form_bugreport):
    def __init__(self, exception: Exception):
        super().__init__()
        traceback_text = "".join(traceback.format_exception(type(exception), exception, exception.__traceback__))

        result_text = """## Describe the bug

<!-- Please describe how you meet the bug -->

## Running Environment Information

**Splatplost version**: `{}`

**Python version**: `{}`

**OS Information**: `{}`

**Systemd Version**: 

```
{}
```

**Python Traceback**

```
{}
```

**Bluetooth status**

```
{}
```
        """.format(__version__,
                   sys.version,
                   platform.platform(),
                   subprocess.check_output("systemctl --version", shell=True).decode(),
                   traceback_text,
                   subprocess.check_output("systemctl status bluetooth.service", shell=True).decode(),
                   )

        self.result = result_text

    def save_to_file_clicked(self):
        """
        Save result to file

        """
        from PyQt6.QtWidgets import QFileDialog
        file_name = QFileDialog.getSaveFileName(None, "Save Bug Report", "bug_report.txt", "Text File (*.txt)")[0]
        if file_name:
            with open(file_name, "w") as f:
                f.write(self.result)

    def copy_to_clipboard_clicked(self):
        """
        Copy result to clipboard

        """
        from PyQt6.QtWidgets import QApplication
        QApplication.clipboard().setText(self.result)

    def open_issue_on_github(self):
        """
        Open issue on github

        """
        from requests.models import PreparedRequest
        url_query = {
            "title":  "[BUG] <Fill your bug info>",
            "body":   self.result,
            "labels": "bug"
            }
        req = PreparedRequest()
        base_url = "https://github.com/Victrid/splatplost/issues/new"
        req.prepare_url(base_url, url_query)
        result_url = req.url

        import webbrowser
        webbrowser.open(result_url)

    def setupUi(self, Dialog):
        super().setupUi(Dialog)
        self.save_to_file.clicked.connect(self.save_to_file_clicked)
        self.go_github.clicked.connect(self.open_issue_on_github)
        self.copy_to_clipboard.clicked.connect(self.copy_to_clipboard_clicked)
        self.traceback_content.setPlainText(self.result)


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
