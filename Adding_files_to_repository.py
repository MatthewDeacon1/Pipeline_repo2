import os
import subprocess


def git_add_files(repo_path):
    # Change to the repository directory
    os.chdir("C:/Users/matth/OneDrive/Desktop/AI_Gamification_Python-main/Elmer/Daniel_JSON_Files_Elmer")

    # List all files in the repository (ignoring hidden files and directories)
    for root, dirs, files in os.walk(repo_path):
        for file in files:
            # Skip .git directory itself and any ignored files
            if file == ".git" or ".gitignore" in file:
                continue

            # Construct the file path
            file_path = os.path.join(root, file)

            # Print the file path being added
            print(f"Adding {file_path}")

            # Try adding each file to the git repository
            result = subprocess.run(["git", "add", file_path], capture_output=True, text=True)

            # Print the output and errors
            if result.returncode != 0:
                print(f"Error adding {file_path}: {result.stderr}")
            else:
                print(f"Successfully added {file_path}: {result.stdout}")

    # Commit changes after adding files
    result = subprocess.run(["git", "commit", "-m", "Added new files"], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error committing changes: {result.stderr}")
    else:
        print("Successfully committed changes.")


# Provide the path to your Git repository
repo_path = "C:/Users/matth/OneDrive/Desktop/AI_Gamification_Python-main/Elmer/Daniel_JSON_Files_Elmer"
git_add_files(repo_path)
