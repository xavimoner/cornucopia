
# crawler_rag/utils/delete_test_data.py

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def delete_test_data(convocatoria_name="Convocatòria Test TFM"):
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cursor = conn.cursor()

    # Trobar la convocatòria per nom
    cursor.execute(
        "SELECT id FROM convocatorias WHERE nombre = %s",
        (convocatoria_name,)
    )
    row = cursor.fetchone()
    if not row:
        print(f"No s'ha trobat cap convocatòria amb nom: {convocatoria_name}")
        conn.close()
        return
    convocatoria_id = row[0]

    print(f"🗑️ Esborrant dades de la convocatòria amb ID {convocatoria_id}...")

    # Esborrar fragments
    cursor.execute("""
        DELETE FROM fragmentos
        WHERE documento_id IN (
            SELECT id FROM documentos WHERE convocatoria_id = %s
        )
    """, (convocatoria_id,))

    # Esborrar documents
    cursor.execute("DELETE FROM documentos WHERE convocatoria_id = %s", (convocatoria_id,))

    # Esborrar convocatòria
    cursor.execute("DELETE FROM convocatorias WHERE id = %s", (convocatoria_id,))

    conn.commit()
    cursor.close()
    conn.close()

    print("S'han esborrat correctament els fragments, documents i convocatòria de prova.")