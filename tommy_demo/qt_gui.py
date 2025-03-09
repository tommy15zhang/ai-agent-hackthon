import sys
import os
import time
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QFileDialog,
    QTreeWidget, QTreeWidgetItem, QSplitter, QTextEdit, QMessageBox, QLabel, QProgressBar
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QThread, pyqtSignal

# Import backend functions
from demo_single import create_gpt_prompt, get_gpt_suggestion, parse_and_organize_files

from tree_structure import generate_directory_tree

class GenerateStructureThread(QThread):
    """Background thread to generate the proposed structure without freezing the UI."""
    progress = pyqtSignal(int)  # Signal for updating progress bar
    result = pyqtSignal(str)    # Signal for returning the GPT response

    def __init__(self, directory):
        super().__init__()
        self.directory = directory

    def run(self):
        """Runs the GPT-4o structure generation in a separate thread."""
        self.progress.emit(20)  # Start progress

        # Simulate a delay for better UI experience
        time.sleep(1)

        self.progress.emit(40)
        directory_tree = generate_directory_tree(self.directory)
        self.progress.emit(60)

        prompt = create_gpt_prompt(directory_tree)
        self.progress.emit(80)

        proposed_structure = get_gpt_suggestion(prompt)
        self.progress.emit(100)

        self.result.emit(proposed_structure)


class DirectoryOrganizerGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Directory Organizer")
        self.setGeometry(200, 100, 1000, 700)
        self.setStyleSheet("background-color: #f4f4f4; font-size: 14px;")

        self.base_dir = ""

        # Main Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Directory Selection
        self.select_dir_button = QPushButton("📂 Select Directory")
        self.select_dir_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 10px; border-radius: 5px;")
        self.select_dir_button.clicked.connect(self.select_directory)
        layout.addWidget(self.select_dir_button)

        # Splitter for better layout
        splitter = QSplitter(Qt.Vertical)

        # Directory Tree View
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabel("Current Directory Structure")
        splitter.addWidget(self.tree_widget)

        # Proposed Structure Display
        self.proposed_structure_display = QTextEdit()
        self.proposed_structure_display.setReadOnly(True)
        self.proposed_structure_display.setStyleSheet("background-color: white; border: 1px solid #ccc; padding: 5px;")
        splitter.addWidget(self.proposed_structure_display)

        layout.addWidget(splitter)

        # Generate Structure Button
        self.generate_structure_button = QPushButton("✨ Generate Proposed Structure")
        self.generate_structure_button.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold; padding: 10px; border-radius: 5px;")
        self.generate_structure_button.clicked.connect(self.start_generate_structure_thread)
        layout.addWidget(self.generate_structure_button)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)

        # Execute Organization Button
        self.execute_button = QPushButton("🚀 Execute Organization")
        self.execute_button.setStyleSheet("background-color: #FF5722; color: white; font-weight: bold; padding: 10px; border-radius: 5px;")
        self.execute_button.clicked.connect(self.execute_organization)
        layout.addWidget(self.execute_button)

    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.base_dir = directory
            self.display_directory_tree(directory)

    def display_directory_tree(self, directory):
        """Populate the QTreeWidget with the directory tree structure."""
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
        """Start a separate thread to generate the proposed structure with progress bar updates."""
        if not self.base_dir:
            QMessageBox.warning(self, "Warning", "Please select a base directory first.")
            return

        # Reset progress bar
        self.progress_bar.setValue(0)

        # Create and start the thread
        self.thread = GenerateStructureThread(self.base_dir)
        self.thread.progress.connect(self.progress_bar.setValue)
        self.thread.result.connect(self.display_proposed_structure)
        self.thread.start()

    def display_proposed_structure(self, proposed_structure):
        """Update the UI with the generated folder structure."""
        self.proposed_structure_display.setPlainText(proposed_structure)

    def execute_organization(self):
        if self.base_dir and self.proposed_structure_display.toPlainText():
            confirm = QMessageBox.question(self, "Confirm Execution", "Are you sure you want to organize files?", QMessageBox.Yes | QMessageBox.No)
            if confirm == QMessageBox.Yes:
                self.progress_bar.setValue(0)
                proposed_structure = self.proposed_structure_display.toPlainText()
                self.progress_bar.setValue(50)
                parse_and_organize_files(proposed_structure, self.base_dir)
                self.progress_bar.setValue(100)
                QMessageBox.information(self, "Success", "Directory organized successfully.")
        else:
            QMessageBox.warning(self, "Warning", "Please generate a proposed structure first.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DirectoryOrganizerGUI()
    window.show()
    sys.exit(app.exec_())
