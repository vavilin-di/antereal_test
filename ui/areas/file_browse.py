from typing import List

from PyQt5.QtWidgets import (
    QHBoxLayout,
    QPushButton,
    QFileDialog,
    QLineEdit,
)
from PyQt5.QtCore import QTimer, pyqtSignal


MANUAL_FILEPATH_INPUT_PARSING_DELAY_MS = 1000


class FileBrowseArea():
    def __init__(self, file_manual_input_open_timer: QTimer, new_file_opened_signal: pyqtSignal) -> None:
        self.file_manual_input_open_timer = file_manual_input_open_timer
        self.file_name = ''
        self.new_file_opened_signal = new_file_opened_signal
        self.file_browse_layout = QHBoxLayout()

        self.path_input = QLineEdit()
        self.path_input.textChanged.connect(self.restart_file_manual_input_open_timer)
        self.file_browse_layout.addWidget(self.path_input)

        file_button = QPushButton("Обзор")
        file_button.clicked.connect(self.show_file_dialog)
        self.file_browse_layout.addWidget(file_button)

    def restart_file_manual_input_open_timer(self):
        """Restart timer for manual file path input
        """
        self.file_manual_input_open_timer.stop()
        self.file_manual_input_open_timer.start(MANUAL_FILEPATH_INPUT_PARSING_DELAY_MS)

    def show_file_dialog(self):
        """Show native Windows file open dialog
        """
        self.file_name, _ = QFileDialog.getOpenFileName(None)
        self.path_input.setText(self.file_name)
        self.new_file_opened_signal.emit()
