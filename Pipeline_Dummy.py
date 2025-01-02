import sys
def create_module_file(module_number, username):
    # Create the file name based on the input variables
    file_name = f"Module_{module_number}_{username}.txt"

    # Open the file and write the test string
    with open(file_name, 'w') as file:
        file.write("This is a test")

    print(f"File '{file_name}' created successfully.")

if __name__ == "__main__":
    # Ensure that the script receives both arguments from Main_Modulos_Intro_Pages.py
    if len(sys.argv) < 3:
        print("Usage: python Pipeline_Dummy.py <ModuleNumb> <current_user>")
        sys.exit(1)

    # Assign command-line arguments to variables
    module_number = sys.argv[1]
    username = sys.argv[2]

    # Call the function to create the file
    create_module_file(module_number, username)
