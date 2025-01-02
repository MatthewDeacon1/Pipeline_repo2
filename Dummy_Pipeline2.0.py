import subprocess
import os
import time
import json
from datetime import datetime
from filelock import FileLock

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
        print("Pipeline is executed")

        # Update the last run time after running the pipeline
        update_run_time(user, module, timestamps)
        save_timestamps(timestamps)
    else:
        print(f"Pipeline for {user} in {module} was run less than a minute ago. Skipping execution.")
