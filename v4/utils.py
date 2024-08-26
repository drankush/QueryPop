# utils.py
import os
import sys
import subprocess
from config_handler import get_config_path
from tkinter import messagebox


def quit_application():
    os._exit(0)

def show_about():
    messagebox.showinfo("About QueryPop", """
        Developer Information:
        Developed by: Dr. Ankush
        🌐 www.drankush.com
        ✉️ querypop@drankush.com

        License:
        MIT
    """)

def open_config():
    config_path = get_config_path()
    if sys.platform == "win32":
        os.startfile(config_path)
    else:
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, config_path])