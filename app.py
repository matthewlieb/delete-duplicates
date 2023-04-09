# Import required libraries
from tkinter.filedialog import askdirectory
from tkinter import Tk
import os
import hashlib
from pathlib import Path

# Prevent the tkinter GUI from appearing
Tk().withdraw()

# Prompt user for folder with dialog box
file_path = askdirectory(title="Please select a folder: ")

# List all files inside root
list_all_files = os.walk(file_path)

# Create empty dictionary to check for unique files
unique_files = dict()

# Loop through files in root
for root, folders, files, in list_all_files:
    for file in files:
        # Get file path and hash file for each file
        file_path = Path(os.path.join(root, file))
        hash_file = hashlib.md5(open(file_path,'rb').read()).hexdigest()

        # If unique file is not in dictionary, add it
        if hash_file not in unique_files:
            unique_files[hash_file] = file_path
        # If unique file is in dictionary, delete file
        else:
            os.remove(file_path)
            print(f"{file_path} has been deleted.")
