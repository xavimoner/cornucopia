# crawler_rag/agents/unified_extraction_agent.py

import os
import sys
import psycopg2
import tiktoken
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.extraction_tasks import TASKS
from agents.llm_client import ask_gemini, GEMINI_MAX_TOKENS


load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


def get_full_text(convocatoria_id):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("SELECT texto FROM documentos WHERE convocatoria_id = %s", (convocatoria_id,))
    textos = [row[0] for row in cursor.fetchall() if row[0] and len(row[0].strip()) > 0]
    cursor.close()
    conn.close()
    
    if not textos:
        print(f"[WARN] No s'ha trobat text per a la convocatòria {convocatoria_id}")
    else:
        print(f"[INFO] {len(textos)} documents trobats per a la convocatòria {convocatoria_id}")
    
    return "\n\n".join(textos).strip()


def truncate_to_max_tokens(text: str, max_tokens: int, model_name: str = "gemini") -> str:
    try:
        encoding = tiktoken.encoding_for_model(model_name)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")

    tokens = encoding.encode(text)
    if len(tokens) <= max_tokens:
        return text
    truncated_tokens = tokens[:max_tokens]
    return encoding.decode(truncated_tokens)


def run_extraction(convocatoria_id):
    full_text = get_full_text(convocatoria_id)
    if not full_text:
        print("Sense text per a la convocatòria indicada.")
        return []

    results = []
    for field, prompt_template in TASKS.items():
        print(f"→ {field}")
        prompt = prompt_template.replace("{{TEXT}}", truncate_to_max_tokens(full_text, int(GEMINI_MAX_TOKENS * 0.75)))
        try:
            response = ask_gemini(prompt)
        except Exception as e:
            response = f"[Gemini Error] {str(e)}"

        results.append({
            "camp": field,
            "Gemini": response
        })

    return results


def save_to_sql(results, convocatoria_id):
    if not results:
        print("No hi ha resultats per guardar a SQL.")
        return

    invalid_responses = [
        "por favor proporciona", "proporciona el texto", "please provide", "please input",
        "envíame el texto", "no se ha proporcionado el texto", "no se ha detectado texto"
    ]

    new_data = {}
    for r in results:
        field = r["camp"]
        value = r.get("Gemini", "").strip()
        if not value:
            continue
        if any(p in value.lower() for p in invalid_responses):
            continue
        new_data[field] = value

    if not new_data:
        print("Cap resposta vàlida de Gemini per guardar.")
        return

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        query_check = f"""
            SELECT {', '.join(new_data.keys())}
            FROM convocatorias
            WHERE id = %s
        """
        cursor.execute(query_check, (convocatoria_id,))
        current_row = cursor.fetchone()

        if not current_row:
            print(f"[ERROR] No s'ha trobat la convocatòria amb ID {convocatoria_id}.")
            cursor.close()
            conn.close()
            return

        columns_changed = []
        values_to_update = []

        for i, field in enumerate(new_data.keys()):
            current_value = current_row[i] if current_row[i] is not None else ""
            new_value = new_data[field]
            if str(current_value).strip() != new_value.strip():
                columns_changed.append(f"{field} = %s")
                values_to_update.append(new_value)

        if not columns_changed:
            print(f"No hi ha canvis per guardar a la convocatòria ID {convocatoria_id}.")
            cursor.close()
            conn.close()
            return

        update_query = f"""
            UPDATE convocatorias
            SET {', '.join(columns_changed)}
            WHERE id = %s
        """
        values_to_update.append(convocatoria_id)
        cursor.execute(update_query, values_to_update)
        conn.commit()

        print(f"S'han actualitzat {len(columns_changed)} camps per a la convocatòria ID {convocatoria_id}.")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"[ERROR SQL] {str(e)}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Ús: python unified_extraction_agent.py <convocatoria_id>")
        sys.exit(1)

    convocatoria_id = int(sys.argv[1])
    results = run_extraction(convocatoria_id)
    #save_to_csv(results, convocatoria_id)
    save_to_sql(results, convocatoria_id)


 

