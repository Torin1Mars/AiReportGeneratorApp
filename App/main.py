import sys

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

from App.UiWindows.main_window import MainWindow
from App.additional import get_app_path, get_resource_path
from App.supportingData.styles import DARK_GREEN_STYLESHEET

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_GREEN_STYLESHEET)

    appPath = get_app_path()

    app_icon = get_resource_path("assets/app_icon_32.png")
    #iconFullPath = os.path.join(appPath, app_icon)

    app.setWindowIcon(QIcon(str(app_icon)))

    window = MainWindow(appPath)
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
