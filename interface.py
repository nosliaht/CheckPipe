import configparser
from pathlib import Path

from PyQt6.QtCore import Qt, QFileSystemWatcher
from PyQt6.QtGui import QAction, QFont, QColor
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
    QTextEdit,
    QFrame,
    QSizePolicy,
    QDialog,
)

from check import analyze_ini_file


SETTINGS_FILE = "settings.ini"
LANGUAGE_FILES = {
    "PT": "PT.ini",
    "EN": "EN.ini",
}
COLOR_FILE = "color.ini"
INTERFACE_FILE = "interface.ini"


class LogWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Log")
        self.resize(900, 500)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

    def append(self, text: str):
        self.output.append(text)

    def clear(self):
        self.output.clear()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.config = configparser.ConfigParser()
        self.translations = configparser.ConfigParser()
        self.colors = configparser.ConfigParser()
        self.interface_config = configparser.ConfigParser()

        self.log_window = LogWindow(self)
        self.file_watcher = QFileSystemWatcher(self)
        self.file_watcher.fileChanged.connect(self.handle_file_changed)

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

        table_frame = QFrame()
        table_frame.setObjectName("Card")
        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(16, 16, 16, 16)
        table_layout.setSpacing(10)

        self.table_label = QLabel()
        self.table_label.setObjectName("SectionLabel")

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels([
            "INI Name",
            "Pipe Count",
            "Folder",
            "Last Valid ID",
            "Status",
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
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

        table_layout.addWidget(self.table_label)
        table_layout.addWidget(self.table)

        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(0, 0, 0, 0)
        footer_layout.addStretch()

        self.run_button = QPushButton()
        self.run_button.setObjectName("PrimaryButton")
        self.run_button.clicked.connect(self.process_files)
        footer_layout.addWidget(self.run_button, 0, Qt.AlignmentFlag.AlignRight)

        root_layout.addWidget(table_frame, 1)
        root_layout.addLayout(footer_layout)

    def create_menu(self):
        menu_bar = self.menuBar()

        self.file_menu = menu_bar.addMenu("")
        self.language_menu = menu_bar.addMenu("")
        self.interface_menu = menu_bar.addMenu("")
        self.view_menu = menu_bar.addMenu("")
        self.help_menu = menu_bar.addMenu("")

        self.add_files_action = QAction(self)
        self.add_files_action.triggered.connect(self.add_ini_files)

        self.remove_selected_action = QAction(self)
        self.remove_selected_action.triggered.connect(self.remove_selected_rows)

        self.clear_all_action = QAction(self)
        self.clear_all_action.triggered.connect(self.clear_all_rows)

        self.show_log_action = QAction(self)
        self.show_log_action.triggered.connect(self.show_log_window)

        self.exit_action = QAction(self)
        self.exit_action.triggered.connect(self.close)

        self.lang_pt_action = QAction("Português", self)
        self.lang_pt_action.triggered.connect(lambda: self.change_language("PT"))

        self.lang_en_action = QAction("English", self)
        self.lang_en_action.triggered.connect(lambda: self.change_language("EN"))

        self.about_action = QAction(self)
        self.about_action.triggered.connect(self.show_about)

        self.file_menu.addAction(self.add_files_action)
        self.file_menu.addAction(self.remove_selected_action)
        self.file_menu.addAction(self.clear_all_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.exit_action)

        self.language_menu.addAction(self.lang_pt_action)
        self.language_menu.addAction(self.lang_en_action)

        self.size_actions = []
        for size_text in self.get_available_sizes():
            action = QAction(size_text, self)
            action.triggered.connect(lambda checked=False, s=size_text: self.change_window_size(s))
            self.interface_menu.addAction(action)
            self.size_actions.append(action)

        self.view_menu.addAction(self.show_log_action)
        self.help_menu.addAction(self.about_action)

    def apply_styles(self):
        font = QFont("Segoe UI", 10)
        self.setFont(font)

        window_background = self.color("window_background")
        surface_background = self.color("surface_background")
        surface_border = self.color("surface_border")
        primary_text = self.color("primary_text")
        accent = self.color("accent")
        accent_hover = self.color("accent_hover")
        accent_pressed = self.color("accent_pressed")
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

            QDialog {{
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

            QLabel#SectionLabel {{
                font-size: 14px;
                font-weight: 700;
                color: {primary_text};
            }}

            QPushButton {{
                border: none;
                border-radius: 10px;
                padding: 10px 18px;
                font-weight: 600;
                min-height: 22px;
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

            QTextEdit, QTableWidget {{
                background-color: {input_background};
                border: 1px solid {input_border};
                border-radius: 10px;
                padding: 6px;
                color: {primary_text};
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
        """)

    def update_texts(self):
        self.setWindowTitle(self.tr("window_title"))
        self.log_window.setWindowTitle(self.tr("log_window_title"))

        self.run_button.setText(self.tr("run_check"))
        self.table_label.setText(self.tr("files_table"))

        self.table.setHorizontalHeaderLabels([
            self.tr("column_ini_name"),
            self.tr("column_pipe_count"),
            self.tr("column_folder"),
            self.tr("column_last_valid_id"),
            self.tr("column_status"),
        ])

        self.file_menu.setTitle(self.tr("menu_file"))
        self.language_menu.setTitle(self.tr("menu_language"))
        self.interface_menu.setTitle(self.tr("menu_interface"))
        self.view_menu.setTitle(self.tr("menu_view"))
        self.help_menu.setTitle(self.tr("menu_help"))

        self.add_files_action.setText(self.tr("add_files"))
        self.remove_selected_action.setText(self.tr("remove_selected"))
        self.clear_all_action.setText(self.tr("clear_all"))
        self.show_log_action.setText(self.tr("show_log"))
        self.exit_action.setText(self.tr("exit"))
        self.about_action.setText(self.tr("about"))

    def show_log_window(self):
        self.log_window.show()
        self.log_window.raise_()
        self.log_window.activateWindow()

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

    def add_watch_path(self, file_path: str):
        paths = self.file_watcher.files()
        if file_path not in paths and Path(file_path).exists():
            self.file_watcher.addPath(file_path)

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
            folder_name = Path(file_path).parent.name

            if self.find_row_by_path(file_path) != -1:
                continue

            row = self.table.rowCount()
            self.table.insertRow(row)

            name_item = QTableWidgetItem(ini_name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)

            pipe_value = self.get_saved_pipe_count(ini_name)
            pipe_item = QTableWidgetItem(str(pipe_value) if pipe_value != "" else "")

            folder_item = QTableWidgetItem(folder_name if folder_name else "-")
            folder_item.setData(Qt.ItemDataRole.UserRole, file_path)
            folder_item.setFlags(folder_item.flags() & ~Qt.ItemFlag.ItemIsEditable)

            result_item = QTableWidgetItem("-")
            result_item.setFlags(result_item.flags() & ~Qt.ItemFlag.ItemIsEditable)

            status_item = QTableWidgetItem("-")
            status_item.setFlags(status_item.flags() & ~Qt.ItemFlag.ItemIsEditable)

            self.table.setItem(row, 0, name_item)
            self.table.setItem(row, 1, pipe_item)
            self.table.setItem(row, 2, folder_item)
            self.table.setItem(row, 3, result_item)
            self.table.setItem(row, 4, status_item)

            self.add_watch_path(file_path)
            self.process_row(row, from_watcher=False)

    def find_row_by_path(self, file_path: str) -> int:
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 2)
            if item and item.data(Qt.ItemDataRole.UserRole) == file_path:
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
        self.process_row(item.row(), from_watcher=False)

    def set_result_style(self, item: QTableWidgetItem, mode: str):
        success_color = QColor(self.color("success"))
        warning_color = QColor(self.color("warning"))
        error_color = QColor(self.color("error"))
        normal_color = QColor(self.color("primary_text"))

        if mode == "success":
            item.setForeground(success_color)
        elif mode == "warning":
            item.setForeground(warning_color)
        elif mode == "error":
            item.setForeground(error_color)
        else:
            item.setForeground(normal_color)

    def process_row(self, row: int, from_watcher: bool = False):
        ini_name_item = self.table.item(row, 0)
        pipe_count_item = self.table.item(row, 1)
        folder_item = self.table.item(row, 2)
        result_item = self.table.item(row, 3)
        status_item = self.table.item(row, 4)

        if not ini_name_item or not pipe_count_item or not folder_item or not result_item or not status_item:
            return

        ini_name = ini_name_item.text().strip()
        pipe_text = pipe_count_item.text().strip()
        file_path = folder_item.data(Qt.ItemDataRole.UserRole)

        if not pipe_text.isdigit() or int(pipe_text) < 1:
            result_item.setText("-")
            status_item.setText(self.tr("invalid_config"))
            self.set_result_style(status_item, "warning")
            self.log_window.append(f"[{ini_name}] {self.tr('error_missing_pipe_count')}")
            return

        pipe_count = int(pipe_text)
        self.set_saved_pipe_count(ini_name, pipe_count)

        analysis = analyze_ini_file(file_path, pipe_count)

        if analysis["error_message"]:
            result_item.setText(
                str(analysis["last_valid_id"]) if analysis["last_valid_id"] is not None else "-"
            )
            status_item.setText(self.tr("broken"))
            self.set_result_style(status_item, "error")
            self.log_window.append(f"[{ini_name}] {self.tr('broken_file')}: {analysis['error_message']}")
            return

        if analysis["is_broken"]:
            result_item.setText(
                str(analysis["last_valid_id"]) if analysis["last_valid_id"] is not None else "-"
            )
            status_item.setText(self.tr("broken"))
            self.set_result_style(status_item, "error")
            self.log_window.append(f"[{ini_name}] {self.tr('broken_file')}")
            return

        if analysis["last_valid_id"] is None:
            result_item.setText("-")
            status_item.setText(self.tr("not_found"))
            self.set_result_style(status_item, "warning")
            self.log_window.append(f"[{ini_name}] {self.tr('no_valid_id_found')}")
            return

        result_item.setText(str(analysis["last_valid_id"]))
        status_item.setText(self.tr("ok"))
        self.set_result_style(result_item, "success")
        self.set_result_style(status_item, "success")

        if from_watcher:
            self.log_window.append(f"[{ini_name}] {self.tr('auto_updated')}: {analysis['last_valid_id']}")
        else:
            self.log_window.append(f"[{ini_name}] {self.tr('last_valid_id')}: {analysis['last_valid_id']}")

    def handle_file_changed(self, changed_path: str):
        row = self.find_row_by_path(changed_path)
        if row != -1:
            self.add_watch_path(changed_path)
            self.process_row(row, from_watcher=True)

    def remove_selected_rows(self):
        selected_rows = sorted(
            {index.row() for index in self.table.selectionModel().selectedRows()},
            reverse=True
        )

        for row in selected_rows:
            folder_item = self.table.item(row, 2)
            if folder_item:
                file_path = folder_item.data(Qt.ItemDataRole.UserRole)
                if file_path in self.file_watcher.files():
                    self.file_watcher.removePath(file_path)
            self.table.removeRow(row)

    def clear_all_rows(self):
        for file_path in list(self.file_watcher.files()):
            self.file_watcher.removePath(file_path)

        self.table.setRowCount(0)
        self.log_window.clear()

    def process_files(self):
        if self.table.rowCount() == 0:
            QMessageBox.information(self, self.tr("information"), self.tr("no_files_loaded"))
            return

        for row in range(self.table.rowCount()):
            self.process_row(row, from_watcher=False)

    def show_about(self):
        QMessageBox.information(
            self,
            self.tr("about"),
            self.tr("about_text"),
        )