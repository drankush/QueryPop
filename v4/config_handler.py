# config_handler.py
import os
import importlib.util
import sys
import subprocess

DEFAULT_CONFIG_CONTENTS = """
# Configuration file for the QueryPop application.

# Users can customize the following settings:
# - OpenAI API credentials
# - Instruction prompts
# - Application shortcut key combination

# To edit this file, open it in a text editor. Be careful to preserve the correct syntax when making changes.

OPENAI_API_URL = "https://api.openai.com/v1"
OPENAI_API_KEY = "Your Key"
MODEL = "Your Selected Model"

# Enter Instruction Prompts in this format:
# Button_Number: "Button_Name: 'Enter the descriptive prompt in detail'",
# 0-9 keys will be mapped to the keyboard keys.

INSTRUCTION_PROMPTS = {
0: "Key Points Extraction: 'Extract key points from the following text:'",
1: "Summarization: 'Summarize the following text:'",
2: "Translation: 'Translate the following text into Spanish:'",
3: "Explanation: 'Explain the following text in detail:'",
4: "Question Answering: 'Answer the following question based on the text:'",
5: "Question Generation: 'Generate Questions based on the text:'",
6: "Paraphrasing: 'Paraphrase the following text:'",
7: "Sentiment Analysis: 'Determine the sentiment of the following text:'",
8: "Topic Modeling: 'Identify the topics in the following text:'",
9: "Text Simplification: 'Simplify the following text for easier understanding:'",
10: "Text Expansion: 'Expand the following text on the topic being discussed:'"
}

# Preferred Web Version (if applicable)
# Options: "chatgpt", "claude", "gemini", "meta", "perplexity"
# Leave blank or set to any other value to use API keys.
PREFER_WEBVERSION = "chatgpt" 

# Input Delay for Web Version (in seconds)
INPUT_DELAY = "5"

# Browser Window Size (for web version)
# Format: {x-coordinate, y-coordinate, width, height}
# - x-coordinate: Horizontal position of the window's top-left corner from the left edge of the screen.
# - y-coordinate: Vertical position of the window's top-left corner from the top edge of the screen.
# - width: Width of the browser window in pixels.
# - height: Height of the browser window in pixels.
BROWSER_WINDOW_SIZE = "{100,50,400,700}" # Keep no spaces

# Application Shortcut
# Users can customize the shortcut key combination here.
# The shortcut should be entered using the syntax recognized by the pynput library.
# For example, "<ctrl>+<shift>+." represents the shortcut Ctrl+Shift+.
# A list of available key names can be found at: https://pynput.readthedocs.io/en/latest/keyboard.html#pynput.keyboard.Key
# Look out for conflicts with the application you will be using.
APPLICATION_SHORTCUT = "<ctrl>+`" # The default is Ctrl + ` (the backtick key, above the tab key). 
""" 



def open_config():
    global config_path  # Use the global config_path variable
    if not os.path.exists(config_path):
        with open(config_path, "w") as f:
            f.write(DEFAULT_CONFIG_CONTENTS)
    if sys.platform == "win32":
        os.startfile(config_path)
    else:
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, config_path])

def get_config_path():
    if os.name == "nt":  # Windows
        config_dir = os.path.join(os.environ["APPDATA"], "QUERYPOP")
    else:  # Assuming macOS or Linux
        config_dir = os.path.join(os.path.expanduser("~"), ".querypop")
    
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    
    return os.path.join(config_dir, "config.py")

def load_config():
    config_path = get_config_path()
    if not os.path.exists(config_path):
        with open(config_path, "w") as f:
            f.write(DEFAULT_CONFIG_CONTENTS)
    
    spec = importlib.util.spec_from_file_location("config", config_path)
    config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config)
    return config

def get_resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
