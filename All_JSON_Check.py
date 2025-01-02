import json
import filelock
import os
import subprocess
import sys

def JSON_check_step(path, question_topic):
    def is_valid_json(question):
        try:
            json.loads(question)
            return True
        except json.JSONDecodeError:
            return False

    def extract_questions(file_path):
        questions = []
        with open(file_path, 'r') as file:
            lines = file.readlines()

        current_question = ""
        in_question = False
        for line in lines:
            for idx, char in enumerate(line):
                if (char == '{') and not in_question:
                    in_question = True
                    current_question = char
                elif (char == '}') and in_question and (line[idx - 1] == '\n'):
                    current_question += char
                    questions.append(current_question.strip())
                    in_question = False
                    current_question = ""
                elif in_question:
                    current_question += char

        return questions

    def check_questions(file_path):
        questions = extract_questions(file_path)
        results = []
        for question in questions:
            is_valid = is_valid_json(question)
            results.append(is_valid)
        return results

    files = [
        "MCQ_Generated.txt",
        "DNDQ_Generated.txt",
        "FITBQ_Generated.txt"
    ]

    for file in files:
        json_file_path = os.path.join(path, file)
        lock_file_path = json_file_path + '.lock'
        lock = filelock.FileLock(lock_file_path)

        max_attempts = 5
        attempt = 0

        while attempt < max_attempts:
            with lock:
                if file == "DNDQ_Generated.txt":
                    question_generator_script = "DND_Question_Generator.py"
                elif file == "MCQ_Generated.txt":
                    question_generator_script = "MC_Question_Generator.py"
                elif file == "FITBQ_Generated.txt":
                    question_generator_script = "FITB_Question_Generator.py"
                else:
                    raise ValueError("Unsupported file name.")

                question_generator_script_path = os.path.join(path, question_generator_script)
                python_interpreter = sys.executable

                subprocess.run([python_interpreter, question_generator_script_path, question_topic], check=True, shell=True)

                results = check_questions(json_file_path)
                counter_true_q = sum(results)

                if counter_true_q >= 10:
                    break

                attempt += 1

        if attempt >= max_attempts:
            print(f"Exceeded maximum number of attempts for {file}")
            return False

    print("JSON Check completed for all files.")
    return True

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise ValueError("Please provide the question_topic argument.")

    question_topic = sys.argv[1]
    path = r"C:\Users\matth\OneDrive\Desktop\AI_Gamification_Python-main\Elmer\Daniel_JSON_Files_Elmer"

    everything_good = JSON_check_step(path, question_topic)
    print("Check if everything was good: " + str(everything_good))
