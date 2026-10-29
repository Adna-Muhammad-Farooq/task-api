
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
PROMPT_PATH = BASE_DIR / "prompts" / "triage_v1.txt"
PROMPT_VERSION = "triage_v1"
MODEL_NAME = "openrouter/free"
API_BASE_URL = "https://openrouter.ai/api/v1"


def get_triage_client() -> OpenAI:
    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not configured")

    return OpenAI(
        api_key=api_key,
        base_url=API_BASE_URL,
        timeout=30.0,
        max_retries=0,
    )


def load_triage_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")
