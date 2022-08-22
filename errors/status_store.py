from typing import List


class StatusStore():
    """Storage for statuses and errors
    """

    def __init__(self) -> None:
        self.statuses_list: List[str] = []

    def add_status(self, status: str) -> None:
        self.statuses_list.append(status)

    def clear_status_list(self) -> None:
        self.statuses_list = []

    def get_statuses_list(self) -> List[str]:
        return self.statuses_list
