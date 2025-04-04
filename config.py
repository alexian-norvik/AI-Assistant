import os

from dotenv import load_dotenv
from anthropic import AsyncAnthropic

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

ANTHROPIC_MODEL = AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
