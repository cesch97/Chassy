from PyQt5.QtWidgets import QApplication
from gui.widgets import ChessApp


if __name__ == "__main__":
    app = QApplication([])
    widget = ChessApp()
    widget.show()
    app.exec()