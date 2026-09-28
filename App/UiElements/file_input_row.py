from tokenize import String

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFileDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget, QFrame

class FileInputRow(QWidget):
    """Reusable row for a single Preparation field: number badge, title,
    browse/add button, clear button, selected-file list and status label."""

    def __init__(self, number: str, label_text: str,
                 allow_multiple: bool = False, parent=None):
        super().__init__(parent)
        self.allow_multiple = allow_multiple
        self.selected_files: list[str] = []

        self._build_content_ui(number, label_text)


    def _build_content_ui(self, rowNumber: str, labelText: str):
        self.setObjectName("FieldCard")

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(16, 5, 16, 5)

        top_row = QHBoxLayout()

        number_badge = QLabel(rowNumber)
        number_badge.setObjectName("NumberBadge")
        number_badge.setFixedSize(26, 26)
        number_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_label = QLabel(labelText)
        title_label.setObjectName("FieldTitle")

        self.browse_button = QPushButton("Add file")
        self.browse_button.setObjectName("BrowseButton")
        self.browse_button.clicked.connect(self.handle_browse_clicked)

        self.clear_button = QPushButton("\u2715")
        self.clear_button.setObjectName("ClearButton")
        self.clear_button.setFixedSize(30, 30)
        self.clear_button.clicked.connect(self.handle_clear_clicked)

        top_row.addWidget(number_badge)
        top_row.addWidget(title_label, 1)
        top_row.addWidget(self.browse_button)
        top_row.addWidget(self.clear_button)

        bottom_row = QHBoxLayout()

        self.files_label = QLabel("No files selected")
        self.files_label.setObjectName("FilesLabel")

        self.status_label = QLabel("Status: not started")
        self.status_label.setObjectName("StatusLabel")

        bottom_row.addWidget(self.files_label, 1)
        bottom_row.addWidget(self.status_label)

        #divider line
        field_divider = QFrame()
        field_divider.setObjectName("FieldDivider")
        field_divider.setFrameShape(QFrame.Shape.HLine)

        outer_layout.addLayout(top_row)
        outer_layout.addSpacing(20)
        outer_layout.addLayout(bottom_row)
        outer_layout.addWidget(field_divider)

    def handle_browse_clicked(self):
        if self.allow_multiple:
            files, _ = QFileDialog.getOpenFileNames(self, "Select files")
        else:
            file_path, _ = QFileDialog.getOpenFileName(self, "Select file")
            files = [file_path] if file_path else []

        if files:
            self.selected_files = files
            names = ", ".join(path.split("/")[-1] for path in files)
            self.files_label.setText(names)

    def handle_clear_clicked(self):
        self.selected_files = []
        self.files_label.setText("No files selected")
        self.status_label.setText("Status: not started")
