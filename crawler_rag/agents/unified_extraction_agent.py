# crawler_rag/agents/unified_extraction_agent.py

# Agent principal d’extracció. Llegeix textos i aplica instruccions.


import os
import psycopg2
from dotenv import load_dotenv
from crawler_rag.agents.llm_client import ask_llm
from crawler_rag.agents.extraction_tasks import TASKS
from datetime import datetime

load_dotenv()

LOG_PATH = "crawler_rag/logs/extraction_agent.log"
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {msg}\n")
    print(msg)

def get_texts_for_convocatoria(convocatoria_id: int):
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cursor = conn.cursor()
    cursor.execute("""
        SELECT texto FROM documentos
        WHERE convocatoria_id = %s
    """, (convocatoria_id,))
    textos = [row[0] for row in cursor.fetchall() if row[0] and len(row[0].split()) > 5]
    cursor.close()
    conn.close()
    return textos

def update_field(convocatoria_id: int, field: str, value: str):
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cursor = conn.cursor()
    cursor.execute(f"""
        UPDATE convocatorias SET {field} = %s WHERE id = %s
    """, (value, convocatoria_id))
    conn.commit()
    cursor.close()
    conn.close()

def run_all_extractions(convocatoria_id: int):
    textos = get_texts_for_convocatoria(convocatoria_id)
    if not textos:
        log(f"⚠️ No s'ha trobat cap text per a la convocatòria ID {convocatoria_id}.")
        return

    full_text = "\n\n".join(textos)
    for key, task in TASKS.items():
        log(f"\n🔍 Extraient camp '{key}'...")
        resposta = ask_llm(task["prompt"].replace("{{TEXT}}", full_text))
        if resposta:
            update_field(convocatoria_id, task["field"], resposta)
            log(f"✅ Camp '{task['field']}' actualitzat amb: {resposta[:300]}...")
        else:
            log(f"❌ Cap resposta obtinguda per a '{task['field']}'")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Ús: python agents/unified_extraction_agent.py <convocatoria_id>")
    else:
        run_all_extractions(int(sys.argv[1]))
