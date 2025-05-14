from src.utils.log import get_console_logger
from google import genai
from google.genai import types

logger = get_console_logger('Gemini')

class Gemini:
    def __init__(self, api_key: str = None, model: str = "gemini-2.0-flash") -> None:
        self.api_key = api_key
        if not self.api_key:
            raise ValueError("Must provide an API key")

        self.client = genai.Client(api_key=self.api_key)
        self.model = model
        logger.info("Initializing remote Gemini client…")

        try:
            response = self.client.models.generate_content(
                model=self.model, contents="Hi!"
            )
            logger.info("Remote Gemini is ready.")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")
            raise

    def answer(self, query: str, history=None):
        try:
            response = self.client.models.generate_content(
                model=self.model, contents=query,
                config=types.GenerateContentConfig(
                    system_instruction=history[0]['content'],
                    temperature=0.1
                )
            )
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")
            raise

        assistant_msg = [candidate.content.parts[0].text for candidate in response.candidates][0]
        return assistant_msg, []


if __name__ == "__main__":
    startup_prompt = [
        {"role": "user",
         "content": "You are a highly skilled professional AI assistant specialized in Retrieval-Augmented Generation. Your primary goal is to help users by combining deep language understanding with relevant external knowledge retrieved from provided documents."},
        {"role": "assistant", "content": "Sure, please send me your query and data."},
    ]
    client = Gemini(api_key="xxx")
    reply, hist = client.answer("Hi Gemini!", history=startup_prompt)
    print("Gemini:", reply)
