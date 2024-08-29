import webbrowser
import subprocess
import sys
import pyperclip
import time
from pynput.keyboard import Controller, Key
import pyautogui
from config_handler import load_config
import tkinter as tk
from tkinter import messagebox

config = load_config()

class BrowserManager:
    def __init__(self, ui_manager):
        self.ui_manager = ui_manager
        self.config = load_config()
        webbrowser.register('new-window', None, NewWindowBrowser('new-window', self.config))

    def update_config(self, new_config):
        self.config = new_config
        webbrowser.register('new-window', None, NewWindowBrowser('new-window', self.config))

    def show_browser_window(self, text, instruction_prompt):
        user_message = f"{instruction_prompt}\n\n{text}"
        pyperclip.copy(user_message)

        web_version = self.config.PREFER_WEBVERSION.lower()
        url = self.get_url(web_version)
        if not url:
            return

        try:
            webbrowser.get('new-window').open(url)
        except Exception as e:
            print(f"Error opening browser: {e}")
            self.ui_manager.error_popup(f"Error opening browser: {e}")

    def get_url(self, web_version):
        urls = {
            "chatgpt": "https://chat.openai.com/",
            "claude": "https://claude.ai/new",
            "gemini": "https://gemini.google.com/",
            "meta": "https://meta.ai/",
            "perplexity": "https://www.perplexity.ai/",
            "copilot": "https://copilot.microsoft.com/",
            "mistral": "https://chat.mistral.ai/chat",
            "you": "https://you.com/",
            "blackbox": "https://www.blackbox.ai/"
        }
        if web_version not in urls:
            print(f"Invalid PREFER_WEBVERSION in config.py: {web_version}")
            self.ui_manager.error_popup(f"Invalid PREFER_WEBVERSION in config.py: {web_version}")
            return None
        return urls[web_version]

class NewWindowBrowser(webbrowser.GenericBrowser):
    def __init__(self, name, config):
        super().__init__(name)
        self.config = config

    def open(self, url, new=2, autoraise=True):
        try:
            window_bounds = [int(x.strip()) for x in self.config.BROWSER_WINDOW_SIZE[1:-1].split(',')]
            width = window_bounds[2] - window_bounds[0]
            height = window_bounds[3] - window_bounds[1]
            input_delay = int(self.config.INPUT_DELAY)
        except Exception as e:
            print(f"Error parsing config values: {e}")
            width, height = 400, 700
            input_delay = 1

        if sys.platform == 'win32':  # Windows
            try:
                chrome_cmd = f'start chrome --new-window "{url}"'
                process = subprocess.run(chrome_cmd, shell=True, capture_output=True)

                if process.returncode != 0:
                    if "not found" in process.stderr.decode('utf-8').lower():
                        root = tk.Tk()
                        root.withdraw()
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

                # Claude and ChatGPT-specific: Press Tab after pasting
                if web_version in ["claude", "chatgpt"]:
                    time.sleep(0.5)  # Add a slight delay to ensure proper focus
                    keyboard.press(Key.tab)
                    keyboard.release(Key.tab)

                # Simulate Enter for all versions
                keyboard.press(Key.enter)
                keyboard.release(Key.enter)

            except Exception as e:
                print(f"Error automating browser on Windows: {e}")
        else:
            print("Web version is currently only supported on macOS and Windows.")
