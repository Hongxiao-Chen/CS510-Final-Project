import json
import re
import ast
from zhipuai import ZhipuAI


from src.utils.log import get_console_logger

logger = get_console_logger('ChatGLM')


class ChatGLM():
    def __init__(self,
                 api_key = "",
                 model="glm-4-flash",
                 ) -> None:

        self.api_key = api_key
        if not self.api_key:
            raise ValueError("Must provide an API key")

        logger.info("Initializing remote ChatGLM client…")
        self.client = ZhipuAI(api_key=self.api_key)
        self.model = model

        _ = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": "Hello"}],
        )
        logger.info("Remote ChatGLM ready.")

    def answer(self, query: str, history):
        messages = []
        if history:
            for q, a in history:
                messages.append({"role": "user", "content": q})
                messages.append({"role": "assistant", "content": a})
        messages.append({"role": "user", "content": query})

        resp = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
        )
        assistant_msg = resp.choices[0].message.content
        if self.model == "glm-z1-flash":
            assistant_msg = assistant_msg.split('</think>')[-1].strip()

        new_history = history[:] if history else []
        new_history.append([query, assistant_msg])
        return assistant_msg, new_history

if __name__ == "__main__":
    llm = ChatGLM(api_key="xxx", model="glm-z1-flash")
    msg, _ = llm.answer("Hello", [])
    print(msg)