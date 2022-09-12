import platform
import subprocess
import sys
import traceback
from pathlib import Path

from PyQt6 import uic

file_path = Path(__file__).parent / "bugreport.ui"

Form_bugreport, Dialog_bugreport = uic.loadUiType(str(file_path))

from splatplost.version import __version__


class BugReportDialog(Form_bugreport):
    def __init__(self, exception: Exception):
        super().__init__()
        traceback_text = traceback.format_exc()

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
