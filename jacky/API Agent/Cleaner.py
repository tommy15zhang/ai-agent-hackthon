import os
from Read_file import AI_Response

folder_path = "C:/Users/dcies/Desktop/test_downloads" 
files = os.listdir(folder_path)

def execute_commands(commands):
    # Split the input into individual commands based on 'n'
    command_list = commands.split('\n')
    os.chdir(folder_path)
    # Execute each command
    for command in command_list:
        # Skip empty strings that might appear due to splitting
        if command.strip():
            if command.strip().startswith('mv'):
                command = command.replace('mv', 'move')
                os.system(command)
            elif command.strip().startswith ('mkdir'):
                os.system(command)
            
            print(f"Executed: {command}")

# Example input string
commands = AI_Response(files)
execute_commands(commands)

