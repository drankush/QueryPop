# llm_manager.py
from openai import OpenAI
from config_handler import load_config

config = load_config()

class LLMManager:
    def __init__(self, ui_manager): # Accept ui_manager here
        self.ui_manager = ui_manager  # Store ui_manager
        self.client = OpenAI(api_key=config.OPENAI_API_KEY, base_url=config.OPENAI_API_URL)

    def update_config(self, new_config):
        global config
        config = new_config

        # Correctly update the OpenAI client:
        self.client = OpenAI(api_key=config.OPENAI_API_KEY, base_url=config.OPENAI_API_URL)
    
    def send_to_llm(self, text, instruction_prompt):
        try:
            response = self.client.chat.completions.create(
                model=config.MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant."},
                    {"role": "user", "content": f"{instruction_prompt}\n\n{text}"}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error in request: {str(e)}" 
