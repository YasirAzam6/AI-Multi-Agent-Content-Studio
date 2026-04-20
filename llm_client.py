import os
from dotenv import load_dotenv
from openai import OpenAI

# Load .env from current working dir (where app.py + .env live)
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY not found in environment or .env file.")

# Single shared client for the whole app
llm_client = OpenAI(api_key=api_key)