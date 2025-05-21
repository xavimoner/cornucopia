# crawler_rag/utils/chat_client.py

import os
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT", "gpt-4o")

def create_chat_completion(prompt: str) -> str:
    messages = [
        {"role": "system", "content": "Ets un assistent útil que resumeix textos tècnics de subvencions."},
        {"role": "user", "content": prompt}
    ]

    response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=messages
    )
    return response.choices[0].message.content.strip()
