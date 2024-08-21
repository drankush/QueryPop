"""

Configuration file for the QueryPop application.

Users can customize the following settings:
- OpenAI API credentials. Enter any OpenAI compatible API credentials in the provided format.
- Instruction prompts
- Application shortcut key combination

To edit this file, open it in a text editor. Be careful to preserve the correct syntax when making changes.

"""

OPENAI_API_URL = "https://api.openai.com/v1"
OPENAI_API_KEY = "Your API key" 
MODEL = "Model Name" # Enter the model name supported by your provider.

"""

Enter Instruction Prompts in this format strictly, to avoid syntax errrors:
Button_Number: "Button_Name: 'Enter the descriptive prompt in detail'",
0-9 Buttons will be mapped to the respective keyboard keys.

"""

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

"""

Application Shortcut
Users can customize the shortcut key combination here.
The shortcut should be entered using the syntax recognized by the pynput library.
For example, "<ctrl>+<shift>+Q" represents the shortcut Ctrl+Shift+Q
A list of available key names can be found at: https://pynput.readthedocs.io/en/latest/keyboard.html#pynput.keyboard.Key

"""

APPLICATION_SHORTCUT = "<ctrl>+<shift>+Q"
