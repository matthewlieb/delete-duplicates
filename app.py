# Import required libraries
import os
import hashlib
from pathlib import Path
from tkinter import Tk, Label, Entry, Button, filedialog
from tkinter import messagebox
from tkinter.ttk import Progressbar
from send2trash import send2trash

# Function that goes identifies duplicate files and moves them to trash
def move_duplicates_to_trash():
    # get folder, get all files in folder, create empty dict
    folder_path = folder_path_entry.get()
    list_all_files = list(os.walk(folder_path))
    unique_files = dict()

    # initialize progress bar
    total_files = sum([len(files) for root, folders, files in list_all_files])
    progressbar["maximum"] = total_files

    # loop through all folders and files
    for root, folders, files, in list_all_files:
        for file in files:
            # get file path and unique hash for each file
            file_path = Path(os.path.join(root, file))
            hash_file = hashlib.md5(open(file_path, 'rb').read()).hexdigest()
            
            # add unique file ash to dictionary key and filepath to value
            if hash_file not in unique_files:
                unique_files[hash_file] = file_path
            # if hash for file is already in dict, move file to trash
            else:
                send2trash(str(file_path))
                print(f"{file_path} has been moved to trash.")
            # move progress bar forward
            progressbar.step(1)
            app.update()
    # show message when process is complete and reset progress bar
    messagebox.showinfo("Complete", "Duplicate files have been moved to trash.")
    progressbar["value"] = 0

# function to ask prompt for directory and insert the path into the text entry
def browse_folder():
    folder_path = filedialog.askdirectory()
    folder_path_entry.delete(0, 'end')
    folder_path_entry.insert(0, folder_path)

# create GUI and give it a title
app = Tk()
app.title("Duplicate Delete")

# Create and place label for the folder path
folder_path_label = Label(app, text="Folder Path:")
folder_path_label.grid(row=0, column=0, padx=5, pady=5)

folder_path_entry = Entry(app, width=50)
folder_path_entry.grid(row=0, column=1, padx=5, pady=5)

# Create and place button and to browse for folder which calls browse_folder command when clicked
browse_button = Button(app, text="Browse", command=browse_folder)
browse_button.grid(row=0, column=2, padx=5, pady=5)

delete_button = Button(app, text="Delete Duplicate Files", command=move_duplicates_to_trash)
delete_button.grid(row=1, column=0, columnspan=3, pady=10)

# Create and place progress bar
progressbar = Progressbar(app, orient="horizontal", length=300, mode="determinate")
progressbar.grid(row=2, column=0, columnspan=3, padx=10, pady=10)

app.mainloop()
