import subprocess

# Initialize the question topic variable
question_topic = "if statements"

# Paths to the question generator scripts
scripts = [
    "MC_Question_Generator1.py",
    "DND_Question_Generator1.py",
    "FITB_Question_Generator1.py"
]

# Run each question generator script
for script in scripts:
    script_path = r"C:\Users\matth\OneDrive\Pipeline_Folder_2\Pipeline Folder"
    subprocess.run(["python", script_path, question_topic])

# Run the JSON Check.py script
subprocess.run(["python", "All_JSON_Check1.py", question_topic])

# Run the Random Question Translator.py script
subprocess.run(["python", "Question_Translator1.py", question_topic])
