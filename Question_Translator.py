import json
import os
import openai
import filelock
import sys

with open('api_key.txt', 'r') as file:
    file_contents = file.read()
openai.api_key = file_contents

def translate_questions(path, question_topic):
    files = [
        "MCQ_Generated.txt",
        "DNDQ_Generated.txt",
        "FITBQ_Generated.txt"
    ]

    def get_question_by_number(file_path, question_number):
        questions = []
        in_question = False
        column_stack = []
        current_question = []

        with open(file_path, 'r') as file:
            for line in file:
                for index, char in enumerate(line):
                    if char == '{':
                        if not in_question:
                            in_question = True
                            column_stack.append(index)
                            current_question.append(char)
                        else:
                            current_question.append(char)
                    elif char == '}':
                        if in_question and column_stack and column_stack[-1] == index:
                            column_stack.pop()
                            current_question.append(char)
                            if not column_stack:
                                in_question = False
                                questions.append(''.join(current_question))
                                current_question = []
                        else:
                            current_question.append(char)
                    elif in_question:
                        current_question.append(char)

        return questions

    def determine_question_type(file_path):
        if 'MC' in file_path:
            return 'MC'
        elif 'DND' in file_path:
            return 'DND'
        elif 'FITB' in file_path:
            return 'FITB'
        else:
            return 'Unknown'

    def translate_to_spanish(json_data):
        prompt = (
                "translate the following JSON content to Spanish. Ensure that all keys and values,including answer options, are translated. Respond with the questions formatted as JSON objects. Leave all python keywords in english:\n\n" + json.dumps(
            json_data, indent=4)
        )
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a translator."},
                {"role": "user", "content": prompt}
           ],
            max_tokens=2048,
            temperature=0.3,
            response_format={ "type": "json_object" }
        )
        translation = response.choices[0].message['content'].strip()
        return json.loads(translation)

    def wrap_question_data(question_data, question_type):
        if question_type == 'MC':
            return {"multiplechoice": [question_data]}
        elif question_type == 'DND':
            return {"draganddrop": [question_data]}
        elif question_type == 'FITB':
            return {"completeblankspace": [question_data]}
        else:
            return question_data

    for file in files:
        file_path = os.path.join(path, file)
        question_type = determine_question_type(file_path)

        questions = get_question_by_number(file_path, 10)  # Get all questions (assuming 10 per type)
        for i, question in enumerate(questions, start=1):
            json_filename = f"Question{i}_{question_type}.json"
            save_path = os.path.join(path, json_filename)

            question_data = {
                "title": f"Question {i}",
                "question": json.loads(question)
            }

            translated_question_data = translate_to_spanish(question_data)
            wrapped_question_data = wrap_question_data(translated_question_data, question_type)

            with open(save_path, 'w') as json_file:
                json.dump(wrapped_question_data, json_file, indent=4)

            print(f"Translated and wrapped question {i} saved to {save_path}")

    print("Question translation completed.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise ValueError("Please provide the question_topic argument.")

    question_topic = sys.argv[1]
    path = r"C:\Users\matth\OneDrive\Desktop\AI_Gamification_Python-main\Elmer\Daniel_JSON_Files_Elmer"

    translate_questions(path, question_topic)
