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


# Application Shortcut
# Users can customize the shortcut key combination here.
# The shortcut should be entered using the syntax recognized by the pynput library.
# For example, "<ctrl>+<shift>+." represents the shortcut Ctrl+Shift+.
# A list of available key names can be found at: https://pynput.readthedocs.io/en/latest/keyboard.html#pynput.keyboard.Key


APPLICATION_SHORTCUT = "<ctrl>+<shift>+."
    
""" 


import os


if os.name == "nt":  # Windows
    config_dir = os.path.join(os.environ["APPDATA"], "QUERYPOP")
else:  # Assuming macOS or Linux
    config_dir = os.path.join(os.path.expanduser("~"), ".querypop")

if not os.path.exists(config_dir):
    os.makedirs(config_dir)

# Check if config.py exists in the config directory
config_path = os.path.join(config_dir, "config.py")
if not os.path.exists(config_path):
    # Create config.py with default contents in the config directory
    with open(config_path, "w") as f:
        f.write(DEFAULT_CONFIG_CONTENTS)




# Standard Library Imports
from datetime import datetime
import os
import subprocess
import sys
import threading
from queue import Queue

# Third-Party Imports
import importlib.util
import markdown2
from openai import OpenAI
from PIL import Image, ImageDraw, ImageFont, ImageTk
from pynput import keyboard
from pynput.keyboard import Controller, Key
import pyperclip
import pystray
from pystray import Icon as tk_icon
from tkhtmlview import HTMLLabel
import tkinter as tk
from tkinter import Button, Canvas, Frame, Label, Scrollbar, Text, Toplevel, messagebox


# Local Application Imports
spec = importlib.util.spec_from_file_location("config", config_path)
config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config)


# Global variables
INSTRUCTION_PROMPT = None
shortcut_detected = threading.Event()  

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def quit_application():
    print("Exiting application...")
    icon.stop()
    os._exit(0)  # Forcefully exit the application


def get_selected_text():
    print("Getting selected text from clipboard...")
    text = pyperclip.paste()
    print(f"Selected text: {text}")
    return text

def send_to_llm(text, result_queue):
    print("Sending text to LLM...")
    try:
        print("Creating OpenAI client...")
        client = OpenAI(api_key=config.OPENAI_API_KEY, base_url=config.OPENAI_API_URL)
        print("Client created successfully.")
        print(f"Sending the following prompt to LLM:\n{INSTRUCTION_PROMPT}\n\n{text}")
        response = client.chat.completions.create(
            model=config.MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": f"{INSTRUCTION_PROMPT}\n\n{text}"}
            ]
        )
        print("Received response from LLM.")
        result_queue.put(response.choices[0].message.content)
        print(response.choices[0].message.content)
    except Exception as e:
        print(f"Request failed: {e}")
        result_queue.put("Error in request.")

def show_popup(selected_text):
    print("Displaying popup window for instruction prompt...")

    def on_ok():
        global INSTRUCTION_PROMPT
        INSTRUCTION_PROMPT = instruction_entry.get("1.0", "end-1c")
        print(f"Instruction Prompt set: {INSTRUCTION_PROMPT}")
        popup.destroy()
        root.after(0, lambda: show_response_window(selected_text))

    def on_button_click(button_number):
        global INSTRUCTION_PROMPT
        INSTRUCTION_PROMPT = config.INSTRUCTION_PROMPTS.get(button_number)
        print(f"Button {button_number} clicked. Instruction Prompt set: {INSTRUCTION_PROMPT}")
        popup.destroy()
        root.after(0, lambda: show_response_window(selected_text))

    def on_key_press(event):
        print(f"Key pressed: {event.char}")
        if event.char.isdigit() and int(event.char) in config.INSTRUCTION_PROMPTS:
            print(f"Key corresponds to instruction prompt button {event.char}.")
            on_button_click(int(event.char))

    def on_close():
        print("Popup window closed.")
        popup.destroy()
        shortcut_detected.set() # Signal main thread to listen for shortcuts again


    try:
        print("Creating popup window...")
        popup = Toplevel()
        popup.title("Instruction Prompt")
        if os.name == "nt":
            initial_width = 800
        else:
            initial_width = 750
        initial_height = 330
        popup.geometry(f"{initial_width}x{initial_height}")

        canvas = Canvas(popup)
        scrollbar = Scrollbar(popup, orient="vertical", command=canvas.yview)
        scrollable_frame = Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        frame = Frame(scrollable_frame)
        frame.pack(padx=10, pady=10)

        print("Loading and resizing image...")
        image_path = resource_path("querypop_logo_main.png")
        original_image = Image.open(image_path)
        width, height = original_image.size
        new_width = initial_width // 8
        new_height = int((new_width / width) * height)
        resized_image = original_image.resize((new_width, new_height), Image.LANCZOS)
        image_tk = ImageTk.PhotoImage(resized_image)

        image_label = Label(frame, image=image_tk)
        image_label.grid(row=1, column=0, rowspan=5, padx=10, pady=10, sticky="n")

        instruction_label = Label(frame, text="Enter \nInstruction \nPrompt:")
        instruction_label.grid(row=0, column=0, padx=10, pady=10)

        instruction_entry = Text(frame, width=70, height=3)
        instruction_entry.grid(row=0, column=1, columnspan=3, padx=10, pady=10)

        ok_button = Button(frame, text="OK", command=on_ok)
        ok_button.grid(row=0, column=4, padx=10, pady=10)

        max_label_length = max(
            len(f"[{key}] {instruction.split(':')[0]}") for key, instruction in config.INSTRUCTION_PROMPTS.items()
        )
        button_width = max_label_length

        row_num = 1
        col_num = 1
        print("Creating buttons for instruction prompts...")
        for key, instruction in config.INSTRUCTION_PROMPTS.items():
            button_text = f"[{key}] {instruction.split(':')[0]}" if key <= 9 else instruction.split(':')[0]
            button = Button(frame, text=button_text, command=lambda k=key: on_button_click(k), width=button_width, anchor="w", padx=15)
            button.grid(row=row_num, column=col_num, columnspan=2, padx=5, pady=5)

            col_num += 2
            if col_num > 3:
                col_num = 1
                row_num += 1

        print("Binding key press event...")
        popup.bind("<KeyPress>", on_key_press)
        popup.protocol("WM_DELETE_WINDOW", on_close)
        print("Popup window setup complete. Running main loop...")
        popup.mainloop()
    except Exception as e:
        print(f"Error occurred in show_popup: {e}")
        sys.exit(1)
    finally:
        root.withdraw() 



def show_response_window(selected_text):
    def on_close():
        root.withdraw()
        shortcut_detected.set() # Signal main thread to listen for shortcuts


    root = Toplevel()
    root.title("LLM Response")
    root.geometry("800x600")
    root.protocol("WM_DELETE_WINDOW", on_close)  # Handle window close

    loading_label = Label(root, text="⚙️ Processing...", font=("Arial", 16))
    loading_label.pack(pady=20)

    # Force the UI to update to ensure the label is displayed
    root.update_idletasks()

    def update_response(response_text):
        loading_label.destroy()

        # Debugging: Print the response text before processing
        print(f"Response Text: {response_text}")

        if not response_text:
            response_text = "Error: No response received from LLM."

        try:
            html_content = markdown2.markdown(response_text)
        except Exception as e:
            html_content = f"<p>Error processing markdown: {str(e)}</p>"

        html_label = HTMLLabel(root, html=html_content)
        html_label.pack(expand=True, fill='both')
        html_label.fit_height()

    def process_llm(text, result_queue):
        send_to_llm(text, result_queue)  # Send the text to LLM and put the response in the queue

        # Fetch the result from the queue
        response = result_queue.get()  # This will block until the result is available

        # Debugging: Check the response content
        print(f"LLM Response: {response}")

        if not response:
            response = "Error: No response received from LLM."
        
        root.after(0, update_response, response)
        save_response(response)
        pyperclip.copy(response)

    def save_response(response_text):
        print("Saving response to file...")
        
        # Handling relative path and ensuring the directory exists
        script_dir = os.path.dirname(__file__)
        save_dir = os.path.join(script_dir, "responses")
        os.makedirs(save_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(save_dir, f"{timestamp}.txt")

        if not response_text:
            response_text = "Error: No response to save."

        try:
            response_html = markdown2.markdown(response_text)
        except Exception as e:
            response_html = f"<p>Error saving response: {str(e)}</p>"

        # Debugging: Ensure response_html is not None before writing
        if response_html is None:
            response_html = "Error: Response conversion failed."

        with open(file_path, "w") as file:
            file.write(response_html)

        print(f"Response saved to {file_path}")

    # Create the queue and pass it to the thread
    result_queue = Queue()
    thread = threading.Thread(target=lambda: process_llm(selected_text, result_queue))
    thread.start()

    root.mainloop()

def error_popup(message):
    print(f"Error: {message}")
    messagebox.showerror("Error", message)

def main():
    print("Main function started.")

    selected_text = get_selected_text()
    if not selected_text.strip():
        print("No text selected. Showing error popup.")
        error_popup("Select a text snippet to send to LLM.")
        return

    print("Selected text found. Showing popup for instruction.")
    show_popup(selected_text)


def listen_for_shortcut():
    keyboard_controller = Controller()

    def on_activate():
        print("Shortcut detected from listener thread!")
        # Detect the operating system
        if sys.platform == 'darwin':  # macOS
            copy_shortcut = (Key.cmd, 'c')
        else:  # Windows or Linux
            copy_shortcut = (Key.ctrl, 'c')
        
        # Simulate the copy shortcut
        with keyboard_controller.pressed(copy_shortcut[0]):
            keyboard_controller.press(copy_shortcut[1])
            keyboard_controller.release(copy_shortcut[1])
            print("Simulated pressing of Cntrl+C")

        # Wait for a short period to ensure the clipboard is updated
        import time
        time.sleep(0.1)
        
        shortcut_detected.set()
        root.after(0, lambda: show_popup(get_selected_text()))

    with keyboard.GlobalHotKeys({config.APPLICATION_SHORTCUT: on_activate}) as h:
        h.join()


def show_about():
    messagebox.showinfo("About QueryPop", """
        Developer Information:
        Developed by: Dr. Ankush
        🌐 www.drankush.com
        ✉️ querypop@drankush.com

        License:
        MIT
    """)


if __name__ == "__main__":
    # Initialize the Tkinter application
    root = tk.Tk()

    # Minimize the Tkinter root window to a very small size
    root.geometry("1x1")

    # Create a text image
    image = Image.new("RGB", (64, 64), color=(0, 0, 0, 0))  # Transparent background
    draw = ImageDraw.Draw(image)
    if os.name == "nt":
        font = ImageFont.load_default()
    else:
        font = ImageFont.truetype("Arial.ttf", size=32)  # Choose an available font
    text_width, text_height = font.getmask("QP").size # Correct way to get text size
    x = (image.width - text_width) // 2
    y = (image.height - text_height) // 2
    draw.text((x, y), "QP", font=font, fill=(255, 255, 255)) # White text

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



    icon = tk_icon("QP", image, "QueryPop", menu=pystray.Menu(
        pystray.MenuItem("Open Config", open_config),
        pystray.MenuItem("About", show_about),
        pystray.MenuItem("Quit", quit_application),
    ))
    icon.run_detached()

    # Start the listener thread
    listener_thread = threading.Thread(target=listen_for_shortcut, daemon=True)
    listener_thread.start()
    print("Main thread waiting for shortcut...")

    root.mainloop()
