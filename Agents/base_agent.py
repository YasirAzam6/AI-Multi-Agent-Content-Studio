# import os
# from openai import OpenAI
# from dotenv import load_dotenv
from Agents.config import LLM, base_temperature
from abc import ABC, abstractmethod
from llm_client import llm_client  

class BaseAgent(ABC):
    """
    Base class that loads the environment and initializes OpenAI client.
    All specialized agents inherit from this.
    """
    def __init__(self):
        # # Load environment variables from project root
        # project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        # load_dotenv(os.path.join(project_root, ".env"))

        # api_key = os.getenv("OPENAI_API_KEY")
        # if not api_key:
        #     raise ValueError("❌ OPENAI_API_KEY not found in .env")

        self.client = llm_client
    @abstractmethod
    def run(self, state: dict) -> dict:
        """Each agent must implement this."""
        raise NotImplementedError

    def call_llm(self, prompt=None, messages=None, model=LLM, temperature: float = base_temperature) -> str:
        """
        Small wrapper around OpenAI chat completions.

        Usage patterns:
        - Simple: call_llm(prompt="...")  → wraps into a single user message
        - Advanced: call_llm(messages=[...]) → you control the messages list

        `model` defaults to Agents.config.LLM.
        """
        if messages is None:
            if prompt is None:
                raise ValueError("call_llm requires either `prompt` or `messages`.")
            messages = [{"role": "user", "content": prompt}]

        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
        )
        return response.choices[0].message.content

