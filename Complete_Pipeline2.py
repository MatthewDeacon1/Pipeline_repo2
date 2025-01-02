import subprocess
import os
import json
import threading
import time
from filelock import FileLock
from datetime import datetime, timedelta
class PipelineMethod:
    def __init__(self, progreso_file, processed_file="processed_progress.json"):
        self.progreso_file = progreso_file
        self.processed_file = processed_file
        self.progreso_data = self.load_progress()
        self.processed_progress = self.load_processed_progress()
        self.lock_dir = "pipeline_locks"  # Directory to store lock files
        self.execution_window = timedelta(minutes=5)  # Prevent re-running within 5 minutes
        self.running_flags = {}  # Dictionary to track running status for each user and module combination

        # Create lock directory if it doesn't exist
        if not os.path.exists(self.lock_dir):
            os.makedirs(self.lock_dir)

    def load_progress(self):
        """Load user progress from progreso.json, or return an empty dictionary if the file is empty or invalid."""
        if os.stat(self.progreso_file).st_size == 0:
            print("progreso.json is empty.")
            return {}
        try:
            with open(self.progreso_file, 'r') as file:
                return json.load(file)
        except json.JSONDecodeError:
            print("Error: Invalid JSON format in progreso.json.")
            return {}

    def load_processed_progress(self):
        """Load processed progress data from processed_progress.json, or return an empty dictionary if the file is empty."""
        if not os.path.exists(self.processed_file) or os.stat(self.processed_file).st_size == 0:
            return {}
        try:
            with open(self.processed_file, 'r') as file:
                return json.load(file)
        except json.JSONDecodeError:
            print("Error: Invalid JSON format in processed_progress.json.")
            return {}

    def save_processed_progress(self):
        """Save processed progress data to processed_progress.json."""
        with open(self.processed_file, 'w') as file:
            json.dump(self.processed_progress, file, indent=4)

    def check_and_run_pipeline(self, user):
        """Check each module's Leccion2 for the user and run the pipeline if conditions are met."""
        for mod_num in range(1, 6):
            modulo_key = f"Modulo{mod_num}"
            leccion1_key = "Leccion1"
            leccion2_key = "Leccion2"

            # Check if Leccion1 is completed
            if not self.progreso_data.get(user, {}).get(modulo_key, {}).get(leccion1_key, False):
                continue

            # Skip if this user's Leccion2 is already processed for this module
            if self.processed_progress.get(user, {}).get(modulo_key, {}).get("Leccion2_processed", False):
                continue

            # Check if Leccion2 is unlocked (set to True) and not yet processed
            if self.progreso_data[user][modulo_key].get(leccion2_key):
                # Check if the pipeline is already running for this user/module combination
                if self.running_flags.get(f"{user}_{mod_num}", False):
                    print(f"Skipping pipeline for Modulo{mod_num} and {user}, already running.")
                    continue

                # Set the running flag for this user/module combination to prevent concurrent execution
                self.running_flags[f"{user}_{mod_num}"] = True

                try:
                    print(f"Running Complete_Pipeline2.py for Modulo{mod_num} and {user}")

                    # Mark Leccion2 as processed before running the pipeline
                    self.processed_progress.setdefault(user, {}).setdefault(modulo_key, {})["Leccion2_processed"] = True

                    # Run the pipeline
                    pipeline_script_path = os.path.abspath("Complete_Pipeline2.py")
                    subprocess.run(["python", pipeline_script_path, str(mod_num), user])

                finally:
                    # After pipeline finishes, clear the running flag
                    self.running_flags[f"{user}_{mod_num}"] = False

                    # Record the execution time to prevent repeated runs in a short time frame
                    self.processed_progress.setdefault(user, {}).setdefault(modulo_key, {})["last_execution"] = datetime.now().isoformat()
                    self.save_processed_progress()  # Save progress after completion

    def monitor_progress(self):
        """Continuously monitor progreso.json for new progress updates and trigger the pipeline when needed."""
        while True:
            # Reload progreso_data on each check
            self.progreso_data = self.load_progress()

            for user in self.progreso_data:
                # Run pipeline checks for each user
                self.check_and_run_pipeline(user)

            time.sleep(5)  # Check every 5 seconds

# Start pipeline monitoring in a separate thread
def start_pipeline_monitoring(progreso_file):
    pipeline = PipelineMethod(progreso_file)
    threading.Thread(target=pipeline.monitor_progress, daemon=True).start()

# Define the file to store last run timestamps for each user-module pair
timestamps_file = "pipeline_timestamps.json"
lock_file = "pipeline.lock"

# Initialize the question topic variable
question_topic = "if statements"

def load_timestamps():
    """Load the last run timestamps from the JSON file."""
    if os.path.exists(timestamps_file):
        with open(timestamps_file, 'r') as file:
            return json.load(file)
    return {}

def save_timestamps(timestamps):
    """Save the updated timestamps to the JSON file."""
    with open(timestamps_file, 'w') as file:
        json.dump(timestamps, file, indent=4)

def can_run_pipeline(user, module, timestamps):
    """Check if the pipeline can be run for this user-module pair (only if 1 minute has passed)."""
    last_run_time = timestamps.get(user, {}).get(module)
    if last_run_time:
        last_run = datetime.fromisoformat(last_run_time)
        time_diff = datetime.now() - last_run
        return time_diff.total_seconds() >= 60  # Check if 60 seconds have passed
    return True  # No record means it can run

def update_run_time(user, module, timestamps):
    """Update the last run time for a user-module pair."""
    if user not in timestamps:
        timestamps[user] = {}
    timestamps[user][module] = datetime.now().isoformat()

# Use a file lock to prevent simultaneous access
with FileLock(lock_file):
    timestamps = load_timestamps()
    user = "current_user"  # Replace with dynamic user input if available
    module = "Module1"      # Replace with dynamic module input if available

    # Only run the pipeline if it's been at least 1 minute since the last run for this user-module pair
    if can_run_pipeline(user, module, timestamps):
        # Run the JSON Check.py script
        subprocess.run(["python", "All_JSON_Check.py", question_topic])

        # Run the Random Question Translator.py script
        subprocess.run(["python", "Question_Translator.py", question_topic])

        # Update the last run time after running the pipeline
        update_run_time(user, module, timestamps)
        save_timestamps(timestamps)
    else:
        print(f"Pipeline for {user} in {module} was run less than a minute ago. Skipping execution.")
