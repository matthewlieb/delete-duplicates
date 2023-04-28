import os
import hashlib
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, 
                              QFileDialog, QMessageBox, QProgressBar, QDialog, QComboBox, QHBoxLayout, QGroupBox, QFormLayout)
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QIcon
from send2trash import send2trash

# Deletion thread class to handle file deletion in a separate thread
class DeletionThread(QThread):
    progress_signal = pyqtSignal(int)
    error_signal = pyqtSignal(str)

    def __init__(self, folder_path, file_types, move_to_trash):
        super().__init__()
        self.folder_path = folder_path
        self.file_types = file_types
        self.move_to_trash = move_to_trash

    def run(self):
        try:
            list_all_files = list(os.walk(self.folder_path))
        except Exception as e:
            self.error_signal.emit(f"An error occurred while accessing the folder: {e}")
            return

        unique_files = dict()
        total_files = sum([len(files) for root, folders, files in list_all_files])

        for root, folders, files in list_all_files:
            for file in files:
                file_path = Path(os.path.join(root, file))
                file_ext = file_path.suffix.lower()

                if self.file_types and file_ext not in self.file_types:
                    continue

                try:
                    hash_file = hashlib.md5(open(file_path, 'rb').read()).hexdigest()
                except Exception as e:
                    self.error_signal.emit(f"An error occurred while processing the file '{file_path}': {e}")
                    return

                if hash_file not in unique_files:
                    unique_files[hash_file] = file_path
                else:
                    try:
                        if self.move_to_trash:
                            send2trash(str(file_path))
                            print(f"{file_path} has been moved to trash.")
                        else:
                            os.remove(str(file_path))
                            print(f"{file_path} has been deleted.")
                    except Exception as e:
                        self.error_signal.emit(f"An error occurred while moving the file '{file_path}' to trash: {e}")
                        return

                self.progress_signal.emit(1)

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setGeometry(100, 100, 400, 200)

        layout = QVBoxLayout()
        self.setLayout(layout)

        file_types_label = QLabel("File types to scan for duplicates (leave empty for all):")
        layout.addWidget(file_types_label)

        self.file_types_entry = QLineEdit()
        layout.addWidget(self.file_types_entry)

        duplicate_handling_label = QLabel("How to handle duplicate files:")
        layout.addWidget(duplicate_handling_label)

        self.duplicate_handling_combobox = QComboBox()
        self.duplicate_handling_combobox.addItem("Move to trash")
        self.duplicate_handling_combobox.addItem("Delete permanently")
        layout.addWidget(self.duplicate_handling_combobox)

        buttons_layout = QHBoxLayout()

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_settings)
        buttons_layout.addWidget(save_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_button)

        layout.addLayout(buttons_layout)

    def save_settings(self):
        self.accept()

class DuplicateDeleteApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up the user interface
        self.init_ui()

        self.file_types = set()
        self.move_to_trash = True

    def init_ui(self):
        # Set up the main widget and layout
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # Create a menu bar with a Help menu
        menu_bar = self.menuBar()
        help_menu = menu_bar.addMenu("Help")
        help_action = help_menu.addAction("Instructions")
        help_action.triggered.connect(self.show_help)

        # Create a group box for the folder path
        folder_group = QGroupBox("Folder")
        layout.addWidget(folder_group)

        folder_layout = QFormLayout()
        folder_group.setLayout(folder_layout)

        # Create and place label for the folder path
        self.folder_path_entry = QLineEdit()
        folder_layout.addRow("Folder Path:", self.folder_path_entry)

        # Create and place button to browse for folder
        browse_button = QPushButton(QIcon("browse.ico"), "Browse", self)
        browse_button.clicked.connect(self.browse_folder)
        folder_layout.addRow(browse_button)

        # Create a group box for the action buttons
        action_group = QGroupBox("Actions")
        layout.addWidget(action_group)

        action_layout = QHBoxLayout()
        action_group.setLayout(action_layout)

        # Create and place button to delete duplicate files
        delete_button = QPushButton(QIcon("delete.ico"), "Delete Duplicate Files", self)
        delete_button.clicked.connect(self.move_duplicates_to_trash)
        action_layout.addWidget(delete_button)

        # Create and place settings button
        settings_button = QPushButton(QIcon("settings.ico"), "Settings", self)
        settings_button.clicked.connect(self.open_settings)
        action_layout.addWidget(settings_button)

        # Create and place progress bar
        self.progressbar = QProgressBar()
        layout.addWidget(self.progressbar)

        # Set up the main window
        self.setWindowTitle("Duplicate Delete")
        self.setWindowIcon(QIcon("logo.ico"))
        self.setGeometry(100, 100, 500, 250)
        self.setStyleSheet("QGroupBox { font-weight: bold; }")

    def show_help(self):
        help_dialog = QDialog(self)
        help_dialog.setWindowTitle("Instructions")
        help_dialog.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()
        help_dialog.setLayout(layout)

        instructions = (
            "<h3>Duplicate Delete</h3>"
            "<p>Duplicate Delete helps you find and remove duplicate files from a selected folder.</p>"
            "<h4>How to use the app:</h4>"
            "<ol>"
            "<li>Click 'Browse' to choose a folder.</li>"
            "<li>(Optional) Configure file type and deletion settings in 'Settings':</li>"
            "<ul>"
            "<li>In 'File types to scan for duplicates', enter a comma-separated list of file extensions (e.g., .jpg, .png) to only search for duplicates among those file types. Leave it empty to search all file types.</li>"
            "<li>Select 'Move to trash' or 'Delete permanently' to decide how to handle duplicate files.</li>"
            "</ul>"
            "<li>Click 'Delete Duplicate Files' to start the process.</li>"
            "<li>Review the progress bar and wait for the completion message.</li>"
            "</ol>"
        )

        instructions_label = QLabel(instructions)
        instructions_label.setWordWrap(True)
        layout.addWidget(instructions_label)

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(help_dialog.accept)
        layout.addWidget(ok_button)

        help_dialog.exec_()

    def browse_folder(self):
            folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
            self.folder_path_entry.setText(folder_path)

    def move_duplicates_to_trash(self):
        folder_path = self.folder_path_entry.text()
        if not folder_path:
            QMessageBox.warning(self, "Warning", "Please select a folder before proceeding.")
            return

        confirmation = QMessageBox.question(self, "Confirmation", "Are you sure you want to move duplicate files to trash? This action cannot be undone.",
                                            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if confirmation == QMessageBox.No:
            return

        self.deletion_thread = DeletionThread(folder_path, self.file_types, self.move_to_trash)
        self.deletion_thread.progress_signal.connect(self.update_progress_bar)
        self.deletion_thread.finished.connect(self.deletion_completed)
        self.deletion_thread.error_signal.connect(self.show_error_message)
        self.deletion_thread.start()

    # Function to update the progress bar
    def update_progress_bar(self, progress):
        self.progressbar.setValue(self.progressbar.value() + progress)

    # Function to show completion message
    def deletion_completed(self):
        QMessageBox.information(self, "Complete", "Duplicate files have been processed.")

    # Function to show error messages
    def show_error_message(self, error_message):
        QMessageBox.critical(self, "Error", error_message)

    # Function to open settings dialog
    def open_settings(self):
        settings_dialog = SettingsDialog(self)
        settings_dialog.file_types_entry.setText(", ".join(self.file_types))
        settings_dialog.duplicate_handling_combobox.setCurrentIndex(0 if self.move_to_trash else 1)

        result = settings_dialog.exec_()
        if result == QDialog.Accepted:
            self.file_types = {ftype.strip().lower() for ftype in settings_dialog.file_types_entry.text().split(",") if ftype.strip()}
            self.move_to_trash = settings_dialog.duplicate_handling_combobox.currentIndex() == 0

if __name__ == '__main__':
    app = QApplication([])
    app.setStyle("Fusion")
    duplicate_delete_app = DuplicateDeleteApp()
    duplicate_delete_app.show()
    app.exec_()
