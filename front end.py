import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QTextEdit, QLabel
from Read_file import AI_Response, encode_resized_image, extract_text, analyze_image
import shutil

class CommandExecutorApp(QWidget):
    def __init__(self):
        super().__init__()

        # Initialize UI
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Command Executor')
        
        # Main layout
        layout = QVBoxLayout()

        # Folder path input
        self.folder_label = QLabel("Enter Folder Path:", self)
        layout.addWidget(self.folder_label)

        self.folder_input = QLineEdit(self)
        layout.addWidget(self.folder_input)

        # Generate commands button
        self.generate_button = QPushButton('Generate Commands', self)
        self.generate_button.clicked.connect(self.generate_commands)
        layout.addWidget(self.generate_button)

        # Text area to display generated commands
        self.commands_output = QTextEdit(self)
        self.commands_output.setReadOnly(True)
        layout.addWidget(self.commands_output)

        # Execute commands button
        self.execute_button = QPushButton('Execute Commands', self)
        self.execute_button.clicked.connect(self.execute_commands)
        layout.addWidget(self.execute_button)

        # Set layout to window
        self.setLayout(layout)

    def generate_commands(self):
        folder_path = self.folder_input.text().strip()
        if not folder_path:
            self.commands_output.setText("Please enter a valid folder path.")
            return
        
        # Import AI_Response locally to avoid circular import
        try:
            from Read_file import AI_Response
            commands = AI_Response(folder_path)
            self.commands_output.setText(commands)
        except Exception as e:
            self.commands_output.setText(f"Error generating commands: {e}")

    def execute_commands(self):
        commands = self.commands_output.toPlainText().strip()
        if not commands:
            self.commands_output.append("\nNo commands to execute.")
            return

        command_list = commands.split('\n')
        folder_path = self.folder_input.text().strip()
        os.chdir(folder_path)

        for command in command_list:
            if command.strip():
                if command.strip().startswith('sh'):
                    exec(command.strip())
                elif command.strip().startswith('mkdir'):
                    os.system(command)

                self.commands_output.append(f"Executed: {command}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CommandExecutorApp()
    window.show()
    sys.exit(app.exec_())
