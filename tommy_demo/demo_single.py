import os
import shutil
from openai import OpenAI

client = OpenAI()

# Define the base directory to organize
BASE_DIR = os.path.expanduser("~/Downloads")

def generate_directory_tree(start_path):
    """Generates a visual representation of the directory tree, ignoring hidden files and directories."""
    tree = []
    
    for root, dirs, files in os.walk(start_path):
        # Remove hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        level = root.replace(start_path, '').count(os.sep)
        indent = ' ' * 4 * level
        tree.append(f'{indent}{os.path.basename(root)}/')
        
        sub_indent = ' ' * 4 * (level + 1)
        for f in files:
            if not f.startswith('.'):  # Ignore hidden files
                tree.append(f'{sub_indent}{f}')
    
    return '\n'.join(tree)

def create_gpt_prompt(directory_tree):
    """Creates a prompt for GPT-4 to suggest an organized folder structure."""
    prompt = (
    "You are an intelligent system designed to optimize and organize directory structures. "
    "Based on the provided directory tree, predict the user's occupation and suggest an improved folder hierarchy that categorizes the files appropriately. "
    "Ensure that the proposed structure does not exceed three levels of depth. "
    "Respond only with the proposed folder structure in a hierarchical format.\n\n"
    "If the response is too long, only output as much as you can and continue in the next response."
    "When all files are outputted, write 'END_OF_STRUCTURE' at the end."
    f"Current Directory Tree:\n{directory_tree}\n\n"
    "Proposed Organized Folder Structure:"
    )
    return prompt

def get_gpt_suggestion(prompt):
    """Obtains GPT-4's suggested folder structure iteratively to avoid truncation."""
    full_response = ""
    continuation_prompt = "\nContinue listing from where you left off."

    try:
        while True:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": prompt + full_response + continuation_prompt}
                ]
            )
            new_content = response.choices[0].message.content.strip()

            # Append the new content
            full_response += "\n" + new_content

            # If the output seems complete, stop requesting more
            if 'END_OF_STRUCTURE' in new_content or len(new_content) < 100:
                break

        return full_response.replace('END_OF_STRUCTURE', "").strip()

    except Exception as e:
        print(f"Error obtaining GPT-4 suggestion: {e}")
        return None

def parse_and_organize_files(proposed_structure, base_path):
    """
    Parses the proposed folder structure and organizes files accordingly.

    Parameters:
    - proposed_structure (str): The structured output from GPT.
    - base_path (str): The base directory where files currently reside.
    """
    lines = proposed_structure.strip().split('\n')
    path_stack = {0: base_path}  # Dictionary to track depth-based paths

    for line in lines:
        # Determine indentation level (each level is represented by 4 spaces)
        indent_level = (len(line) - len(line.lstrip(' '))) // 4
        name = line.strip()

        # Determine the parent directory
        parent_dir = path_stack[indent_level]

        # Construct full path
        current_path = os.path.join(parent_dir, name)

        if name.endswith('/'):
            # It's a folder, create it if it doesn't exist
            os.makedirs(current_path, exist_ok=True)
            path_stack[indent_level + 1] = current_path  # Update path tracking
        else:
            # It's a file, find and move it
            original_file_path = find_file(base_path, name)
            if original_file_path:
                shutil.move(original_file_path, current_path)
                print(f"Moved: {original_file_path} -> {current_path}")
            else:
                print(f"File not found: {name}")

def find_file(base_path, filename):
    """
    Recursively searches for a file within the base_path directory.

    Parameters:
    - base_path (str): The directory to search within.
    - filename (str): The name of the file to search for.

    Returns:
    - str: The full path to the file if found; otherwise, None.
    """
    for root, dirs, files in os.walk(base_path):
        if filename in files:
            return os.path.join(root, filename)
    return None


def organize_directory(base_path, execute=False):
    """Main function to organize the directory based on GPT-4's suggestions."""
    directory_tree = generate_directory_tree(base_path)
    print("Current Directory Tree:" + directory_tree)
    print("\n--- Requesting GPT-4 Suggestion ---")
    prompt = create_gpt_prompt(directory_tree)
    proposed_structure = get_gpt_suggestion(prompt)
    print("Proposed Structure Tree:" + proposed_structure)
    if proposed_structure:
        if execute:
            print("\n--- Organizing Files ---")
            parse_and_organize_files(proposed_structure, base_path)
    else:
        print("No proposed structure received from GPT-4o.")

if __name__ == "__main__":
    execute = input("Do you want to make change to your directory? (y/n): ")
    if execute.lower() == 'y':
        execute = True
    else:
        execute = False
    organize_directory(BASE_DIR, execute)
        
        
    
