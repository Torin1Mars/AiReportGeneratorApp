from PyQt6.QtCore import QPoint, Qt
from PyQt6.QtWidgets import (
    QButtonGroup,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QVBoxLayout, QApplication,
)

from App.supportingData.settingsManager import SettingsManager
from App.WindowsLogic.settings_window_logic import SettingsWindowLogic

class SettingsWindow(QDialog):
    def __init__(self, appSettings: SettingsManager, parent=None,):
        super().__init__(parent)

        self.appSettings:SettingsManager = appSettings

        self._drag_position = QPoint()
        self._setup_screen()

        self.options = {
            "Minimalistic": "Short report style, each chapter should have to 5 sentences size, key facts mostly",
            "Normal": "Medium report style, each chapter should have min 5-10 describing sentences size based on key facts results",
            "Expanded": "Expanded report style, each chapter should have 10 or more sentences based on key facts results and your personal observation opinion about obtained results, should include design advantages and disadvantages"
            }

        self._build_ui()

        self.logic = SettingsWindowLogic(key = self.appSettings.GPT_KEY,
                                         aiModelName = self.appSettings.GPT_MODEL_NAME,
                                         reportStyle = self._get_current_report_style_option())

    def get_current_settings(self)->SettingsWindowLogic:
        return self.logic

    def _get_current_report_style_option(self)->str:
        mode:str = ""

        checkedButtonId = self.style_group.checkedId()
        mode = list(self.options.values())[checkedButtonId]

        return mode

    def _setup_screen(self):
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)

        #Window size
        self.setFixedSize(self.appSettings.SETTINGS_WINDOW_WIDTH, self.appSettings.SETTINGS_WINDOW_HEIGHT)

        #Starting position
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        start_width = int((screen_geometry.width()-self.appSettings.SETTINGS_WINDOW_WIDTH) * 0.5)
        start_height = int((screen_geometry.height()-self.appSettings.SETTINGS_WINDOW_HEIGHT) * 0.5)
        self.move(start_width, start_height)

    def _build_ui(self):
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        container = QFrame()
        container.setObjectName("MainContainer")
        outer_layout.addWidget(container)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        layout.addLayout(self._build_header())

        layout.addWidget(self._build_field_label("AI API key :"))
        self.api_key_input = QLineEdit()
        self.api_key_input.setObjectName("SettingsInput")
        #self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setPlaceholderText("sk-...")
        self.api_key_input.setText(self.appSettings.GPT_KEY)
        layout.addWidget(self.api_key_input)

        layout.addWidget(self._build_field_label("Model name :"))
        self.model_name_input = QLineEdit()
        self.model_name_input.setObjectName("SettingsInput")
        self.model_name_input.setPlaceholderText("e.g. gpt-4o")
        self.model_name_input.setText(self.appSettings.GPT_MODEL_NAME)
        layout.addWidget(self.model_name_input)

        layout.addWidget(self._build_field_label("Report generator style"))
        layout.addLayout(self._build_style_options())

        layout.addStretch(1)
        layout.addLayout(self._build_footer_buttons())

    def _build_header(self):
        header_layout = QHBoxLayout()

        title_label = QLabel("Settings")
        title_label.setObjectName("AppTitle")

        self.close_button = QPushButton("\u2715")
        self.close_button.setObjectName("IconButton")
        self.close_button.setFixedSize(26, 26)
        self.close_button.clicked.connect(self.handle_cancel_clicked)

        header_layout.addWidget(title_label)
        header_layout.addStretch(1)
        header_layout.addWidget(self.close_button)
        return header_layout

    def _build_field_label(self, text):
        label = QLabel(text)
        label.setObjectName("FieldLabel")
        return label

    def _build_style_options(self):
        layout = QVBoxLayout()
        layout.setSpacing(6)

        self.style_group = QButtonGroup(self)

        index = 1
        for option in self.options:
            option_frame = QFrame()
            option_frame.setObjectName("StyleOption")
            option_layout = QHBoxLayout(option_frame)

            radio_button = QRadioButton()
            radio_button.setObjectName("StyleRadio")
            if index == 1:
               radio_button.setChecked(True)

            text_layout = QVBoxLayout()
            text_layout.setSpacing(0)

            name_label = QLabel(option)
            name_label.setObjectName("StyleName")
            description_label = QLabel(self.options[option])
            description_label.setObjectName("StyleDescription")

            text_layout.addWidget(name_label)
            text_layout.addWidget(description_label)

            option_layout.addWidget(radio_button)
            option_layout.addLayout(text_layout)

            self.style_group.addButton(radio_button, index)
            layout.addWidget(option_frame)
            index +=1

        return layout

    def _build_footer_buttons(self):
        button_row = QHBoxLayout()

        cancel_button = QPushButton("Cancel")
        cancel_button.setObjectName("SecondaryOutlineButton")
        cancel_button.clicked.connect(self.handle_cancel_clicked)

        save_button = QPushButton("Save")
        save_button.setObjectName("PrimarySettingsButton")
        save_button.clicked.connect(self.handle_save_clicked)

        button_row.addWidget(cancel_button)
        button_row.addWidget(save_button)
        return button_row

    def handle_cancel_clicked(self):
        self.reject()

    def handle_save_clicked(self):
        self.accept()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()
