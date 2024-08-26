# llm_manager.py
from openai import OpenAI
from config_handler import load_config

config = load_config()

class LLMManager:
    def __init__(self):
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