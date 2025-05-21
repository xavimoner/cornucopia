# scripts/list_documents_by_convocatoria.py

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def list_documents(convocatoria_id: int):
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cursor = conn.cursor()
    cursor.execute("""
        SELECT titulo, LEFT(texto, 300)
        FROM documentos
        WHERE convocatoria_id = %s
    """, (convocatoria_id,))
    rows = cursor.fetchall()

    if not rows:
        print(f"No s’han trobat documents per a la convocatòria ID {convocatoria_id}.")
    else:
        print(f"\nDocuments associats a la convocatòria ID {convocatoria_id}:\n")
        for title, snippet in rows:
            print(f"{title}\n   {snippet.strip()}\n{'-'*80}")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Ús: python scripts/list_documents_by_convocatoria.py <convocatoria_id>")
    else:
        list_documents(int(sys.argv[1]))
