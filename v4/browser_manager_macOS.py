import webbrowser
import subprocess
import sys
import pyperclip
import time
from pynput.keyboard import Controller, Key
from config_handler import load_config
from tkinter import messagebox


config = load_config()


class BrowserManager:
    def __init__(self, ui_manager):
        self.ui_manager = ui_manager  # Store a reference to UIManager
        self.config = load_config()
        webbrowser.register('new-window', None, NewWindowBrowser('new-window', self.config)) # Pass config to NewWindowBrowser

    def update_config(self, new_config):
        self.config = new_config
        # Update the config for the registered browser
        webbrowser.register('new-window', None, NewWindowBrowser('new-window', self.config)) 

    def show_browser_window(self, text, instruction_prompt):
        user_message = f"{instruction_prompt}\n\n{text}"
        pyperclip.copy(user_message)

        web_version = self.config.PREFER_WEBVERSION.lower() 
        if web_version == "chatgpt":
            url = "https://chat.openai.com/"
        elif web_version == "claude":
            url = "https://claude.ai/new"
        elif web_version == "gemini":
            url = "https://gemini.google.com/"
        elif web_version == "meta":
            url = "https://meta.ai/"
        elif web_version == "perplexity":
            url = "https://www.perplexity.ai/"
        elif web_version == "copilot":
            url = "https://copilot.microsoft.com/"
        elif web_version == "mistral":
            url = "https://chat.mistral.ai/chat"
        elif web_version == "you":
            url = "https://you.com/"
        elif web_version == "blackbox":
            url = "https://www.blackbox.ai/"
        else:
            print("Invalid PREFER_WEBVERSION in config.py.")
            self.ui_manager.error_popup("Invalid PREFER_WEBVERSION in config.py.")  # Show error popup
            return

        try:
            webbrowser.get('new-window').open(url)
        except Exception as e:
            print(f"Error opening browser: {e}")
            self.ui_manager.error_popup(f"Error opening browser: {e}")  # Show error popup

class NewWindowBrowser(webbrowser.GenericBrowser):
    def __init__(self, name, config):
        super().__init__(name)
        self.config = config

    def open(self, url, new=2, autoraise=True):
        try:
            window_bounds = [int(x.strip()) for x in self.config.BROWSER_WINDOW_SIZE[1:-1].split(',')]
            input_delay = int(self.config.INPUT_DELAY)
        except Exception as e:
            print(f"Error parsing BROWSER_WINDOW_SIZE or INPUT_DELAY from config.py: {e}")
            window_bounds = [100, 50, 400, 700]  # Default window bounds
            input_delay = 1  # Default input delay

        if sys.platform == 'darwin':  # macOS
            # Try opening in Chrome first
            chrome_script = f'''
                tell application "Google Chrome"
                    activate
                    make new window
                    set URL of active tab of window 1 to "{url}"
                    set bounds of window 1 to {{{", ".join(map(str, window_bounds))}}}
                    delay {input_delay}
                end tell
            '''
            chrome_process = subprocess.Popen(["osascript", "-e", chrome_script], stderr=subprocess.PIPE)
            stderr_output, _ = chrome_process.communicate()
            chrome_result = chrome_process.returncode

            if chrome_result != 0:
                print("Chrome not found. Trying Safari...")

                safari_script = f'''
                    tell application "Safari"
                        activate
                        tell window 1
                            set current tab to (make new tab)
                            set the URL of the current tab to "{url}"
                        end tell
                        set bounds of window 1 to {{{", ".join(map(str, window_bounds))}}}
                        delay {input_delay}
                    end tell
                '''
                safari_process = subprocess.Popen(["osascript", "-e", safari_script], stderr=subprocess.PIPE)
                stderr_output, _ = safari_process.communicate()
                safari_result = safari_process.returncode

                if safari_result != 0:
                    messagebox.showerror("Browser Error", "Neither Chrome nor Safari found. Please install a supported browser.")
                else:
                    print("Safari opened successfully.")
            else:
                print("Chrome opened successfully.")
            
            # Create a keyboard controller
            keyboard = Controller()

            # Additional actions based on web version
            web_version = config.PREFER_WEBVERSION.lower()
            if web_version == "claude":
                for _ in range(16):  # Press tab 16 times
                    keyboard.press(Key.tab)
                    keyboard.release(Key.tab)

            # Ensure a short delay before pasting to avoid multiple pastes
            time.sleep(0.5)

            # Simulate Cmd+V to paste (for all versions)
            with keyboard.pressed(Key.cmd):
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

            # Added Redundant Actions as a Safety Net for Claude due to quirky web interface. Wierdly it works!
            if web_version == "claude":
                with keyboard.pressed(Key.cmd):
                    keyboard.press('v')
                    keyboard.release('v')
                time.sleep(0.5)  # Add a slight delay to ensure proper focus
                keyboard.press(Key.tab)
                keyboard.release(Key.tab)
                time.sleep(0.5)  # Add a slight delay to ensure proper focus
            # Simulate Enter 
                keyboard.press(Key.enter)
                keyboard.release(Key.enter)
        else:
            print("Web version is currently only supported on macOS.")

