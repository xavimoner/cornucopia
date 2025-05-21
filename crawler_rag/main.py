# crawler_rag/main.py

import asyncio
import os

print("Main script engegat...")

# Lògica del crawler
# funció buida 
async def stay_alive():
    try:
        while True:
            await asyncio.sleep(60)
    except asyncio.CancelledError:
        print("Sortint...")

def get_active_model():
    return {
        "llm_provider": os.getenv("LLM_PROVIDER", "NO DEFINIT"),
        "model": os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT") if os.getenv("LLM_PROVIDER") == "OPENAI"
        else os.getenv("GEMINI_MODEL") if os.getenv("LLM_PROVIDER") == "GEMINI"
        else os.getenv("DEEPSEEK_MODEL") if os.getenv("LLM_PROVIDER") == "DEEPSEEK"
        else "NO DEFINIT"
    }




if __name__ == "__main__":
    # Ens assegurem q funció només es cridi una vegada
    asyncio.run(stay_alive())