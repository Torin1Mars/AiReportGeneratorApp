import os.path
import webbrowser
from pathlib import Path
from tkinter import messagebox

from PyQt6.QtCore import QPoint, Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from App.additional import APP_VERSION, APP_NAME, get_resource_path
from App.supportingData.settingsManager import SettingsManager
from App.UiElements.file_input_row import FileInputRow
from App.WindowsLogic.main_window_logic import MainWindowLogic
from App.UiWindows.settings_window import SettingsWindow

class MainWindow(QWidget):
    def __init__(self, currentAppPath:Path):
        super().__init__()
        self.thisAppPath = currentAppPath
        self.currentSettings  = SettingsManager(self.thisAppPath)

        #Logic
        #With using lateinit
        self.mainWindowLogic = MainWindowLogic(self.currentSettings)

        #Ui
        self._drag_position = QPoint()
        self._setup_screen()

        self._build_ui()
        self.mainWindowLogic.appIndicator = self.generation_status_label

        #Settings
        self.settings_window = SettingsWindow(self.currentSettings, self)

        self.settings_window.hide()

    def _setup_screen(self):
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        #Window size
        self.setFixedSize(self.currentSettings.MAIN_WINDOW_WIDTH, self.currentSettings.MAIN_WINDOW_HEIGHT)

        #Starting position
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        start_width = int((screen_geometry.width()-self.currentSettings.MAIN_WINDOW_WIDTH) * 0.5)
        start_height = int((screen_geometry.height()-self.currentSettings.MAIN_WINDOW_HEIGHT) * 0.5)
        self.move(start_width, start_height)

    def _build_ui(self):
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(5, 5, 5, 5)

        container = QFrame()
        container.setObjectName("MainContainer")
        outer_layout.addWidget(container)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        layout.addLayout(self._build_header())

        layout.addWidget(self._build_section_title("Preparation:"))
        layout.addWidget(self._build_preparation_group())

        layout.addWidget(self._build_section_title("AI generation:"))
        layout.addWidget(self._build_generation_group())

        #Generate button
        generate_button = QPushButton("Generate report")
        generate_button.setObjectName("PrimaryButton")
        generate_button.clicked.connect(self._runReportGeneration)
        layout.addWidget(generate_button)

        #DevBy section
        layout.addLayout(self._build_bottom_layout())

    def _build_header(self):
        header_layout = QHBoxLayout()

        '''icon_label = QLabel("\U0001F4C4")
        icon_label.setObjectName("AppIcon")
        icon_label.setFixedSize(30, 30)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)'''

        image_label = QLabel()
        #image_label.setPixmap(QPixmap("assets/app_icon_32.png"))

        iconPath = get_resource_path("assets/app_icon_32.png")
        image_label.setPixmap(QPixmap(str(iconPath)))

        title_label = QLabel(APP_NAME)
        title_label.setObjectName("AppTitle")

        self.about_button = QPushButton("\u24D8")
        self.about_button.setObjectName("IconButton")
        self.about_button.setFixedSize(30, 30)
        self.about_button.clicked.connect(self._openAboutFile)

        self.settings_button = QPushButton("\u2699")
        self.settings_button.setObjectName("IconButton")
        self.settings_button.setFixedSize(30, 30)
        self.settings_button.clicked.connect(self.handle_settings_clicked)

        self.close_button = QPushButton("\u2715")
        self.close_button.setObjectName("IconButton")
        self.close_button.setFixedSize(30, 30)
        self.close_button.clicked.connect(self.handle_close_clicked)

        header_layout.addWidget(image_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch(1)
        header_layout.addWidget(self.about_button)
        header_layout.addWidget(self.settings_button)
        header_layout.addWidget(self.close_button)
        return header_layout

    def _build_bottom_layout(self):
        bottom_layout = QHBoxLayout()

        status_label = QLabel("Dev by: SkodaUa team")
        status_label.setObjectName("DevLabel")

        info_label = QLabel(APP_VERSION)
        info_label.setObjectName("DevLabel")

        bottom_layout.addWidget(status_label)
        bottom_layout.addStretch()
        bottom_layout.addWidget(info_label)

        return bottom_layout

    def _build_section_title(self, text):
        label = QLabel(text)
        label.setObjectName("SectionTitle")
        return label

    def _build_preparation_group(self):
        group = QFrame()
        group.setObjectName("GroupPanel")

        layout = QVBoxLayout(group)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        self.template_row = FileInputRow("1", "Report template" , allow_multiple=False)
        self.reports_row = FileInputRow("2", "User reports", allow_multiple=True)
        self.explanations_row = FileInputRow("3", "Explanation docs", allow_multiple=True)

        layout.addWidget(self.template_row)
        layout.addWidget(self.reports_row)
        layout.addWidget(self.explanations_row)

        prepare_button = QPushButton("Prepare data")
        prepare_button.setObjectName("SecondaryButton")

        prepare_button.clicked.connect(self._handePrepareBtnClicked)
        layout.addWidget(prepare_button)

        return group

    def _build_generation_group(self):
        group = QFrame()
        group.setObjectName("GroupPanel")

        layout = QVBoxLayout(group)
        layout.setContentsMargins(12, 12, 12, 12)

        top_row = QHBoxLayout()
        top_row.setSpacing(14)

        number_badge = QLabel("4")
        number_badge.setObjectName("NumberBadge")
        number_badge.setFixedSize(26, 26)
        number_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_label = QLabel("Report generation setup:")
        title_label.setObjectName("FieldTitle")

        self.generation_clear_button = QPushButton("\u2715")
        self.generation_clear_button.setObjectName("ClearButton")
        self.generation_clear_button.setFixedSize(30, 30)
        self.generation_clear_button.clicked.connect(self.handle_generation_clear_clicked)

        top_row.addWidget(number_badge)
        top_row.addWidget(title_label, 1)
        top_row.addWidget(self.generation_clear_button)

        self.prompt_input = QTextEdit()
        self.prompt_input.setObjectName("PromptInput")
        self.prompt_input.setPlaceholderText("Additional prompt for the AI...")

        self.language_combo = QComboBox()
        self.language_combo.setObjectName("LanguageCombo")
        self.language_combo.addItems(self.currentSettings.REPORT_LANGUAGES_VARIANTS)

        self.generation_status_label = QLabel("Status: not started")
        self.generation_status_label.setObjectName("StatusLabel")
        self.generation_status_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        layout.addLayout(top_row)
        layout.addWidget(self.prompt_input)
        layout.addWidget(self.language_combo)
        layout.addWidget(self.generation_status_label)

        return group

    def handle_settings_clicked(self):
        self.settings_window.show()

    def handle_close_clicked(self):
        self.close()

    def handle_generation_clear_clicked(self):
        self.prompt_input.clear()
        self.language_combo.setCurrentIndex(0)
        #self.generation_status_label.setText("Status: not started")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()

    def _handePrepareBtnClicked(self):
        #Connecting Ui to Bc logic
        self.mainWindowLogic.set_new_inputs( self.template_row.selected_files,
                                             self.reports_row.selected_files,
                                             self.explanations_row.selected_files)

        self.mainWindowLogic.prepareUserInputs()

    def _runReportGeneration(self):
        prompt:str = self.prompt_input.toPlainText()
        report_language:str = self.language_combo.currentText()
        report_style:str = self.settings_window.get_current_settings().current_report_style

        self.mainWindowLogic.runReportGeneration(prompt, report_language, report_style, self.changeAppStatus)

    def _openAboutFile(self):
        try:
            diePath = self.thisAppPath
            fileName = "about.html"
            fullPath = os.path.join(diePath, fileName)

            webbrowser.open(fullPath)

        except Exception as e:
            messagebox.showerror("Pay Attention!", "Couldn't found About file!")
            print(e)

    def changeAppStatus(self, newStatus):
        self.generation_status_label.setText(newStatus)
        QApplication.processEvents()
