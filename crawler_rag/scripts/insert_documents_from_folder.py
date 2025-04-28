# crawler_rag/scripts/insert_documents_from_folder.py
import os
import sys
import psycopg2
from dotenv import load_dotenv
from typing import Callable
import requests
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Tasks i tools
from crawler_rag.agents.tasks.extract_linea_task import TASK as TASK_LINEA, FIELD as FIELD_LINEA
from crawler_rag.agents.tools.extract_field_linea import extract_field_linea

from crawler_rag.agents.tasks.extract_objetivo_task import TASK as TASK_OBJ, FIELD as FIELD_OBJ
from crawler_rag.agents.tools.extract_field_objetivo import extract_field_objetivo

# Entorn
load_dotenv()

def get_texts_for_convocatoria(convocatoria_id: int) -> str:
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cursor = conn.cursor()
    cursor.execute("""
        SELECT texto FROM documentos
        WHERE convocatoria_id = %s AND texto IS NOT NULL
    """, (convocatoria_id,))
    texts = [row[0] for row in cursor.fetchall() if row[0].strip()]
    cursor.close()
    conn.close()
    return "\n\n".join(texts)

def update_field(convocatoria_id: int, field: str, value: str):
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cursor = conn.cursor()
    cursor.execute(f"""
        UPDATE convocatorias
        SET {field} = %s
        WHERE id = %s
    """, (value, convocatoria_id))
    conn.commit()
    cursor.close()
    conn.close()

def extract_with_gemini(task: str, context: str, model: str = "gemini-2.0-pro") -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    payload = {
        "contents": [{
            "parts": [
                {"text": f"{task}\n\n{context}"}
            ]
        }]
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(endpoint, headers=headers, data=json.dumps(payload))
    try:
        return response.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        return ""

def extract_with_azure(task: str, context: str) -> str:
    from crawler_rag.utils.chat_client import create_chat_completion
    prompt = f"{task}\n\n{context}"
    return create_chat_completion(prompt)

def run_extraction(convocatoria_id: int, task: str, field: str, model: str = "azure"):
    print(f"\n🔍 [{field.upper()}] Extracció en curs...")
    context = get_texts_for_convocatoria(convocatoria_id)
    if not context.strip():
        print("⚠️ Sense context disponible.")
        return

    if model == "gemini":
        value = extract_with_gemini(task, context)
    else:
        value = extract_with_azure(task, context)

    if value:
        update_field(convocatoria_id, field, value)
        print(f"✅ Camp '{field}' actualitzat amb: {value[:300]}...")
    else:
        print(f"⚠️ Cap resultat rellevant per al camp '{field}'.")

def main():
    convocatoria_id = 2  # ← adapta si cal
    model = os.getenv("AGENT_MODEL", "azure")

    run_extraction(convocatoria_id, TASK_LINEA, FIELD_LINEA, model)
    run_extraction(convocatoria_id, TASK_OBJ, FIELD_OBJ, model)

if __name__ == "__main__":
    main()
