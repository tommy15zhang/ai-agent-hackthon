import os

folder_path = input("Path to folder to be sorted:")
files = os.listdir(folder_path)

# Import inside the function to avoid circular import
def process_files():
    import Read_file  # Delayed import to avoid circular dependency

    commands = Read_file.AI_Response(folder_path)
    print(commands)
    Read_file.execute_commands(commands, folder_path)

process_files()

