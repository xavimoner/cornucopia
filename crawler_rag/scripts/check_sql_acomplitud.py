# scripts/check_sql_acomplitud.py

import os
import psycopg2
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def main():
    conn = psycopg2.connect(DATABASE_URL)
    query = "SELECT * FROM convocatorias ORDER BY id"
    df = pd.read_sql_query(query, conn)
    conn.close()

    df_valids = df.drop(columns=["created_at"]).copy()
    df_valids_boolean = df_valids.notnull() & df_valids.applymap(lambda x: str(x).strip() != "")

    df_valids_boolean["% camps omplerts"] = (df_valids_boolean.sum(axis=1) / len(df_valids_boolean.columns) * 100).round(1)

    df_resultat = df[["id"]].copy()
    df_resultat["% camps omplerts"] = df_valids_boolean["% camps omplerts"]

    print(df_resultat.to_string(index=False))

    output_file = "results/validacio_acomplitud_convocatories.csv"
    df_resultat.to_csv(output_file, index=False, encoding="utf-8")
    print(f"\nFitxer guardat: {output_file}")
if __name__ == "__main__":
    main()
