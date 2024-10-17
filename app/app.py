import tkinter as tk
from tkinter import filedialog, messagebox
import os
import shutil
import psutil

class FileCatalogApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Catalog and Transfer")
        self.root.geometry("500x400")

        self.current_folder = ""
        self.sd_card_path = ""

        self.create_widgets()

    def create_widgets(self):
        browse_button = tk.Button(self.root, text="Browse Files/Folders", command=self.browse_files)
        browse_button.pack(pady=10)

        self.files_listbox = tk.Listbox(self.root, selectmode=tk.MULTIPLE)
        self.files_listbox.pack(pady=10, fill=tk.BOTH, expand=True)

        sd_card_button = tk.Button(self.root, text="Select SD Card", command=self.browse_sd_card)
        sd_card_button.pack(pady=10)

        self.sd_card_label = tk.Label(self.root, text="SD Card: Not selected")
        self.sd_card_label.pack(pady=10)

        transfer_button = tk.Button(self.root, text="Transfer Files", command=self.transfer_files)
        transfer_button.pack(pady=10)

    def browse_files(self):
        folder = filedialog.askdirectory()
        if folder:
            self.current_folder = folder
            self.list_files(folder)

    def list_files(self, folder):
        self.files_listbox.delete(0, tk.END)
        for file in os.listdir(folder):
            self.files_listbox.insert(tk.END, file)

    def browse_sd_card(self):
        self.sd_card_path = filedialog.askdirectory()
        if self.sd_card_path:
            self.sd_card_label.config(text=f"SD Card: {self.sd_card_path}")

    def transfer_files(self):
        if not self.sd_card_path:
            messagebox.showerror("Error", "No SD card selected.")
            return

        selected_indices = self.files_listbox.curselection()
        if not selected_indices:
            messagebox.showerror("Error", "No files selected.")
            return

        for i in selected_indices:
            file_name = self.files_listbox.get(i)
            source_path = os.path.join(self.current_folder, file_name)
            destination_path = os.path.join(self.sd_card_path, file_name)

            if os.path.exists(destination_path):
                overwrite = messagebox.askyesno("Overwrite", f"{file_name} already exists. Overwrite?")
                if not overwrite:
                    continue

            try:
                shutil.copy2(source_path, destination_path)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to copy {file_name}: {str(e)}")
                return

        messagebox.showinfo("Success", "Files transferred successfully!")

    @staticmethod
    def detect_sd_card():
        for partition in psutil.disk_partitions():
            if 'removable' in partition.opts.lower():  # This might not work on all systems
                return partition.mountpoint
        return None

if __name__ == "__main__":
    root = tk.Tk()
    app = FileCatalogApp(root)
    root.mainloop()