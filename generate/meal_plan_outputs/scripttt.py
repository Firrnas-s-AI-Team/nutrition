import os
import shutil

# Define the parent directory
parent_dir = "."  # Change this to your actual folder path

# Loop through all subdirectories
for root, dirs, files in os.walk(parent_dir, topdown=False):
    for file in files:
        # Get full file path
        file_path = os.path.join(root, file)
        # Move the file to the parent directory
        shutil.move(file_path, os.path.join(parent_dir, file))

# Optionally, remove empty subdirectories
for root, dirs, files in os.walk(parent_dir, topdown=False):
    for dir in dirs:
        dir_path = os.path.join(root, dir)
        if not os.listdir(dir_path):  # Check if the directory is empty
            os.rmdir(dir_path)

print("All files moved to the parent directory!")
