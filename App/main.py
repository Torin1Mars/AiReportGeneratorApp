import sys
from PyQt6.QtWidgets import QApplication

from App.UiWindows.main_window import MainWindow
from App.SupportingData.styles import DARK_GREEN_STYLESHEET


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_GREEN_STYLESHEET)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()