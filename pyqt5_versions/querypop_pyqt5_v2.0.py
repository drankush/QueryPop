import os
from datetime import datetime
import threading
import sys

from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QVBoxLayout,
    QLabel,
    QTextEdit,
    QMessageBox,
    QMainWindow,
    QGridLayout,
    QLineEdit,
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QTextCursor, QFont, QPixmap
import pyperclip
from openai import OpenAI
import markdown2
import config  # Import the config file


class Worker(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, text, instruction_prompt):
        super().__init__()
        self.text = text
        self.instruction_prompt = instruction_prompt

    def run(self):
        try:
            client = OpenAI(
                api_key=config.OPENAI_API_KEY, base_url=config.OPENAI_API_URL
            )
            response = client.chat.completions.create(
                model=config.MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful AI assistant.",
                    },
                    {
                        "role": "user",
                        "content": f"{self.instruction_prompt}\n\n{self.text}",
                    },
                ],
            )
            self.finished.emit(response.choices[0].message.content)
        except Exception as e:
            self.error.emit(f"Request failed: {e}")


class ResponseWindow(QMainWindow):
    def __init__(self, selected_text, instruction_prompt):
        super().__init__()
        self.setWindowTitle("LLM Response")
        self.resize(800, 600)

        self.selected_text = selected_text
        self.instruction_prompt = instruction_prompt

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        self.loading_label = QLabel("⚙️ Processing...", self)
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setFont(QFont("Arial", 16))
        layout.addWidget(self.loading_label)

        self.text_edit = QTextEdit(self)
        self.text_edit.setReadOnly(True)
        layout.addWidget(self.text_edit)

        self.process_llm()

    def process_llm(self):
        self.worker = Worker(self.selected_text, self.instruction_prompt)
        self.worker.finished.connect(self.update_response)
        self.worker.error.connect(self.show_error)
        self.worker.start()

    def update_response(self, response_text):
        self.loading_label.hide()
        html_content = markdown2.markdown(response_text)
        self.text_edit.setHtml(html_content)
        self.save_response(response_text)

    def show_error(self, error_message):
        self.loading_label.hide()
        QMessageBox.critical(self, "Error", error_message)

    def save_response(self, response_html):
        script_dir = os.path.dirname(__file__)
        save_dir = os.path.join(script_dir, "responses")
        os.makedirs(save_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(save_dir, f"{timestamp}.txt")

        with open(file_path, "w") as file:
            file.write(response_html)


class InstructionPopup(QWidget):
    def __init__(self, selected_text):
        super().__init__()
        self.setWindowTitle("Instruction Prompt")
        self.resize(700, 400)
        self.selected_text = selected_text

        layout = QVBoxLayout(self)
        grid_layout = QGridLayout()
        layout.addLayout(grid_layout)

        # Prompt Input (occupies single row now)
        prompt_label = QLabel("Enter Instruction Prompt:")
        self.prompt_input = QLineEdit(self)
        grid_layout.addWidget(prompt_label, 0, 0)
        grid_layout.addWidget(self.prompt_input, 0, 1)

        # OK Button 
        ok_button = QPushButton("OK", self)
        ok_button.clicked.connect(self.on_ok)
        grid_layout.addWidget(ok_button, 0, 2)

        # Logo (adjust row and rowspan accordingly)
        logo_label = QLabel(self)
        pixmap = QPixmap("querypop_logo_main.jpg")
        logo_label.setPixmap(pixmap.scaledToWidth(100))
        grid_layout.addWidget(logo_label, 1, 2, 5, 1)  # Start from row 1, span 5 rows

        # Dynamically generate buttons
        buttons_per_row = 2
        row = 1  # Start from row 1 (below prompt input)
        col = 0
        for i, (key, instruction) in enumerate(config.INSTRUCTION_PROMPTS.items()):
            button_text = (
                f"[{key}] {instruction.split(':')[0]}"
                if key <= 9
                else instruction.split(":")[0]
            )
            button = QPushButton(button_text, self)
            button.clicked.connect(
                lambda checked, k=key: self.on_button_click(k)
            )
            grid_layout.addWidget(button, row, col)
            col += 1
            if (i + 1) % buttons_per_row == 0:
                row += 1
                col = 0

    def on_button_click(self, button_number):
        self.instruction_prompt = config.INSTRUCTION_PROMPTS.get(button_number)
        self.close()
        self.show_response_window()

    def on_ok(self):
        # Use text from input if provided, otherwise use the selected button's prompt
        self.instruction_prompt = self.prompt_input.text() or self.instruction_prompt
        self.close()
        self.show_response_window()

    def show_response_window(self):
        if self.instruction_prompt is not None:
            self.response_window = ResponseWindow(
                self.selected_text, self.instruction_prompt
            )
            self.response_window.show()


def main():
    app = QApplication(sys.argv)
    selected_text = pyperclip.paste()
    if not selected_text.strip():
        QMessageBox.critical(None, "Error", "Select a text snippet to send to LLM.")
        sys.exit(1)

    instruction_popup = InstructionPopup(selected_text)
    instruction_popup.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
