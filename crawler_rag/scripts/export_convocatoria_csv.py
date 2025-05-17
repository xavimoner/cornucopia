# scripts/export_convocatoria_csv.py
import csv
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def export_convocatoria_to_csv(convocatoria_id, filename):
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM convocatorias WHERE id = %s", (convocatoria_id,))
    row = cursor.fetchone()
    
    if not row:
        print(f"No s'ha trobat cap convocatòria amb id {convocatoria_id}")
        return

    # Agafa els noms de columna
    colnames = [desc[0] for desc in cursor.description]

    output_path = os.path.join("results", filename)

    with open(output_path, "w", encoding="utf-8", newline="") as f:

        writer = csv.writer(f)
        writer.writerow(colnames)
        writer.writerow(row)

    print(f"Exportació completada a {output_path}")
    cursor.close()
    conn.close()

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Ús: python scripts/export_convocatoria_csv.py <convocatoria_id> <filename>")
    else:
        export_convocatoria_to_csv(int(sys.argv[1]), sys.argv[2])
