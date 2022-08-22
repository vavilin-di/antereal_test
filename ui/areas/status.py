from typing import List

from PyQt5.QtWidgets import (
    QVBoxLayout,
    QWidget,
    QLabel,
    QSizePolicy,
    QScrollArea,
)

from errors.status_store import StatusStore


class StatusArea():
    def __init__(self, status_store: StatusStore) -> None:
        self.status_store = status_store
        self.status_area_container = QScrollArea()
        self.status_area_container.setWidgetResizable(True)
        self.status_area_widget = QWidget()
        self.status_area = QVBoxLayout()

        self.status_area_container.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))
        self.status_area_container.setMinimumHeight(25)
        self.status_area_container.setMaximumHeight(62)

        self.status_area_widget.setLayout(self.status_area)
        self.status_area_container.setWidget(self.status_area_widget)

    def update_status_area(self, statuses: List[str]) -> None:
        """Add new statuses to area

        Args:
            statuses (List[str]): statuses
        """
        for status in statuses:
            self.status_area.addWidget(QLabel(status))

        self.status_area_widget.setLayout(self.status_area)
        self.status_area.update()

    def clear_status_area(self) -> None:
        for index in range(self.status_area.count()):
            self.status_area.itemAt(index).widget().deleteLater()
        self.status_area.update()
