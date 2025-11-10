# app/core/llm.py

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.messages import HumanMessage, SystemMessage
from app.utils.logger import get_logger
import os
from dotenv import load_dotenv
from typing import Any, Union

load_dotenv()
logger = get_logger(__name__)

MessageType = Union[HumanMessage, SystemMessage]

class GeminiLLM:
    """
    Wrapper around Google's Gemini model for text generation.z
    Handles summarization, explanation, and conversational prompts.
    """

    def __init__(self, model_name: str = "gemini-2.5-flash"):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("❌ GOOGLE_API_KEY not found in .env file")

        self.model_name = model_name
        self.llm = ChatGoogleGenerativeAI(model=model_name, google_api_key=self.api_key)
        logger.info(f"Gemini LLM initialized with model '{model_name}'")

    def generate_text(self, prompt: str, system_prompt: str| None =  None) -> str | Any:
        """
        Sends a prompt to the Gemini model and returns its response.
        """
        try:
            messages: list [MessageType] = []
            if system_prompt:
                messages.append(SystemMessage(content=system_prompt))
            messages.append(HumanMessage(prompt))

            response = self.llm.invoke(messages)
            return response.content

        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            return "⚠️ Error generating response from Gemini."

if __name__ == "__main__":

    llm = GeminiLLM()

    result = llm.generate_text("explain quantum computing in 2 lines", system_prompt="you're one of the top quantum researcher in the world")
    print(result)


