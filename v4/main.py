# main.py
import sys
import threading
import tkinter as tk
from pynput import keyboard
from pynput.keyboard import Controller, Key
from pystray import Icon as tk_icon, Menu, MenuItem
from PIL import Image, ImageTk

from config_handler import load_config, get_resource_path
from clipboard_utils import get_selected_text
from ui_manager import UIManager
from utils import quit_application, show_about, open_config


config = load_config()

# Global variables
INSTRUCTION_PROMPT = None
shortcut_detected = threading.Event()  

class Application:
    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry("1x1")
        self.ui_manager = UIManager(self.root)


    def listen_for_shortcut(self):
        keyboard_controller = Controller()

        def on_activate(self):
            print("Shortcut detected from listener thread!")
            # Detect the operating system
            if sys.platform == 'darwin':  # macOS
                copy_shortcut = (Key.cmd, 'c')
            else:  # Windows or Linux
                copy_shortcut = (Key.ctrl, 'c')
            
            # Simulate the copy shortcut
            with keyboard_controller.pressed(copy_shortcut[0]): #commented for debugging
                keyboard_controller.press(copy_shortcut[1])
                keyboard_controller.release(copy_shortcut[1])
                print("Simulated pressing of Cntrl+C")

            # Wait for a short period to ensure the clipboard is updated
            import time
            time.sleep(0.1)
            
            shortcut_detected.set()
            self.root.after(0, lambda: self.ui_manager.show_popup(get_selected_text()))

        # Pass 'self' to on_activate:
        with keyboard.GlobalHotKeys({config.APPLICATION_SHORTCUT: lambda *args: on_activate(self)}) as h: 
            h.join() 






    def run(self):
        image_path = get_resource_path("querypop_logo_main.png")
        image = Image.open(image_path)
        resized_image = image.resize((64, 64))
        tk_image = ImageTk.PhotoImage(resized_image)

        icon = tk_icon("QP", image, "QueryPop", menu=Menu(
            MenuItem("Open Config", open_config),
            MenuItem("About", show_about),
            MenuItem("Quit", quit_application),
        ))
        icon.run_detached()

        listener_thread = threading.Thread(target=self.listen_for_shortcut, daemon=True)
        listener_thread.start()

        self.root.mainloop()

if __name__ == "__main__":
    app = Application()
    app.run()




