import sys
import os
import time
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QFileDialog,
    QTreeWidget, QTreeWidgetItem, QSplitter, QTextEdit, QMessageBox, QLabel, QProgressBar, QHBoxLayout
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from one_folder_tool import flatten_directory

# Import backend functions
from demo_single import create_gpt_prompt, get_gpt_suggestion, parse_and_organize_files

from tree_structure import generate_directory_tree

from Read_file import AI_Response, execute_commands
import dan
class GenerateStructureThread(QThread):
    """Background thread to generate the proposed structure without freezing the UI."""
    progress = pyqtSignal(int)  # Signal for updating progress bar
    result = pyqtSignal(str)    # Signal for returning the GPT response

    def __init__(self, directory, mode):
        super().__init__()
        self.directory = directory
        self.mode = mode

    def run(self):
        """Runs the GPT-4o structure generation in a separate thread."""
        self.progress.emit(20)  # Start progress

        time.sleep(1)  # Simulate delay for better UI experience

        self.progress.emit(40)
        directory_tree = generate_directory_tree(self.directory)
        self.progress.emit(60)

        # Choose prompt generation based on mode
        if self.mode == "name":
            # TODO: Customize create_gpt_prompt for 'name' mode if needed
            prompt = create_gpt_prompt(directory_tree)
            self.progress.emit(80)
            proposed_structure = get_gpt_suggestion(prompt)
          
        elif self.mode == "metadata":
            metadata = dan.get_file_metadata(self.directory)
            prompt = dan.prepare_prompt(metadata)
            proposed_structure = dan.categorize_files_with_gpt4(prompt)
          
        elif self.mode == "content":
            proposed_structure = AI_Response(self.directory)
          
        self.progress.emit(100)

        self.result.emit(proposed_structure)

class DirectoryOrganizerGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Directory Organizer")
        self.setGeometry(200, 100, 1000, 700)
        self.setStyleSheet("background-color: #f4f4f4; font-size: 14px;")

        self.base_dir = ""
        self.mode = "name"  # Default mode

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.select_dir_button = QPushButton("\ud83d\udcc2 Select Directory")
        self.select_dir_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 10px; border-radius: 5px;")
        self.select_dir_button.clicked.connect(self.select_directory)
        layout.addWidget(self.select_dir_button)

        # Mode Selection Buttons
        mode_layout = QHBoxLayout()
        self.name_button = QPushButton("Organize by Name")
        self.metadata_button = QPushButton("Organize by Metadata")
        self.content_button = QPushButton("Organize by Content")

        for btn in [self.name_button, self.metadata_button, self.content_button]:
            btn.setStyleSheet("padding: 8px; border-radius: 4px; background-color: #e0e0e0;")

        self.name_button.clicked.connect(lambda: self.set_mode("name"))
        self.metadata_button.clicked.connect(lambda: self.set_mode("metadata"))
        self.content_button.clicked.connect(lambda: self.set_mode("content"))

        mode_layout.addWidget(QLabel("Choose Organizing Mode:"))
        mode_layout.addWidget(self.name_button)
        mode_layout.addWidget(self.metadata_button)
        mode_layout.addWidget(self.content_button)
        layout.addLayout(mode_layout)

        splitter = QSplitter(Qt.Vertical)

        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabel("Current Directory Structure")
        splitter.addWidget(self.tree_widget)

        self.proposed_structure_display = QTextEdit()
        self.proposed_structure_display.setReadOnly(True)
        self.proposed_structure_display.setStyleSheet("background-color: white; border: 1px solid #ccc; padding: 5px;")
        splitter.addWidget(self.proposed_structure_display)

        layout.addWidget(splitter)

        self.generate_structure_button = QPushButton("\u2728 Generate Proposed Structure")
        self.generate_structure_button.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold; padding: 10px; border-radius: 5px;")
        self.generate_structure_button.clicked.connect(self.start_generate_structure_thread)
        layout.addWidget(self.generate_structure_button)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)

        self.execute_button = QPushButton("\ud83d\ude80 Execute Organization")
        self.execute_button.setStyleSheet("background-color: #FF5722; color: white; font-weight: bold; padding: 10px; border-radius: 5px;")
        self.execute_button.clicked.connect(self.execute_organization)
        layout.addWidget(self.execute_button)
        
         # **New: Add Flatten Directory Button**
        self.flatten_button = QPushButton("\u2699 Flatten Directory")
        self.flatten_button.setStyleSheet("background-color: #9C27B0; color: white; font-weight: bold; padding: 10px; border-radius: 5px;")
        self.flatten_button.clicked.connect(self.flatten_directory)
        layout.addWidget(self.flatten_button)

    def set_mode(self, mode):
        self.mode = mode
        QMessageBox.information(self, "Mode Selected", f"Organizing mode set to: {mode.capitalize()}")

    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.base_dir = directory
            self.display_directory_tree(directory)

    def display_directory_tree(self, directory):
        self.tree_widget.clear()
        tree_structure = generate_directory_tree(directory)
        root_item = QTreeWidgetItem([os.path.basename(directory)])
        self.tree_widget.addTopLevelItem(root_item)

        for line in tree_structure.split("\n"):
            if not line.strip():
                continue
            level = line.count("    ")
            item_text = line.strip()
            item = QTreeWidgetItem([item_text])
            if level == 0:
                root_item.addChild(item)
            else:
                parent = root_item
                for _ in range(level):
                    if parent.childCount() > 0:
                        parent = parent.child(parent.childCount() - 1)
                parent.addChild(item)

        self.tree_widget.expandAll()

    def start_generate_structure_thread(self):
        if not self.base_dir:
            QMessageBox.warning(self, "Warning", "Please select a base directory first.")
            return

        self.progress_bar.setValue(0)
        self.thread = GenerateStructureThread(self.base_dir, self.mode)
        self.thread.progress.connect(self.progress_bar.setValue)
        self.thread.result.connect(self.display_proposed_structure)
        self.thread.start()

    def display_proposed_structure(self, proposed_structure):
        self.proposed_structure_display.setPlainText(proposed_structure)

    def execute_organization(self):
        if self.base_dir and self.proposed_structure_display.toPlainText():
            confirm = QMessageBox.question(self, "Confirm Execution", "Are you sure you want to organize files?", QMessageBox.Yes | QMessageBox.No)
            if confirm == QMessageBox.Yes:
                self.progress_bar.setValue(0)
                proposed_structure = self.proposed_structure_display.toPlainText()

                # Choose organization logic based on mode
                if self.mode == "name":
                    parse_and_organize_files(proposed_structure, self.base_dir)
                elif self.mode == "metadata":
                    dan.move_files(self.base_dir, proposed_structure)
                elif self.mode == "content":
                    execute_commands(proposed_structure, self.base_dir)

                self.progress_bar.setValue(100)
                QMessageBox.information(self, "Success", "Directory organized successfully.")
        else:
            QMessageBox.warning(self, "Warning", "Please generate a proposed structure first.")

    def flatten_directory(self):
        """Calls the external flatten_directory function and updates UI."""
        if not self.base_dir:
            QMessageBox.warning(self, "Warning", "Please select a base directory first.")
            return

        confirm = QMessageBox.question(self, "Confirm Flattening", "Are you sure you want to flatten the directory?", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            self.progress_bar.setValue(0)

            try:
                result = flatten_directory(self.base_dir)  # Call imported function
                self.progress_bar.setValue(100)
                QMessageBox.information(self, "Success", result)
                self.display_directory_tree(self.base_dir)  # Refresh tree view
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to flatten directory: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DirectoryOrganizerGUI()
    window.show()
    sys.exit(app.exec_())
