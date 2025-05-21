# backend/llm_client.py

import os
from dotenv import load_dotenv
load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "OPENAI").upper()

if LLM_PROVIDER == "OPENAI":
    from backend.llms.openai_client import ask_openai as ask_llm
    MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", 128000))

elif LLM_PROVIDER == "GEMINI":
    from backend.llms.gemini_client import ask_gemini as ask_llm
    MAX_TOKENS = int(os.getenv("GEMINI_MAX_TOKENS", 32000))

elif LLM_PROVIDER == "DEEPSEEK":
    from backend.llms.deepseek_client import ask_deepseek as ask_llm
    MAX_TOKENS = int(os.getenv("DEEPSEEK_MAX_TOKENS", 8000))

else:
    raise ValueError(f"Model LLM_PROVIDER '{LLM_PROVIDER}' no reconegut.")
