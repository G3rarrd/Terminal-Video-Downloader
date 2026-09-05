from pathlib import Path
import tkinter as tk

from tkinter import filedialog

def pick_directory_native(initial_dir: str = str(Path.home())) -> str | None:
    root = tk.Tk()
    root.withdraw()          # hide the empty Tk root window
    root.attributes("-topmost", True)  # bring dialog to front
    path = filedialog.askdirectory(initialdir=initial_dir or None)
    root.destroy()
    return path or None