import os
from Read_file import AI_Response
import shutil

folder_path = "C:/Users/jacky/Desktop/Test files" 
files = os.listdir(folder_path)

api_key = os.environ.get("OPENAI_API_KEY")

def execute_commands(commands):
    # Split the input into individual commands based on 'n'
    print(commands)
    command_list = commands.split('\n')
    os.chdir(folder_path)
    
    move_choice = input("Do you want to move the files to their categorized hierarchy? (y/n): ").strip().lower()
    # Execute each command
    if move_choice == "y":
        for command in command_list:
            # Skip empty strings that might appear due to splitting
            if command.strip():
                if command.strip().startswith('sh'):
                    exec(command.strip())
                elif command.strip().startswith ('mkdir'):
                    os.system(command)
                
                print(f"Executed: {command}")
    else:
        print("We dont move then.")

# Example input string
commands = AI_Response(folder_path)
execute_commands(commands)

