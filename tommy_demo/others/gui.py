import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
from demo_single import generate_directory_tree, create_gpt_prompt, get_gpt_suggestion, parse_and_organize_files

def select_directory():
    directory = filedialog.askdirectory()
    if directory:
        base_dir.set(directory)
        # Display the current directory tree
        tree = generate_directory_tree(directory)
        current_tree_display.delete(1.0, tk.END)
        current_tree_display.insert(tk.END, tree)

def generate_proposed_structure():
    directory = base_dir.get()
    if directory:
        tree = generate_directory_tree(directory)
        prompt = create_gpt_prompt(tree)
        proposed_structure = get_gpt_suggestion(prompt)
        proposed_structure_display.delete(1.0, tk.END)
        proposed_structure_display.insert(tk.END, proposed_structure)
    else:
        messagebox.showerror("Error", "Please select a base directory first.")

def execute_organization():
    directory = base_dir.get()
    proposed_structure = proposed_structure_display.get(1.0, tk.END).strip()
    if directory and proposed_structure:
        parse_and_organize_files(proposed_structure, directory)
        messagebox.showinfo("Success", "Directory organized successfully.")
    else:
        messagebox.showerror("Error", "Please generate a proposed structure first.")

# Initialize the main window
root = tk.Tk()
root.title("Directory Organizer")

base_dir = tk.StringVar()

# Directory selection
tk.Label(root, text="Base Directory:").pack()
tk.Entry(root, textvariable=base_dir, width=50).pack()
tk.Button(root, text="Select Directory", command=select_directory).pack()

# Current directory tree display
tk.Label(root, text="Current Directory Tree:").pack()
current_tree_display = scrolledtext.ScrolledText(root, width=80, height=20)
current_tree_display.pack()

# Proposed structure display
tk.Label(root, text="Proposed Structure:").pack()
proposed_structure_display = scrolledtext.ScrolledText(root, width=80, height=20)
proposed_structure_display.pack()

# Buttons to generate and execute
tk.Button(root, text="Generate Proposed Structure", command=generate_proposed_structure).pack()
tk.Button(root, text="Execute Organization", command=execute_organization).pack()

root.mainloop()
