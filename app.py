from tkinter import *
from tkinter import filedialog, messagebox, Listbox
from PIL import Image, ImageTk
from PreprocessingV2 import scan_obj
import os
import shutil


### WIDGET FUNCTIONS ###
# List files in app data
def list_files():
    files = filedialog.askopenfilenames(filetypes = (("all files","*.*")))
    if files:
        files_listbox.delete(0, END)  # Clear the listbox
        for file in os.listdir(os.path.abspath):
            files_listbox.insert(END, file)  # Add files to the listbox

# Browse renderings and process them
def browse_renderings():
    # Open file dialog to select files
    files = filedialog.askopenfilenames(filetypes=(("object files", "*.obj"), ("all files", "*.*")))

    output_folders = []
    for file in files:
        output_folder = scan_obj(file)  # Assuming scan_obj processes the file and returns the output folder path
        output_folders.append(output_folder)

        # Now copy the processed files to the cave_data folder
        for output_folder in output_folders:
            if os.path.exists(output_folder):  # Check if the folder exists
                for file_name in os.listdir(output_folder):  # List all files in the folder
                    source_file = os.path.join(output_folder, file_name)
                    dest_folder = os.path.join(os.getcwd(), "cave_data")  # Target folder where data will be copied
                    dest_file = os.path.join(dest_folder, file_name)

                    # Copy the file to cave_data
                    shutil.copy(source_file, dest_file)
                    print(f"File {file_name} copied to {dest_folder}")
            else:
                print(f"Output folder does not exist: {output_folder}")

    # Clear the Listbox and list files from cave_data folder
    files_listbox.delete(0, END)

    # List all files from the cave_data folder
    cave_data_folder = os.path.join(os.getcwd(), "cave_data")
    if os.path.exists(cave_data_folder):  # Check if the cave_data folder exists
        for file_name in os.listdir(cave_data_folder):
            file_path = os.path.join(cave_data_folder, file_name)

            # Use os.path.relpath to get the part of the file path after 'cave_data'
            relative_path = os.path.relpath(file_path, cave_data_folder)
            files_listbox.insert('end', relative_path)  # Insert the relative file path into the listbox
    else:
        print("cave_data folder not found.")

# Function to clear cave_data folder at start of execution
def clear_cave_data_folder():
    cave_data_folder = os.path.join(os.getcwd(), "cave_data")

    # Check if the cave_data folder exists
    if os.path.exists(cave_data_folder):
        # Remove all files in the folder
        for file_name in os.listdir(cave_data_folder):
            file_path = os.path.join(cave_data_folder, file_name)
            try:
                if os.path.isfile(file_path):  # Check if it's a file
                    os.remove(file_path)  # Delete the file
                elif os.path.isdir(file_path):  # If it's a directory, delete it recursively
                    shutil.rmtree(file_path)
                print(f"Deleted: {file_name}")
            except Exception as e:
                print(f"Error deleting {file_name}: {e}")
    else:
        print("cave_data folder does not exist.")

# Function to browse for SD card destination
def browse_sd_card():
    global sd_card_path
    sd_card_path = filedialog.askdirectory()
    if sd_card_path:
        sd_card_label.config(text=f"SD Card: {sd_card_path.split('/')[-1]}")

# Function to select the SD card path using a file dialog
def select_sd_card():
    global sd_card_path
    sd_card_path = filedialog.askdirectory()
    if sd_card_path:
        messagebox.showinfo("SD Card Selected", f"SD card selected: {sd_card_path}")

# Function to transfer selected files to the SD card
def transfer_files():
    # Check if the SD card path is set
    if not sd_card_path:
        messagebox.showerror("Error", "No SD card selected.")
        return

    # Get selected files from the Listbox
    selected_files = files_listbox.curselection()
    if not selected_files:
        messagebox.showerror("Error", "No files selected.")
        return

    for i in selected_files:
        file_name = files_listbox.get(i)
        file_path = os.path.join(data_folder, file_name)
        # Copy the file to the SD card path
        shutil.copy(file_path, sd_card_path)

    # Show success message if all files are copied
    messagebox.showinfo("Success", "Files transferred successfully!")


### LAYOUT ###
# Create the main window
root = Tk()
# root.title("Clash of Plans Cave Catalog")
root.title(" ")
root.geometry("750x600")
current_folder = initialdir = os.path.abspath(os.getcwd())
data_folder = os.path.join(os.path.abspath(os.getcwd()), "cave_data")
clear_cave_data_folder()
print("Current working directory:", os.getcwd())
# Create all of the main containers
top_frame = Frame(root, pady=3)
center_frame = Frame(root, padx=3, pady=3)
bottom_frame = Frame(root, pady=3)

top_frame.pack(fill=X)
center_frame.pack(fill=BOTH, expand=True)
bottom_frame.pack(fill=X)

# Create top sub frames
top_left_frame = Frame(top_frame)
top_right_frame = Frame(top_frame)

top_left_frame.pack(side=LEFT, fill=X, expand=True)
top_right_frame.pack(side=RIGHT, fill=X)

# Create and place the UI elements for the top frame
list_label = Label(top_left_frame, text="Clash of Plans Cave Catalog", font=("Arial", 16, "bold"))
list_label.pack(anchor=CENTER)

browse_button = Button(top_right_frame, text="Upload Cave", command=browse_renderings)
browse_button.pack(side=RIGHT)

# Create and place the UI elements for the center frame
files_listbox = Listbox(center_frame, selectmode=MULTIPLE)
data_files = os.listdir(data_folder)
for name in data_files:
    file_path = os.path.join("cave_data", name)
    with open(file_path) as current_file:
        cave_title = current_file.readline()
    files_listbox.insert('end', cave_title)
files_listbox.pack(pady=3, fill=BOTH, expand=True)

file_source = Image.open("./fileicon.jpg")
photo = ImageTk.PhotoImage(file_source)
test_button = Button(center_frame, image=photo, borderwidth=0, relief="flat").pack()

# Create bottom sub frames
bottom_left_frame = Frame(bottom_frame, padx=3)
bottom_middle_frame = Frame(bottom_frame, padx=3)
bottom_right_frame = Frame(bottom_frame, padx=3)

bottom_left_frame.pack(side=LEFT, fill=X, expand=True)
bottom_middle_frame.pack(side=LEFT, fill=X, expand=True)
bottom_right_frame.pack(side=RIGHT, fill=X, expand=True)

# Create and place the UI elements for the bottom frame
sd_card_label = Label(bottom_left_frame, text="SD Card: Not selected")
sd_card_label.pack()

sd_card_button = Button(bottom_left_frame, text="Change SD Card", command=browse_sd_card)
sd_card_button.pack()


current_cave_label = Label(bottom_middle_frame, text="Saved Cave: None")
current_cave_label.pack(side=LEFT)

new_cave_label = Label(bottom_right_frame, text="Selected Cave: None")
new_cave_label.pack(side=LEFT)

transfer_button = Button(bottom_right_frame, text="Transfer to SD", command=transfer_files)
transfer_button.pack()

root.mainloop()
