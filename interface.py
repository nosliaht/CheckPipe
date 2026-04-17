import configparser
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QFont
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QFileDialog,
    QMessageBox,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
    QComboBox,
    QTextEdit,
    QFrame,
    QSizePolicy,
)

from check import get_last_valid_id


SETTINGS_FILE = "settings.ini"
LANGUAGE_FILES = {
    "PT": "PT.ini",
    "EN": "EN.ini",
}
COLOR_FILE = "color.ini"
INTERFACE_FILE = "interface.ini"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.config = configparser.ConfigParser()
        self.translations = configparser.ConfigParser()
        self.colors = configparser.ConfigParser()
        self.interface_config = configparser.ConfigParser()

        self.load_settings()
        self.load_color_config()
        self.load_interface_config()

        self.current_language = self.config.get("General", "language", fallback="PT")
        self.current_window_size = self.config.get("General", "window_size", fallback="1080x720")

        self.load_language(self.current_language)

        self.build_ui()
        self.apply_window_size()
        self.apply_styles()
        self.update_texts()

    def load_settings(self):
        if Path(SETTINGS_FILE).exists():
            self.config.read(SETTINGS_FILE, encoding="utf-8")

        if "General" not in self.config:
            self.config["General"] = {}

        if "IniFiles" not in self.config:
            self.config["IniFiles"] = {}

        if "language" not in self.config["General"]:
            self.config["General"]["language"] = "PT"

        if "window_size" not in self.config["General"]:
            self.config["General"]["window_size"] = "1080x720"

        self.save_settings()

    def save_settings(self):
        with open(SETTINGS_FILE, "w", encoding="utf-8") as file:
            self.config.write(file)

    def load_language(self, language_code: str):
        file_name = LANGUAGE_FILES.get(language_code, "PT.ini")
        self.translations = configparser.ConfigParser()
        self.translations.read(file_name, encoding="utf-8")

    def load_color_config(self):
        if Path(COLOR_FILE).exists():
            self.colors.read(COLOR_FILE, encoding="utf-8")

        if "Colors" not in self.colors:
            self.colors["Colors"] = {
                "window_background": "#eef4fb",
                "surface_background": "#ffffff",
                "surface_border": "#d8e1eb",
                "primary_text": "#102a43",
                "secondary_text": "#486581",
                "accent": "#2563eb",
                "accent_hover": "#1d4ed8",
                "accent_pressed": "#1e40af",
                "button_secondary": "#64748b",
                "button_secondary_hover": "#475569",
                "button_secondary_pressed": "#334155",
                "table_header_background": "#dbeafe",
                "table_header_text": "#102a43",
                "table_grid": "#d9e2ec",
                "table_selected_background": "#bfdbfe",
                "table_selected_text": "#0f172a",
                "input_background": "#ffffff",
                "input_border": "#cbd5e1",
                "result_background": "#f8fafc",
                "success": "#166534",
                "warning": "#b45309",
                "error": "#b91c1c",
            }

            with open(COLOR_FILE, "w", encoding="utf-8") as file:
                self.colors.write(file)

    def load_interface_config(self):
        if Path(INTERFACE_FILE).exists():
            self.interface_config.read(INTERFACE_FILE, encoding="utf-8")

        if "WindowSizes" not in self.interface_config:
            self.interface_config["WindowSizes"] = {
                "1080x720": "1080x720",
                "1280x720": "1280x720",
                "1366x768": "1366x768",
                "1600x900": "1600x900",
                "1920x1080": "1920x1080",
            }

            with open(INTERFACE_FILE, "w", encoding="utf-8") as file:
                self.interface_config.write(file)

    def tr(self, key: str) -> str:
        return self.translations.get("Texts", key, fallback=key)

    def color(self, key: str, fallback: str = "#000000") -> str:
        return self.colors.get("Colors", key, fallback=fallback)

    def get_available_sizes(self):
        if "WindowSizes" not in self.interface_config:
            return ["1080x720"]

        return list(self.interface_config["WindowSizes"].values())

    def parse_size(self, size_text: str):
        try:
            width_text, height_text = size_text.lower().split("x")
            return int(width_text), int(height_text)
        except Exception:
            return 1080, 720

    def apply_window_size(self):
        width, height = self.parse_size(self.current_window_size)
        self.setWindowTitle(self.tr("window_title"))
        self.setFixedSize(width, height)

    def build_ui(self):
        self.create_menu()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(18, 18, 18, 18)
        root_layout.setSpacing(14)

        header_frame = QFrame()
        header_frame.setObjectName("Card")
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 18, 20, 18)
        header_layout.setSpacing(8)

        self.title_label = QLabel()
        self.title_label.setObjectName("TitleLabel")

        self.subtitle_label = QLabel()
        self.subtitle_label.setObjectName("SubtitleLabel")
        self.subtitle_label.setWordWrap(True)

        header_layout.addWidget(self.title_label)
        header_layout.addWidget(self.subtitle_label)

        controls_frame = QFrame()
        controls_frame.setObjectName("Card")
        controls_layout = QHBoxLayout(controls_frame)
        controls_layout.setContentsMargins(16, 14, 16, 14)
        controls_layout.setSpacing(10)

        self.add_files_button = QPushButton()
        self.add_files_button.setObjectName("PrimaryButton")
        self.add_files_button.clicked.connect(self.add_ini_files)

        self.run_button = QPushButton()
        self.run_button.setObjectName("PrimaryButton")
        self.run_button.clicked.connect(self.process_files)

        self.remove_selected_button = QPushButton()
        self.remove_selected_button.setObjectName("SecondaryButton")
        self.remove_selected_button.clicked.connect(self.remove_selected_rows)

        self.clear_all_button = QPushButton()
        self.clear_all_button.setObjectName("SecondaryButton")
        self.clear_all_button.clicked.connect(self.clear_all_rows)

        self.language_label = QLabel()
        self.language_combo = QComboBox()
        self.language_combo.addItems(["PT", "EN"])
        self.language_combo.setCurrentText(self.current_language)
        self.language_combo.currentTextChanged.connect(self.change_language)

        self.window_size_label = QLabel()
        self.window_size_combo = QComboBox()
        self.window_size_combo.addItems(self.get_available_sizes())
        self.window_size_combo.setCurrentText(self.current_window_size)
        self.window_size_combo.currentTextChanged.connect(self.change_window_size)

        controls_layout.addWidget(self.add_files_button)
        controls_layout.addWidget(self.run_button)
        controls_layout.addWidget(self.remove_selected_button)
        controls_layout.addWidget(self.clear_all_button)
        controls_layout.addStretch()
        controls_layout.addWidget(self.window_size_label)
        controls_layout.addWidget(self.window_size_combo)
        controls_layout.addWidget(self.language_label)
        controls_layout.addWidget(self.language_combo)

        content_layout = QHBoxLayout()
        content_layout.setSpacing(14)

        left_frame = QFrame()
        left_frame.setObjectName("Card")
        left_layout = QVBoxLayout(left_frame)
        left_layout.setContentsMargins(16, 16, 16, 16)
        left_layout.setSpacing(10)

        self.table_label = QLabel()
        self.table_label.setObjectName("SectionLabel")

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["INI Name", "Pipe Count", "File Path"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(
            QAbstractItemView.EditTrigger.DoubleClicked
            | QAbstractItemView.EditTrigger.SelectedClicked
            | QAbstractItemView.EditTrigger.EditKeyPressed
        )
        self.table.itemChanged.connect(self.handle_item_changed)
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        left_layout.addWidget(self.table_label)
        left_layout.addWidget(self.table)

        right_frame = QFrame()
        right_frame.setObjectName("Card")
        right_layout = QVBoxLayout(right_frame)
        right_layout.setContentsMargins(16, 16, 16, 16)
        right_layout.setSpacing(10)

        self.results_label = QLabel()
        self.results_label.setObjectName("SectionLabel")

        self.results_output = QTextEdit()
        self.results_output.setReadOnly(True)
        self.results_output.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        right_layout.addWidget(self.results_label)
        right_layout.addWidget(self.results_output)

        content_layout.addWidget(left_frame, 7)
        content_layout.addWidget(right_frame, 5)

        root_layout.addWidget(header_frame)
        root_layout.addWidget(controls_frame)
        root_layout.addLayout(content_layout, 1)

    def create_menu(self):
        menu_bar = self.menuBar()

        self.file_menu = menu_bar.addMenu("")
        self.language_menu = menu_bar.addMenu("")
        self.help_menu = menu_bar.addMenu("")

        self.add_files_action = QAction(self)
        self.add_files_action.triggered.connect(self.add_ini_files)

        self.exit_action = QAction(self)
        self.exit_action.triggered.connect(self.close)

        self.lang_pt_action = QAction("Português", self)
        self.lang_pt_action.triggered.connect(lambda: self.change_language("PT"))

        self.lang_en_action = QAction("English", self)
        self.lang_en_action.triggered.connect(lambda: self.change_language("EN"))

        self.about_action = QAction(self)
        self.about_action.triggered.connect(self.show_about)

        self.file_menu.addAction(self.add_files_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.exit_action)

        self.language_menu.addAction(self.lang_pt_action)
        self.language_menu.addAction(self.lang_en_action)

        self.help_menu.addAction(self.about_action)

    def apply_styles(self):
        font = QFont("Segoe UI", 10)
        self.setFont(font)

        window_background = self.color("window_background")
        surface_background = self.color("surface_background")
        surface_border = self.color("surface_border")
        primary_text = self.color("primary_text")
        secondary_text = self.color("secondary_text")
        accent = self.color("accent")
        accent_hover = self.color("accent_hover")
        accent_pressed = self.color("accent_pressed")
        button_secondary = self.color("button_secondary")
        button_secondary_hover = self.color("button_secondary_hover")
        button_secondary_pressed = self.color("button_secondary_pressed")
        table_header_background = self.color("table_header_background")
        table_header_text = self.color("table_header_text")
        table_grid = self.color("table_grid")
        table_selected_background = self.color("table_selected_background")
        table_selected_text = self.color("table_selected_text")
        input_background = self.color("input_background")
        input_border = self.color("input_border")
        result_background = self.color("result_background")

        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {window_background};
            }}

            QMenuBar {{
                background-color: {surface_background};
                color: {primary_text};
                border-bottom: 1px solid {surface_border};
            }}

            QMenuBar::item {{
                background: transparent;
                padding: 6px 10px;
            }}

            QMenuBar::item:selected {{
                background: {table_header_background};
                border-radius: 6px;
            }}

            QMenu {{
                background-color: {surface_background};
                color: {primary_text};
                border: 1px solid {surface_border};
            }}

            QMenu::item:selected {{
                background-color: {table_header_background};
            }}

            QFrame#Card {{
                background-color: {surface_background};
                border: 1px solid {surface_border};
                border-radius: 14px;
            }}

            QLabel {{
                color: {primary_text};
                border: none;
                background: transparent;
            }}

            QLabel#TitleLabel {{
                font-size: 26px;
                font-weight: 700;
                color: {primary_text};
            }}

            QLabel#SubtitleLabel {{
                font-size: 12px;
                color: {secondary_text};
            }}

            QLabel#SectionLabel {{
                font-size: 14px;
                font-weight: 700;
                color: {primary_text};
            }}

            QPushButton {{
                border: none;
                border-radius: 10px;
                padding: 10px 16px;
                font-weight: 600;
                min-height: 20px;
            }}

            QPushButton#PrimaryButton {{
                background-color: {accent};
                color: white;
            }}

            QPushButton#PrimaryButton:hover {{
                background-color: {accent_hover};
            }}

            QPushButton#PrimaryButton:pressed {{
                background-color: {accent_pressed};
            }}

            QPushButton#SecondaryButton {{
                background-color: {button_secondary};
                color: white;
            }}

            QPushButton#SecondaryButton:hover {{
                background-color: {button_secondary_hover};
            }}

            QPushButton#SecondaryButton:pressed {{
                background-color: {button_secondary_pressed};
            }}

            QComboBox, QTextEdit, QTableWidget {{
                background-color: {input_background};
                border: 1px solid {input_border};
                border-radius: 10px;
                padding: 6px;
                color: {primary_text};
            }}

            QComboBox::drop-down {{
                border: none;
                width: 24px;
            }}

            QHeaderView::section {{
                background-color: {table_header_background};
                color: {table_header_text};
                padding: 10px;
                border: none;
                border-right: 1px solid {surface_border};
                border-bottom: 1px solid {surface_border};
                font-weight: 700;
            }}

            QTableWidget {{
                gridline-color: {table_grid};
                selection-background-color: {table_selected_background};
                selection-color: {table_selected_text};
                alternate-background-color: {result_background};
            }}

            QTableWidget::item {{
                padding: 6px;
            }}

            QTextEdit {{
                background-color: {result_background};
                font-family: Consolas, monospace;
                font-size: 12px;
            }}

            QScrollBar:vertical, QScrollBar:horizontal {{
                background: transparent;
                border: none;
            }}
        """)

    def update_texts(self):
        self.setWindowTitle(self.tr("window_title"))
        self.title_label.setText(self.tr("main_title"))
        self.subtitle_label.setText(self.tr("main_subtitle"))

        self.add_files_button.setText(self.tr("add_files"))
        self.run_button.setText(self.tr("run_check"))
        self.remove_selected_button.setText(self.tr("remove_selected"))
        self.clear_all_button.setText(self.tr("clear_all"))
        self.language_label.setText(self.tr("language"))
        self.window_size_label.setText(self.tr("window_size"))

        self.table_label.setText(self.tr("files_table"))
        self.results_label.setText(self.tr("results"))

        self.table.setHorizontalHeaderLabels([
            self.tr("column_ini_name"),
            self.tr("column_pipe_count"),
            self.tr("column_file_path"),
        ])

        self.file_menu.setTitle(self.tr("menu_file"))
        self.language_menu.setTitle(self.tr("menu_language"))
        self.help_menu.setTitle(self.tr("menu_help"))

        self.add_files_action.setText(self.tr("add_files"))
        self.exit_action.setText(self.tr("exit"))
        self.about_action.setText(self.tr("about"))

    def change_language(self, language_code: str):
        self.current_language = language_code
        self.config["General"]["language"] = language_code
        self.save_settings()
        self.load_language(language_code)
        self.update_texts()

    def change_window_size(self, size_text: str):
        self.current_window_size = size_text
        self.config["General"]["window_size"] = size_text
        self.save_settings()
        self.apply_window_size()

    def get_saved_pipe_count(self, ini_name: str):
        value = self.config["IniFiles"].get(ini_name)
        if value and value.isdigit():
            return int(value)
        return ""

    def set_saved_pipe_count(self, ini_name: str, pipe_count: int):
        self.config["IniFiles"][ini_name] = str(pipe_count)
        self.save_settings()

    def add_ini_files(self):
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            self.tr("select_ini_files"),
            "",
            "INI Files (*.ini);;All Files (*.*)"
        )

        if not file_paths:
            return

        for file_path in file_paths:
            ini_name = Path(file_path).name

            if self.find_row_by_path(file_path) != -1:
                continue

            row = self.table.rowCount()
            self.table.insertRow(row)

            name_item = QTableWidgetItem(ini_name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)

            pipe_value = self.get_saved_pipe_count(ini_name)
            pipe_item = QTableWidgetItem(str(pipe_value) if pipe_value != "" else "")

            path_item = QTableWidgetItem(file_path)
            path_item.setFlags(path_item.flags() & ~Qt.ItemFlag.ItemIsEditable)

            self.table.setItem(row, 0, name_item)
            self.table.setItem(row, 1, pipe_item)
            self.table.setItem(row, 2, path_item)

    def find_row_by_path(self, file_path: str) -> int:
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 2)
            if item and item.text() == file_path:
                return row
        return -1

    def handle_item_changed(self, item: QTableWidgetItem):
        if item.column() != 1:
            return

        ini_name_item = self.table.item(item.row(), 0)
        if not ini_name_item:
            return

        value = item.text().strip()
        if value == "":
            return

        if not value.isdigit() or int(value) < 1:
            QMessageBox.warning(
                self,
                self.tr("warning"),
                self.tr("invalid_pipe_count"),
            )
            self.table.blockSignals(True)
            item.setText("")
            self.table.blockSignals(False)
            return

        ini_name = ini_name_item.text().strip()
        self.set_saved_pipe_count(ini_name, int(value))

    def remove_selected_rows(self):
        selected_rows = sorted(
            {index.row() for index in self.table.selectionModel().selectedRows()},
            reverse=True
        )

        for row in selected_rows:
            self.table.removeRow(row)

    def clear_all_rows(self):
        self.table.setRowCount(0)
        self.results_output.clear()

    def process_files(self):
        if self.table.rowCount() == 0:
            QMessageBox.information(self, self.tr("information"), self.tr("no_files_loaded"))
            return

        self.results_output.clear()

        for row in range(self.table.rowCount()):
            ini_name_item = self.table.item(row, 0)
            pipe_count_item = self.table.item(row, 1)
            file_path_item = self.table.item(row, 2)

            if not ini_name_item or not pipe_count_item or not file_path_item:
                continue

            ini_name = ini_name_item.text().strip()
            pipe_text = pipe_count_item.text().strip()
            file_path = file_path_item.text().strip()

            if not pipe_text.isdigit() or int(pipe_text) < 1:
                self.results_output.append(
                    f"[{ini_name}] {self.tr('error_missing_pipe_count')}"
                )
                continue

            pipe_count = int(pipe_text)
            self.set_saved_pipe_count(ini_name, pipe_count)

            try:
                result = get_last_valid_id(file_path, pipe_count)
                if result is None:
                    self.results_output.append(
                        f"[{ini_name}] {self.tr('no_valid_id_found')}"
                    )
                else:
                    self.results_output.append(
                        f"[{ini_name}] {self.tr('last_valid_id')}: {result}"
                    )
            except Exception as error:
                self.results_output.append(
                    f"[{ini_name}] {self.tr('error')}: {str(error)}"
                )

    def show_about(self):
        QMessageBox.information(
            self,
            self.tr("about"),
            self.tr("about_text"),
        )