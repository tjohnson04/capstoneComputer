import tkinter as tk
from tkinter import filedialog, messagebox
import os
import shutil

# Function to browse files or directories
def browse_files():
    folder = filedialog.askopenfilenames(filetypes = (("jpeg files","*.jpg"),("all files","*.*")))
    if folder:
        list_files(folder)

# Function to list files in the selected directory
def list_files(folder):
    files_listbox.delete(0, tk.END)  # Clear the listbox
    for file in os.listdir(folder):
        files_listbox.insert(tk.END, file)  # Add files to the listbox

# Function to browse for SD card destination
def browse_sd_card():
    global sd_card_path
    sd_card_path = filedialog.askdirectory()
    if sd_card_path:
        sd_card_label.config(text=f"SD Card: {sd_card_path}")

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
        file_path = os.path.join(current_folder, file_name)
        shutil.copy(file_path, sd_card_path)
    
    messagebox.showinfo("Success", "Files transferred successfully!")

# Create the main window
root = tk.Tk()
root.title("Clash of Plans Cave Catalog")
root.geometry("500x400")
current_folder = initialdir = os.path.abspath(os.getcwd())

# Create and place the UI elements
browse_button = tk.Button(root, text="Upload New Cave", command=browse_files)
browse_button.pack(pady=10)

files_listbox = tk.Listbox(root, selectmode=tk.MULTIPLE)
files_listbox.pack(pady=10, fill=tk.BOTH, expand=True)

sd_card_button = tk.Button(root, text="Select SD Card", command=browse_sd_card)
sd_card_button.pack(pady=10)

sd_card_label = tk.Label(root, text="SD Card: Not selected")
sd_card_label.pack(pady=10)

transfer_button = tk.Button(root, text="Transfer Files", command=transfer_files)
transfer_button.pack(pady=10)

root.mainloop()
