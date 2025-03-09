import os
import shutil
import json
from openai import OpenAI
import pymupdf4llm

# Set your OpenAI API key

# Define the directories
DOWNLOADS_DIR = os.path.expanduser("~/Desktop/Screenshots")
OUTPUT_DIR = os.path.join(DOWNLOADS_DIR, "Organized_Files")
client = OpenAI()

# Ensure the output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

def extract_text_from_pdf(file_path, num_pages=3):
    """Extracts text from the first 'num_pages' pages of a PDF file."""
    try:
        md_text = pymupdf4llm.to_markdown(file_path)
        pages = md_text.split('\f')
        return ''.join(pages[:num_pages])
    except Exception as e:
        print(f"Error extracting text from {file_path}: {e}")
        return ""

def generate_filename_with_gpt(document_content, filename):
    """Generates a descriptive filename using GPT based on document content."""
    prompt = (
        "Based on the provided document content and name, suggest a concise, descriptive and short filename. "
        "Respond only with the suggested filename without any file extension or additional text.\n\n"
        f"Document Name: \n{filename}\n\n Document Content:\n{document_content[:500]}\n\n"  # Limiting to the first 500 characters
        "Suggested Filename:"
    )
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        suggested_filename = response.choices[0].message.content.strip()
        # Remove any invalid characters for filenames
        suggested_filename = "".join(c for c in suggested_filename if c.isalnum() or c in (' ', '_', '-')).rstrip()
        print(f"Suggested Filename: {suggested_filename}")
        return suggested_filename
    except Exception as e:
        print(f"Error generating filename with GPT: {e}")
        return None

def organize_files():
    """Renames and organizes files based on their content using GPT."""
    for file_name in os.listdir(DOWNLOADS_DIR):
        if file_name.startswith('.') | file_name.startswith('mov'):
            print(f"Skipping hidden file: {file_name}")
            continue
        file_path = os.path.join(DOWNLOADS_DIR, file_name)

        if os.path.isfile(file_path):
            print(f"Processing file: {file_name}")
            # Extract content
            if file_name.endswith(".pdf"):
                document_content = extract_text_from_pdf(file_path)
            else:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                        document_content = file.read()
                except Exception as e:
                    print(f"Error reading file {file_name}: {e}")
                    document_content = ""

            if document_content:
                # Generate new filename
                new_filename_base = generate_filename_with_gpt(document_content, file_name)
                
                
                # if new_filename_base:
                #     new_filename = f"{new_filename_base}{os.path.splitext(file_name)[1]}"
                #     new_file_path = os.path.join(OUTPUT_DIR, new_filename)
                #     # Ensure unique filename
                #     counter = 1
                #     while os.path.exists(new_file_path):
                #         new_filename = f"{new_filename_base}_{counter}{os.path.splitext(file_name)[1]}"
                #         new_file_path = os.path.join(OUTPUT_DIR, new_filename)
                #         counter += 1
                #     # Move and rename the file
                #     shutil.move(file_path, new_file_path)
                #     print(f"Renamed and moved: {file_name} -> {new_filename}")
                # else:
                #     print(f"Skipping file due to filename generation failure: {file_name}")
            else:
                print(f"Skipping file due to content extraction failure: {file_name}")
        else:
            print(f"Skipping non-file item: {file_name}")

if __name__ == "__main__":
    print("\n--- Organizing Files ---")
    organize_files()
    print("\n--- Organization Complete ---")
