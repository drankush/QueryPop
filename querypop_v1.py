import pyperclip
from openai import OpenAI
import tkinter as tk
from tkinter import messagebox
from tkhtmlview import HTMLLabel
import os
from datetime import datetime
import markdown2
import threading


# Define your OpenAI API details
#####  Accepts all OpenAI compatible API.
OPENAI_API_URL = "https://api.openai.com/v1"
OPENAI_API_KEY = "your_openai_api_key"
MODEL = "gpt-4o"


# Predefined instruction prompt
INSTRUCTION_PROMPT = "Customize this instruction prompt"

def get_selected_text():
    return pyperclip.paste()

def send_to_llm(text):
    try:
        client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_API_URL)
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": f"{INSTRUCTION_PROMPT}\n\n{text}"}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Request failed: {e}")
        return "Error in request."

def show_popup(selected_text):  # Pass selected_text to show_popup
    # Create the main window
    root = tk.Tk()
    root.title("LLM Response")
    root.geometry("800x600")

    # Create the loading label
    loading_label = tk.Label(root, text="⚙️ Processing...", font=("Arial", 16))
    loading_label.pack(pady=20)

    # Define the function to update the GUI with the response
    def update_response(response_text):
        # Remove the loading label
        loading_label.destroy()

        # Display either the response or error message
        if response_text == "Error in request.":
            error_label = tk.Label(root, text=response_text, font=("Arial", 16), fg="red")
            error_label.pack(pady=20)
        else:
            # Convert markdown to HTML
            html_content = markdown2.markdown(response_text)

            # Create an HTMLLabel to display the HTML content
            html_label = HTMLLabel(root, html=html_content)
            html_label.pack(expand=True, fill='both')
            html_label.fit_height()

    # Start a new thread to send the LLM request
    def process_llm(text):  # Use 'text' parameter for LLM request
        response = send_to_llm(text)
        update_response(response)
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
    root.withdraw()
    messagebox.showerror("Error", message)
    root.destroy()

def main():
    selected_text = get_selected_text()
    if not selected_text.strip():
        error_popup("Select a text snippet to send to LLM.")
        return

    show_popup(selected_text)  


if __name__ == "__main__":
    main()
