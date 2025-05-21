# scripts/list_summary.py

import os
import psycopg2
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

def list_summary():
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cursor = conn.cursor()

    query = """
    SELECT 
        c.id,
        c.nombre AS convocatoria,
        COUNT(d.id) AS num_documents,
        MAX(d.created_at) AS ultima_modificacio
    FROM convocatorias c
    LEFT JOIN documentos d ON c.id = d.convocatoria_id
    GROUP BY c.id, c.nombre
    ORDER BY ultima_modificacio DESC;
    """

    cursor.execute(query)
    rows = cursor.fetchall()
    headers = [desc[0] for desc in cursor.description]

    df = pd.DataFrame(rows, columns=headers)

    print(f"\n📋 Resum de la base de dades:\n")
    print(df.to_markdown(index=False))

    cursor.close()
    conn.close()

if __name__ == "__main__":
    list_summary()
