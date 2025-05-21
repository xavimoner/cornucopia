# crawler_rag/scripts/validate_fields.py

import os
import psycopg2
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()
cursor.execute("SELECT * FROM convocatorias")
rows = cursor.fetchall()
columns = [desc[0] for desc in cursor.description]
df = pd.DataFrame(rows, columns=columns)

respostes_invalides = [
    "por favor proporciona", "según el texto", "basándome en el texto",
    "[error", "no se especifica", "no se menciona", "proporciona el texto"
]

def valida(x):
    if pd.isna(x) or str(x).strip() == "":
        return False
    return not any(p in str(x).lower() for p in respostes_invalides)

cols = [col for col in df.columns if col not in ("id", "created_at")]
df_val = df[["id"]].copy()

for col in cols:
    df_val[col] = df[col].apply(valida)

df_val["% camps vàlids"] = (df_val[cols].sum(axis=1) / len(cols) * 100).round(1)
df_val.to_csv("validacio_convocatories.csv", index=False)
print("Informe de validació guardat a validacio_convocatories.csv")
