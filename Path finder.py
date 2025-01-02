import os

absolute_path = r"C:\Users\matth\OneDrive\Desktop\AI_Gamification_Python-main\Elmer\Daniel_JSON_Files_Elmer\Main_Modulos_Intro_Pages.py"
current_working_directory = os.getcwd()

relative_path = os.path.relpath(absolute_path, current_working_directory)
print(relative_path)
