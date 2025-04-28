# rawler_rag/agents/llm_client.py

# Mòdul per parlar amb OpenAI o Gemini, segons config.


import os
import requests
from openai import AzureOpenAI
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

USE_GEMINI = os.getenv("USE_GEMINI", "false").lower() == "true"

# --------------- OpenAI Client ---------------
openai_client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)
AZURE_DEPLOYMENT = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT")

# --------------- Gemini Config ---------------
GEMINI_URL = os.getenv("GEMINI_API_URL")  # Ex: https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-pro:generateContent
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

# --------------- LLM Wrapper ---------------
def ask_llm(prompt: str) -> str:
    if USE_GEMINI:
        return ask_gemini(prompt)
    else:
        return ask_openai(prompt)

# --------------- OpenAI Request ---------------
def ask_openai(prompt: str) -> str:
    response = openai_client.chat.completions.create(
        model=AZURE_DEPLOYMENT,
        messages=[{"role": "system", "content": "Eres un asistente experto en análisis de convocatorias."},
                  {"role": "user", "content": prompt}],
        temperature=0.0
    )
    return response.choices[0].message.content.strip()

# --------------- Gemini Request ---------------
def ask_gemini(prompt: str) -> str:
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    response = requests.post(
        f"{GEMINI_URL}?key={GEMINI_KEY}",
        headers=headers,
        json=payload
    )
    data = response.json()
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception:
        return "[Error] No s'ha pogut interpretar la resposta de Gemini."

# --------------- Logger Helper (opcional) ---------------
def log_response(source: str, field: str, content: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    os.makedirs("crawler_rag/logs", exist_ok=True)
    with open("crawler_rag/logs/extraction_agent.log", "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] [{source}] [{field}] → {content[:300]}\n")
