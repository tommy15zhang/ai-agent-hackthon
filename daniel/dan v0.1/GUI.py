import os
import shutil
import openai
from datetime import datetime
from dotenv import load_dotenv
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from collections import defaultdict
import threading

# Load environment variables
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

def get_file_metadata(folder_path):
    files_metadata = []
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path):
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

def categorize_files_with_gpt4(prompt):
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that categorizes files into a structured hierarchy with proper subfolders, ensuring that no folder has fewer than two files or two subfolders."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

def prepare_prompt(metadata):
    prompt = (
        "Based on the provided files, infer the occupation and activities of the user and categorize the "
        "files into a structured hierarchy, ensuring proper nesting. Do this using their metadata, "
        "including name, creation timestamp, modification timestamp, last accessed timestamp, and size. "
        "Ensure a logical folder structure, avoiding too many top-level folders and preventing folders with fewer than two files or two subfolders."
    )
    for file in metadata:
        prompt += (f"File: {file['name']}, Created: {file['date_created']}, Modified: {file['date_modified']}, "
                   f"Accessed: {file['date_accessed']}, Size: {file['size']}\n")
    prompt += "\nReturn results in the format: File: <file_name>, Path: <folder/subfolder/...>"
    return prompt

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

def browse_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        folder_var.set(folder_path)

def suggest_ordering():
    folder_path = folder_var.get()
    if folder_path:
        metadata = get_file_metadata(folder_path)
        prompt = prepare_prompt(metadata)
        categorized_files = categorize_files_with_gpt4(prompt)
        display_tree(categorized_files)

def display_tree(categorized_files):
    tree.delete(*tree.get_children())
    folder_map = {}
    for line in categorized_files.strip().split("\n"):
        if ", Path: " in line:
            file_name, category_path = line.replace("File: ", "").split(", Path: ")
            file_name, category_path = file_name.strip(), category_path.strip()
            folder_levels = category_path.split('/')
            parent = ""
            for level in folder_levels:
                if level not in folder_map:
                    folder_map[level] = tree.insert(parent, "end", text=level, open=True)
                parent = folder_map[level]
            tree.insert(parent, "end", text=file_name)
    global cached_categorization
    cached_categorization = categorized_files

def confirm_reorder():
    if cached_categorization:
        move_files(folder_var.get(), cached_categorization)

# GUI Setup
root = tk.Tk()
root.title("File Organizer")
root.geometry("700x550")
root.configure(bg="#f5f5f5")

frame = ttk.Frame(root, padding=10)
frame.pack(fill=tk.BOTH, expand=True)

folder_var = tk.StringVar()
cached_categorization = ""

btn_browse = ttk.Button(frame, text="Select Folder", command=browse_folder)
btn_browse.pack(pady=5)

entry_folder = ttk.Entry(frame, textvariable=folder_var, state='readonly', width=60)
entry_folder.pack(pady=5)

btn_suggest = ttk.Button(frame, text="Suggest Ordering", command=suggest_ordering)
btn_suggest.pack(pady=5)

tree = ttk.Treeview(frame)
tree.pack(expand=True, fill=tk.BOTH, pady=10)

btn_confirm = ttk.Button(frame, text="Confirm & Reorder", command=confirm_reorder)
btn_confirm.pack(pady=5)

root.mainloop()
