from tkinter import *
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
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
    files = filedialog.askopenfilenames(filetypes = (("object files","*.obj"),("all files","*.*")))
    for file in files:
        # run joseph processing code
        mesh = trimesh.load(file)

        # Get the bounding box min and max values
        min_val, max_val = mesh.bounds[0], mesh.bounds[1]
        max_range = max(max_val - min_val)
        center = (min_val + max_val) / 2.0
        
        # Generate the base grid, scale it, and perform the scan
        base_grid = generate_base_grid(cube_size=16, num_rotations=54)
        scaled_grid = scale_grid(base_grid, scale=1.0)
        inside_points, outside_points = perform_scan(mesh, scaled_grid, center)

        # Save scan output to a file (you can modify this path if needed)
        save_scan_output_to_file(inside_points, inside_points, filename=f"{file}_scan_output.txt")
        # add file to app data
        continue
        
    files_listbox.delete(0, END)
    for name in data_files:
        files_listbox.insert('end', name)

# Function to browse for SD card destination
def browse_sd_card():
    global sd_card_path
    sd_card_path = filedialog.askdirectory()
    if sd_card_path:
        sd_card_label.config(text=f"SD Card: {sd_card_path.split('/')[-1]}")

# Function to transfer selected files to the SD card
def transfer_files():
    if not sd_card_path:
        messagebox.showerror("Error", "No SD card selected.")
        return

    selected_files = files_listbox.curselection()
    if not selected_files:
        messagebox.showerror("Error", "No files selected.")
        return

    for i in selected_files:
        file_name = files_listbox.get(i)
        file_path = os.path.join(data_folder, file_name)
        shutil.copy(file_path, sd_card_path)
    
    messagebox.showinfo("Success", "Files transferred successfully!")


### LAYOUT ###
# Create the main window
root = Tk()
# root.title("Clash of Plans Cave Catalog")
root.title(" ")
root.geometry("750x600")
current_folder = initialdir = os.path.abspath(os.getcwd())
data_folder = os.path.abspath(os.getcwd()) + "/cave_data"

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
    with open("cave_data/" + name) as current_file:
        cave_title = current_file.readline()
    files_listbox.insert('end', cave_title)
files_listbox.pack(pady=3, fill=BOTH, expand=True)

file_source = Image.open("/Users/thomasjohnson/Documents/UVA/Capstone/capstoneComputer/fileicon.jpg")
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
