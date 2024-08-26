# clipboard_utils.py
import pyperclip


def get_selected_text():
    print("Getting selected text from clipboard...")
    text = pyperclip.paste()
    print(f"Selected text: {text}")
    return text


# def get_selected_text():
#     return pyperclip.paste()

# def get_selected_text():
    # try:
    #     # Attempt to get the selection (platform-specific)
    #     from tkinter import Tk
    #     root = Tk()
    #     root.withdraw() 
    #     selected_text = root.clipboard_get()
    #     return selected_text 
    # except Exception:
    #     # Fallback: If getting selection fails, check the clipboard
    #     clipboard_content = pyperclip.paste()
    #     return clipboard_content if clipboard_content else None