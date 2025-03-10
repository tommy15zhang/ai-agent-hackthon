import os
from datetime import datetime
import openai
import shutil

from collections import defaultdict
import threading
# Load environment variables from .env file

# Get OpenAI API key from environment variables
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Function to get metadata of files in a folder
def get_file_metadata(folder_path):
    files_metadata = []
    
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        
        if os.path.isfile(file_path):  # Make sure it's a file
            stats = os.stat(file_path)
            metadata = {
                'name': file_name,
                'date_created': datetime.fromtimestamp(stats.st_ctime),
                'date_modified': datetime.fromtimestamp(stats.st_mtime),
                'date_accessed': datetime.fromtimestamp(stats.st_atime),
                'size': stats.st_size
            }
            files_metadata.append(metadata)
    
    return files_metadata

# Function to send a prompt to ChatGPT for hierarchical categorization
def categorize_files_with_gpt4(prompt):
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that categorizes files into a folder system. You will perform this task with extreme diligence and precision"},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

# Function to prepare prompt for GPT-4
def prepare_prompt(metadata):
    prompt = (
        "Based on the provided files, infer the occupation and activities of the user and then categorize the  files into a well-structured folder system that will be convenient for the user. Do this using their metadata, including name, creation timestamp, modification timestamp last accessed timestamp and size. You may create subfolders or higher order folders as appropriate, potentially including a miscellaneous folder, but make sure no folder contains fewer than 3 items, and avoid folders with too many items."
    )
    
    for file in metadata:
        prompt += (f"File: {file['name']}, Created: {file['date_created']}, Modified: {file['date_modified']}, Accessed: {file['date_accessed']}, Size {file['size']}\n")
    
    prompt += "\nReturn the results in the format:\nFile: <file_name>, Path: <high-level/mid-level/low-level (if needed)>"
    return prompt

# Function to move files into a hierarchical folder structure
def move_files(folder_path, categorized_files):
    folder_contents = defaultdict(list)
    lines = categorized_files.strip().split("\n")
    
    for line in lines:
        if ", Path: " in line:
            file_name, category_path = line.replace("File: ", "").split(", Path: ")
            file_name, category_path = file_name.strip(), category_path.strip()
            folder_contents[category_path].append(file_name)
    
    # Filter out folders with fewer than two files or two subfolders
    valid_folders = {k: v for k, v in folder_contents.items() if len(v) >= 2}
    
    def move_batch():
        for category_path, files in valid_folders.items():
            dest_path = os.path.join(folder_path, *category_path.split('/'))
            os.makedirs(dest_path, exist_ok=True)
            for file_name in files:
                src_file = os.path.join(folder_path, file_name)
                if os.path.isfile(src_file):
                    try:
                        shutil.move(src_file, os.path.join(dest_path, file_name))
                    except Exception as e:
                        print(f"Failed to move {file_name}: {e}")
        messagebox.showinfo("Success", "Files have been reorganized successfully!")
    
    threading.Thread(target=move_batch).start()

# Main function to categorize files and move them
def main(folder_path):
    # Step 1: Get file metadata
    metadata = get_file_metadata(folder_path)
    
    # Step 2: Prepare prompt for GPT-4
    prompt = prepare_prompt(metadata)
    
    # Step 3: Get hierarchical categorization from GPT-4
    categorized_files = categorize_files_with_gpt4(prompt)
    
    # Step 4: Output the categorization
    print("Categorized Files:")
    print(categorized_files)
    
    # Step 5: Ask user if they want the files moved
    move_choice = input("Do you want to move the files to their categorized hierarchy? (yes/no): ").strip().lower()
    
    if move_choice == "yes":
        # Step 6: Move files into the hierarchical folder structure
        move_files_to_hierarchy(folder_path, categorized_files)
    else:
        print("Files were not moved.")
