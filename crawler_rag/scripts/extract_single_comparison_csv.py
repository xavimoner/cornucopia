# crawler_rag/scripts/extract_single_comparison_csv.py

import os
import sys
import csv
import psycopg2
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.extraction_tasks import TASKS
from agents.llm_client import ask_openai, ask_gemini, ask_deepseek
from agents.llm_client import OPENAI_MAX_TOKENS, GEMINI_MAX_TOKENS, DEEPSEEK_MAX_TOKENS

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def get_full_text(convocatoria_id):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("SELECT texto FROM documentos WHERE convocatoria_id = %s", (convocatoria_id,))
    textos = [row[0] for row in cursor.fetchall() if row[0]]
    cursor.close()
    conn.close()
    return "\n\n".join(textos).strip()

def truncate_to_tokens(text, max_tokens, buffer_tokens=5000):
    words = text.split()
    approx_tokens = max_tokens - buffer_tokens
    return ' '.join(words[:int(approx_tokens)])



def run_extraction(convocatoria_id):
    full_text = get_full_text(convocatoria_id)
    if not full_text:
        print("Sense text per a la convocatòria indicada.")
        return []

    results = []
    for task in TASKS:
        field = task["field"]
        prompt_template = task["prompt"]
        print(f"→ {field}")

        prompt_openai = prompt_template.replace("{{TEXT}}", truncate_to_tokens(full_text, OPENAI_MAX_TOKENS))
        prompt_gemini = prompt_template.replace("{{TEXT}}", truncate_to_tokens(full_text, GEMINI_MAX_TOKENS))
        prompt_deepseek = prompt_template.replace("{{TEXT}}", truncate_to_tokens(full_text, DEEPSEEK_MAX_TOKENS))

        try:
            openai_resp = ask_openai(prompt_openai)
        except Exception as e:
            openai_resp = f"[OpenAI Error] {str(e)}"

        try:
            gemini_resp = ask_gemini(prompt_gemini)
        except Exception as e:
            gemini_resp = f"[Gemini Error] {str(e)}"

        try:
            deepseek_resp = ask_deepseek(prompt_deepseek)
        except Exception as e:
            deepseek_resp = f"[DeepSeek Error] {str(e)}"

        results.append({
            "camp": field,
            "prompt": prompt_template.replace("{{TEXT}}", "[TEXT]"),
            "OpenAI": openai_resp,
            "Gemini": gemini_resp,
            "DeepSeek": deepseek_resp
        })

    return results

def save_to_csv(results, convocatoria_id):
    if not results:
        return

    filename = f"comparativa_models_convocatoria_{convocatoria_id}.csv"
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["camp", "prompt", "OpenAI", "Gemini", "DeepSeek"])
        writer.writeheader()
        writer.writerows(results)

    print(f"\nResultats guardats a {filename}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Ús: python scripts/extract_single_comparison_csv.py <convocatoria_id>")
        sys.exit(1)

    convocatoria_id = int(sys.argv[1])
    results = run_extraction(convocatoria_id)
    save_to_csv(results, convocatoria_id)
