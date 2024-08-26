import os
import sys

import tkinter as tk
from tkinter import Toplevel, Label, Button, Frame, Canvas, Scrollbar, Text, messagebox
from tkhtmlview import HTMLLabel
import markdown2
from PIL import Image, ImageTk
from queue import Queue
import threading

from config_handler import load_config, get_resource_path
from llm_manager import LLMManager
from browser_manager import BrowserManager

config = load_config()

class UIManager:
    def __init__(self, root):
        self.root = root
        self.llm_manager = LLMManager()
        self.browser_manager = BrowserManager()

    def show_popup(self, selected_text):
        print("Displaying popup window for instruction prompt...")

        def on_ok():
            instruction_prompt = config.INSTRUCTION_PROMPTS.get("1.0", "end-1c")
            print(f"Instruction Prompt set: {instruction_prompt}")
            popup.destroy()
            self.root.after(0, lambda: self.handle_llm_interaction(selected_text, instruction_prompt))

        def on_button_click(button_number):
            instruction_prompt = config.INSTRUCTION_PROMPTS.get(button_number)
            print(f"Button {button_number} clicked. Instruction Prompt set: {instruction_prompt}")
            popup.destroy()
            self.root.after(0, lambda: self.handle_llm_interaction(selected_text, instruction_prompt))

        def on_key_press(event):
            print(f"Key pressed: {event.char}")
            if event.char.isdigit() and int(event.char) in config.INSTRUCTION_PROMPTS:
                print(f"Key corresponds to instruction prompt button {event.char}.")
                on_button_click(int(event.char))

        def on_close():
            print("Popup window closed.")
            popup.destroy()

        try:
            print("Creating popup window...")
            popup = Toplevel(self.root)
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
            image_path = get_resource_path("querypop_logo_main.png")
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
            self.root.withdraw() 


        popup.mainloop()

    def show_response_window(self, selected_text, instruction_prompt):
        response_window = Toplevel(self.root)
        response_window.title("LLM Response")
        response_window.geometry("800x600")

        loading_label = Label(response_window, text="⚙️ Processing...", font=("Arial", 16))
        loading_label.pack(pady=20)

        response_window.update_idletasks()

        def update_response(response_text):
            loading_label.destroy()

            if not response_text:
                response_text = "Error: No response received from LLM."

            try:
                html_content = markdown2.markdown(response_text)
            except Exception as e:
                html_content = f"<p>Error processing markdown: {str(e)}</p>"

            html_label = HTMLLabel(response_window, html=html_content)
            html_label.pack(expand=True, fill='both')
            html_label.fit_height()

        def process_llm():
            response = self.llm_manager.send_to_llm(selected_text, instruction_prompt)
            response_window.after(0, update_response, response)

        thread = threading.Thread(target=process_llm)
        thread.start()

        response_window.mainloop()

    def handle_llm_interaction(self, selected_text, instruction_prompt):
        if config.PREFER_WEBVERSION.lower() in ["chatgpt", "claude", "gemini", "meta"]:
            print(f"Web version preferred: {config.PREFER_WEBVERSION}. Calling show_browser_window.")
            self.browser_manager.show_browser_window(selected_text, instruction_prompt)
        else:
            print("Proceeding with API based response window...")
            self.show_response_window(selected_text, instruction_prompt)

    def error_popup(self, message):
        messagebox.showerror("Error", message)