import os

folder_path = "C:/Users/jacky/Desktop/Test files" 
files = os.listdir(folder_path)



api_key = os.environ.get("OPENAI_API_KEY")

from openai import OpenAI



def AI_response(files):
    exm_files = ['birthday1.psd', 'Speech.docx', 'Speech.pptx']

    client = OpenAI()
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
        {"role": "system", "content": "You are an assistant that helps organize files into themed folders based on their names."},
        {"role": "user", "content": "Generate a list of shell commands to create folders and move the files I send into appropriate themes based on their names. Thr output only consists of commands, seperated by \\n. Ignore any folders inside the folder."},
        {"role": "user", "content": f"{', '.join(exm_files)}"},
        {"role": "assistant", "content": "mkdir Speeches\\n mkdir Birthdays\\n mv Speech.docx\\n mv birthday1.psd Birthdays/\\n mv Speech.pptx/\\n"},
        {"role": "user", "content": f"Here is a list of files:\n{', '.join(files)}"},
        ]
    )

    return(completion.choices[0].message.content)