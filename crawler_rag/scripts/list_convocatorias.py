
# scripts/list_convocatorias.py

import os
import psycopg2
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

def list_convocatorias():
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cursor = conn.cursor()

    query = '''
    SELECT c.id, c.organismo, c.nombre,
        COUNT(d.id) AS n_documents
    FROM convocatorias c
    LEFT JOIN documentos d ON c.id = d.convocatoria_id
    GROUP BY c.id, c.organismo, c.nombre
    ORDER BY c.id;
    '''

    cursor.execute(query)
    rows = cursor.fetchall()
    headers = [desc[0] for desc in cursor.description]

    df = pd.DataFrame(rows, columns=headers)

    cursor.close()
    conn.close()

    if df.empty:
        print("No hi ha convocatòries registrades.")
    else:
        print(df.to_markdown(index=False))

if __name__ == "__main__":
    list_convocatorias()
