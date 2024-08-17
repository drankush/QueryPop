import pyperclip
from openai import OpenAI
import tkinter as tk
from tkinter import messagebox, Button, Label, Toplevel, Text
from tkhtmlview import HTMLLabel
from PIL import Image, ImageTk 
import os
from datetime import datetime
import markdown2
import threading
import sys
import config  # Import the config file

# Global variable to store selected instruction
INSTRUCTION_PROMPT = None

def get_selected_text():
    return pyperclip.paste()

def send_to_llm(text):
    try:
        client = OpenAI(api_key=config.OPENAI_API_KEY, base_url=config.OPENAI_API_URL)
        response = client.chat.completions.create(
            model=config.MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant trained on large amounts of USMLE Step3 material."},
                {"role": "user", "content": f"{INSTRUCTION_PROMPT}\n\n{text}"}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Request failed: {e}")
        return "Error in request."


def show_popup(selected_text):
    def on_ok():
        global INSTRUCTION_PROMPT
        INSTRUCTION_PROMPT = instruction_entry.get("1.0", "end-1c")
        popup.destroy()
        show_response_window(selected_text)

    def on_button_click(button_number):
        global INSTRUCTION_PROMPT
        INSTRUCTION_PROMPT = config.INSTRUCTION_PROMPTS.get(button_number)
        popup.destroy()
        show_response_window(selected_text)

    def on_key_press(event):
        if event.char.isdigit() and int(event.char) in config.INSTRUCTION_PROMPTS:
            on_button_click(int(event.char))

    def on_close():
        sys.exit()  # Exit the application

    # Create main popup window
    popup = Toplevel()
    popup.title("Instruction Prompt")

    # Use initial window size
    initial_width = 700
    initial_height = 310
    popup.geometry(f"{initial_width}x{initial_height}")

    # Create a canvas and a scrollbar for scrolling
    canvas = tk.Canvas(popup)
    scrollbar = tk.Scrollbar(popup, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    # Bind the canvas to the scrollbar
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Create a frame within the canvas for the content
    frame = tk.Frame(scrollable_frame)
    frame.pack(padx=10, pady=10)

    # Load and resize the image
    image_path = "querypop_logo_main.jpg"  # Path to your image file
    original_image = Image.open(image_path)
    # Resize the image to fit within column 0 (adjust size accordingly)
    width, height = original_image.size
    new_width = initial_width // 6  # Adjust width for image
    new_height = int((new_width / width) * height)  # Maintain aspect ratio
    resized_image = original_image.resize((new_width, new_height), Image.LANCZOS)
    image_tk = ImageTk.PhotoImage(resized_image)

    # Display the image spanning over rows 1 to 5 but in column 0
    image_label = Label(frame, image=image_tk)
    image_label.grid(row=1, column=0, rowspan=5, padx=10, pady=10, sticky="n")

    # Instruction entry
    instruction_label = Label(frame, text="Enter \nInstruction \nPrompt:")
    instruction_label.grid(row=0, column=0, padx=10, pady=10)

    instruction_entry = Text(frame, width=50, height=3)  # Use Text widget for taller input field
    instruction_entry.grid(row=0, column=2, columnspan=4, padx=10, pady=10)

    ok_button = Button(frame, text="OK", command=on_ok)
    ok_button.grid(row=0, column=6, padx=10, pady=10)

    # Calculate the maximum button width based on the instruction labels
    max_label_length = max(
        len(f"[{key}] {instruction.split(':')[0]}") for key, instruction in config.INSTRUCTION_PROMPTS.items()
    )
    max_button_width = max_label_length + 2  # Add padding

    # Dynamically generate buttons based on config.INSTRUCTION_PROMPTS
    row_num = 1  # Start from row 1
    col_num = 1
    for key, instruction in config.INSTRUCTION_PROMPTS.items():
        button_text = f"[{key}] {instruction.split(':')[0]}" if key <= 9 else instruction.split(':')[0]
        button = Button(frame, text=button_text, command=lambda k=key: on_button_click(k), width=max_button_width)
        button.grid(row=row_num, column=col_num, columnspan=2, padx=10, pady=10)

        col_num += 2  # Move to the next pair of columns (i.e., from 1 & 2 to 3 & 4)
        if col_num > 3:  # Move to the next row after placing two buttons
            col_num = 1
            row_num += 1

    popup.bind("<KeyPress>", on_key_press)  # Bind keypress events to the popup
    popup.protocol("WM_DELETE_WINDOW", on_close)  # Handle window close

    popup.mainloop()


def show_response_window(selected_text):
    def on_close():
        sys.exit()  # Exit the application

    root = Toplevel()
    root.title("LLM Response")
    root.geometry("800x600")
    root.protocol("WM_DELETE_WINDOW", on_close)  # Handle window close

    loading_label = Label(root, text="⚙️ Processing...", font=("Arial", 16))
    loading_label.pack(pady=20)

    def update_response(response_text):
        loading_label.destroy()

        if response_text == "Error in request.":
            error_label = Label(root, text=response_text, font=("Arial", 16), fg="red")
            error_label.pack(pady=20)
        else:
            html_content = markdown2.markdown(response_text)
            html_label = HTMLLabel(root, html=html_content)
            html_label.pack(expand=True, fill='both')
            html_label.fit_height()

    def process_llm(text):
        response = send_to_llm(text)
        root.after(0, update_response, response)
        save_response(response)

    thread = threading.Thread(target=lambda: process_llm(selected_text))
    thread.start()

    root.mainloop()

def save_response(response_html):
    script_dir = os.path.dirname(__file__)
    save_dir = os.path.join(script_dir, "responses")
    os.makedirs(save_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = os.path.join(save_dir, f"{timestamp}.txt")

    with open(file_path, "w") as file:
        file.write(response_html)

def error_popup(message):
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    messagebox.showerror("Error", message)
    root.destroy()

def main():
    root = tk.Tk()
    root.withdraw()

    selected_text = get_selected_text()
    if not selected_text.strip():
        error_popup("Select a text snippet to send to LLM.")
        return

    show_popup(selected_text)  
    root.destroy()

if __name__ == "__main__":
    main()
