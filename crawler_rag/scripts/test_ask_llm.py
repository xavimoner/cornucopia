# scripts/test_ask_llm.py


import os
import sys
from dotenv import load_dotenv


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.llm_client import ask_llm

load_dotenv()

if __name__ == "__main__":
    prompt = "Resume breument què és una ajuda pública i qui la pot demanar."
    resposta = ask_llm(prompt)
    print("Resposta del model:")
    print(resposta)
