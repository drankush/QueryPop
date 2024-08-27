import webbrowser
import subprocess
import sys
import pyperclip
import time
from pynput.keyboard import Key, Controller
import pyautogui
from config_handler import load_config
import tkinter as tk
from tkinter import messagebox

config = load_config()

class BrowserManager:
    def __init__(self):
        webbrowser.register('new-window', None, NewWindowBrowser('new-window'))

    def show_browser_window(self, text, instruction_prompt):
        user_message = f"{instruction_prompt}\n\n{text}"
        pyperclip.copy(user_message)

        web_version = config.PREFER_WEBVERSION.lower()
        if web_version == "chatgpt":
            url = "https://chat.openai.com/"
        elif web_version == "claude":
            url = "https://claude.ai/new"
        elif web_version == "gemini":
            url = "https://gemini.google.com/"
        elif web_version == "meta":
            url = "https://meta.ai/"
        else:
            print("Invalid PREFER_WEBVERSION in config.py.")
            return

        try:
            webbrowser.get('new-window').open(url)
        except Exception as e:
            print(f"Error opening browser: {e}")

class NewWindowBrowser(webbrowser.GenericBrowser):
    def open(self, url, new=2, autoraise=True):
        input_delay = int(config.INPUT_DELAY)

        try:
            window_bounds = [int(x.strip()) for x in config.BROWSER_WINDOW_SIZE[1:-1].split(',')]
            width = window_bounds[2] - window_bounds[0]
            height = window_bounds[3] - window_bounds[1]
        except Exception as e:
            print(f"Error parsing BROWSER_WINDOW_SIZE from config.py: {e}")
            width = 400
            height = 700

        if sys.platform == 'win32':  # Windows
            try:
                # Open Chrome with the specified URL
                chrome_cmd = f'start chrome --new-window "{url}"'
                process = subprocess.run(chrome_cmd, shell=True, capture_output=True)

                # Check for errors
                if process.returncode != 0:
                    # Check if Chrome is not found in the path
                    if "not found" in process.stderr.decode('utf-8').lower():
                        # Display error popup if Chrome is not found
                        root = tk.Tk()
                        root.withdraw()  # Hide the main Tkinter window
                        messagebox.showerror("Error", "Google Chrome not found. Please install it or add it to your PATH.")
                        root.destroy()
                        return

                # Wait for the window to open
                time.sleep(2)

                # Get the current active window and resize
                window = pyautogui.getActiveWindow()
                window.resizeTo(width, height)

                # Wait for specified input delay
                time.sleep(input_delay)

                # Create a keyboard controller
                keyboard = Controller()

                # Additional actions based on web version
                web_version = config.PREFER_WEBVERSION.lower()
                if web_version == "claude":
                    for _ in range(10):  # Press tab 10 times
                        keyboard.press(Key.tab)
                        keyboard.release(Key.tab)

                # Simulate Ctrl+V to paste (for all versions)
                with keyboard.pressed(Key.ctrl):
                    keyboard.press('v')
                    keyboard.release('v')

                # Short pause
                time.sleep(0.5)

                # Claude-specific: Press Tab after pasting
                if web_version == "claude":
                    keyboard.press(Key.tab)
                    keyboard.release(Key.tab)

                # Simulate Enter for all versions
                keyboard.press(Key.enter)
                keyboard.release(Key.enter)

            except Exception as e:
                print(f"Error automating browser on Windows: {e}")
        else:
            print("Web version is currently only supported on macOS and Windows.")
