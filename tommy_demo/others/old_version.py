import os
import shutil
import json
from openai import OpenAI
import pymupdf4llm

client = OpenAI()

# Define the downloads directory
DOWNLOADS_DIR = os.path.expanduser("~/Desktop/Test")
OUTPUT_DIR = os.path.join(DOWNLOADS_DIR, "Organized_Files")

# Ensure the output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_immediate_structure(directory):
    """Returns the immediate structure of the directory as a string."""
    structure = ""
    entries = sorted(os.listdir(directory))
    for entry in entries:
        path = os.path.join(directory, entry)
        if os.path.isdir(path):
            structure += f"{entry}/\n"
            subentries = sorted(os.listdir(path))
            for subentry in subentries:
                structure += f"    {subentry}\n"
        else:
            structure += f"{entry}\n"
    return structure


def extract_text_from_pdf(file_path, num_pages=3):
    """Extracts text from the first 'num_pages' pages of a PDF file."""
    try:
        # Convert the PDF to Markdown
        md_text = pymupdf4llm.to_markdown(file_path)
        # Split the Markdown text into pages
        pages = md_text.split('\f')  # '\f' is the page break character in PDFs
        # Return text from the first 'num_pages' pages
        return ''.join(pages[:num_pages])
    except Exception as e:
        print(f"Error extracting text from {file_path}: {e}")
        return ""

def classify_file_with_gpt(file_name, directory_structure):
    """Uses GPT to classify files into broader categories based on their content and directory structure."""
    prompt = (
        "You are an intelligent document classifier. Based on the provided directory structure and the filename, "
        "determine the most appropriate broad category for this document. "
        "Respond only with a JSON object in the format: {\"Category\": \"<Category Name>\"}.\n\n"
        f"Directory Structure:\n{directory_structure}\n\n"
        f"Filename: {file_name}\n\n"
        "Classify the document and return JSON only."
    )
    try:
        completion = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": prompt}
            ]
        )
        response_content = completion.choices[0].message.content.strip()
        return json.loads(response_content)
    except Exception as e:
        print(f"Error classifying text with GPT: {e}")
        return {"Category": "Miscellaneous"}

def organize_files():
    """Organizes files in Downloads based on GPT-4 classification."""
    directory_structure = get_immediate_structure(DOWNLOADS_DIR)
    for file_name in os.listdir(DOWNLOADS_DIR):
        if file_name.startswith('.'):
            print(f"Skipping hidden file: {file_name}")
            continue
        file_path = os.path.join(DOWNLOADS_DIR, file_name)

        if os.path.isfile(file_path):
            print(f"Processing file: {file_name}")
            # Get classification from GPT-4
            classification = classify_file_with_gpt(file_name, directory_structure)
            category = classification.get("Category", "Miscellaneous")

            # Create category folder
            category_folder = os.path.join(OUTPUT_DIR, category)
            os.makedirs(category_folder, exist_ok=True)

            new_file_path = os.path.join(category_folder, file_name)

            shutil.move(file_path, new_file_path)
            print(f"Moved: {file_name} -> {new_file_path}")
        else:
            print(f"Skipping non-file item: {file_name}")
            
if __name__ == "__main__":
    print("\n--- Before Organizing: Downloads Folder Structure ---")
    print(get_immediate_structure(DOWNLOADS_DIR))
    print("\n--- Organizing Files ---")
    organize_files()
    print("\n--- After Organizing: Organized Files Folder Structure ---")
    print(get_immediate_structure(OUTPUT_DIR))