import sys

from PyQt5.QtWidgets import QApplication

from errors.status_store import StatusStore
from ui.main_window import Window

if __name__ == "__main__":
    app = QApplication(sys.argv)
    status_store = StatusStore()
    window = Window(status_store=status_store)
    window.show()
    # Exit on any exceptions properly
    try:
        sys.exit(app.exec_())
    except:
        sys.exit()
