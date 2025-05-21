# crawler_rag/agents/llm_client.py
# Triar el model que volguem. Ampliable a altres futurs.
import os
import requests
from openai import AzureOpenAI, OpenAI
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "OPENAI").upper()

# --- OpenAI (Azure) ---
openai_client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)
AZURE_DEPLOYMENT = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT")
OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "128000"))

# --- Gemini ---
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/{GEMINI_MODEL}:generateContent"
GEMINI_MAX_TOKENS = int(os.getenv("GEMINI_MAX_TOKENS", "32000"))

# --- DeepSeek ---
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = os.getenv("DEEPSEEK_API_URL")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
DEEPSEEK_MAX_TOKENS = int(os.getenv("DEEPSEEK_MAX_TOKENS", "8000"))

# --- Entrypoint ---
def ask_llm(prompt: str) -> str:
    if LLM_PROVIDER == "OPENAI":
        return ask_openai(prompt)
    elif LLM_PROVIDER == "GEMINI":
        return ask_gemini(prompt)
    elif LLM_PROVIDER == "DEEPSEEK":
        return ask_deepseek(prompt)
    else:
        raise ValueError(f"[ERROR] LLM_PROVIDER desconegut: {LLM_PROVIDER}")

# --- OpenAI Request ---
def ask_openai(prompt: str) -> str:
    response = openai_client.chat.completions.create(
        model=AZURE_DEPLOYMENT,
        messages=[
            {"role": "system", "content": "Eres un asistente experto en análisis de convocatorias."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.0
    )
    return response.choices[0].message.content.strip()

# --- Gemini Request ---
def ask_gemini(prompt: str) -> str:
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    try:
        response = requests.post(f"{GEMINI_URL}?key={GEMINI_KEY}", headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception as e:
        return f"[Error Gemini] {str(e)}"

# --- DeepSeek Request (API compatible amb OpenAI) ---
def ask_deepseek(prompt: str) -> str:
    try:
        deepseek_client = OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_API_URL,
        )
        response = deepseek_client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[
                {"role": "system", "content": "Eres un asistente experto en análisis de convocatorias."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[Error DeepSeek] {str(e)}"

# --- Metadata del model actiu ---
def get_model_info():
    if LLM_PROVIDER == "GEMINI":
        return {"name": GEMINI_MODEL, "max_tokens": GEMINI_MAX_TOKENS}
    elif LLM_PROVIDER == "DEEPSEEK":
        return {"name": DEEPSEEK_MODEL, "max_tokens": DEEPSEEK_MAX_TOKENS}
    else:
        return {"name": AZURE_DEPLOYMENT, "max_tokens": OPENAI_MAX_TOKENS}
