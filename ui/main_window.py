from PyQt5.QtWidgets import (
    QVBoxLayout,
    QWidget,
    QShortcut,
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QKeySequence

from coordinates_handling.coordinates_handling import CoordinatesHandler
from errors.status_store import StatusStore
from ui.areas import FileBrowseArea, MapArea, StatusArea

MANUAL_FILEPATH_INPUT_PARSING_DELAY_MS = 1000

MAIN_WINDOW_MIN_WIDTH = 640
MAIN_WINDOW_MIN_HEIGHT = 480

MAP_ZOOM_RATIO = 1.5


class Window(QWidget):
    new_file_opened_signal = pyqtSignal()
    shape_removed_signal = pyqtSignal()

    def __init__(self, status_store: StatusStore):
        super().__init__()

        self.status_store = status_store

        self.setWindowTitle("Тестовая ГИС")
        self.setMinimumSize(MAIN_WINDOW_MIN_WIDTH, MAIN_WINDOW_MIN_HEIGHT)

        self.file_manual_input_open_timer = QTimer()
        # Display map on manual input (on timer timeout) or on file name set through file open dialog
        self.file_manual_input_open_timer.timeout.connect(self.display_map)
        self.new_file_opened_signal.connect(self.display_map)

        self.shape_removed_signal.connect(self.remove_shape)
        # Save file on Ctrl+s sequence
        save_file_shortcut = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_S), self)
        save_file_shortcut.activated.connect(self.save_coords_file)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        self.coordinates_handler = CoordinatesHandler(status_store=self.status_store)

        # Initialize areas (file browse, map, statuses)
        self.file_browse_area = FileBrowseArea(
            file_manual_input_open_timer=self.file_manual_input_open_timer, new_file_opened_signal=self.new_file_opened_signal)
        main_layout.addLayout(self.file_browse_area.file_browse_layout)

        self.map_area = MapArea(shape_removed_signal=self.shape_removed_signal)
        main_layout.addWidget(self.map_area.map_widget)

        self.status_area = StatusArea(status_store=self.status_store)
        main_layout.addWidget(self.status_area.status_area_container)

    def clear_statuses(self):
        """Remove status records from storage and area widget
        """
        self.status_store.clear_status_list()
        self.status_area.clear_status_area()

    def display_map(self):
        """Stop manual input timer, get coordinates, render shapes and update status
        """
        self.file_manual_input_open_timer.stop()

        self.clear_statuses()

        self.coordinates_handler.retrieve_coords(file_path=self.file_browse_area.path_input.text())
        self.map_area.render_shapes(self.coordinates_handler.get_shapes())

        self.status_area.update_status_area(statuses=self.status_store.get_statuses_list())

    def remove_shape(self):
        """Remove shape from coordinates_handler and rendered item from map
        """
        focused_shape = self.map_area.get_focused_shape()
        if focused_shape is not None:
            self.coordinates_handler.remove_shape(id=id(self.map_area.get_focused_shape()))
            self.map_area.remove_focused_item()

    def save_coords_file(self):
        """Clear status list only (not the widget) save coords to file and update status
        """
        self.status_store.clear_status_list()
        self.coordinates_handler.save_coords(file_path=self.file_browse_area.path_input.text())
        self.status_area.update_status_area(statuses=self.status_store.get_statuses_list())
