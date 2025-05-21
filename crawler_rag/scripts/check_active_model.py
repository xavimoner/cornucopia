# crawler_rag/scripts/check_active_model.py

import os
from dotenv import load_dotenv

load_dotenv()

llm_provider = os.getenv("LLM_PROVIDER", "OPENAI").upper()

if llm_provider == "GEMINI":
    model = os.getenv("GEMINI_MODEL", "models/gemini-2.0-pro")
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/{model}:generateContent"
elif llm_provider == "DEEPSEEK":
    model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    endpoint = os.getenv("DEEPSEEK_API_URL")
else:
    model = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT", "gpt-4o")
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")

print(f"Model actiu ({llm_provider}): {model}")
print(f"Endpoint: {endpoint}")
