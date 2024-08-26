# browser_manager.py
import webbrowser
import subprocess
import sys
import pyperclip
from config_handler import load_config

config = load_config()  # Load your configuration

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
        input_delay = int(config.INPUT_DELAY)  # Assuming you have INPUT_DELAY in your config

        try:
            window_bounds = [int(x.strip()) for x in config.BROWSER_WINDOW_SIZE[1:-1].split(',')]
            window_size = f"{{ {window_bounds[0]}, {window_bounds[1]}, {window_bounds[2]}, {window_bounds[3]} }}"
        except Exception as e:
            print(f"Error parsing BROWSER_WINDOW_SIZE from config.py: {e}")
            window_size = "{100, 50, 400, 700}" 

        if sys.platform == 'darwin':  # macOS
            # Try opening in Chrome first
            chrome_script = f'''
                tell application "Google Chrome"
                    activate
                    make new window
                    set URL of active tab of window 1 to "{url}"
                    set bounds of window 1 to {{{", ".join(map(str, window_bounds))}}} 
                    delay {input_delay}
                    tell application "System Events"
                        keystroke "v" using command down
                        delay 1 
                        '''
            if config.PREFER_WEBVERSION.lower() == "chatgpt":
                chrome_script += 'keystroke return using {command down}'
            elif config.PREFER_WEBVERSION.lower() in ["gemini", "meta"]:
                chrome_script += 'keystroke return'
            chrome_script += '''
                    end tell
                end tell
            '''
            chrome_result = subprocess.run(["osascript", "-e", chrome_script], stderr=subprocess.DEVNULL)

            # If Chrome is not found, try Safari
            if chrome_result.returncode != 0: 
                safari_script = f'''
                    tell application "Safari"
                        activate
                        tell window 1
                            set current tab to (make new tab)
                            set the URL of the current tab to "{url}"
                        end tell
                        set bounds of window 1 to {{{", ".join(map(str, window_bounds))}}} 
                        delay {input_delay}
                        tell application "System Events"
                            keystroke "v" using command down
                            delay 1
                            '''
                if config.PREFER_WEBVERSION.lower() == "chatgpt":
                    safari_script += 'keystroke return using {command down}'
                elif config.PREFER_WEBVERSION.lower() in ["gemini", "meta"]:
                    safari_script += 'keystroke return'
                safari_script += '''    
                        end tell
                    end tell
                '''
                safari_result = subprocess.run(["osascript", "-e", safari_script], stderr=subprocess.DEVNULL)

                if safari_result.returncode != 0:
                    print("Neither Chrome nor Safari found. Please install a supported browser.")
        else:
            print("Web version is currently only supported on macOS.")
