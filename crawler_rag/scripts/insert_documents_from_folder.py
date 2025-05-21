# scripts/insert_documents_from_folder.py

"""
Script per inserir documents PDF a la base de dades 'documentos' i generar embeddings.
- Llegeix documents de la carpeta 'documents/'
- Insereix text complet i embedding
- Crea nova convocatòria si no existeix
- Actualitza documents si la seva data d'actualització és més recent
"""

import os
import sys
import psycopg2
import pdfplumber
from dotenv import load_dotenv
from datetime import datetime
from openai import AzureOpenAI
import tiktoken


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


load_dotenv()


client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

# Constants
LOG_PATH = "logs/insert_documents.log"
DOCUMENTS_DIR = "documents"

os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {msg}\n")
    print(msg)

def extract_text_from_pdf(path):
    with pdfplumber.open(path) as pdf:
        return "\n".join([p.extract_text() or "" for p in pdf.pages])

def split_text_if_needed(text, max_tokens=8000):
    encoding = tiktoken.encoding_for_model("gpt-4")
    tokens = encoding.encode(text)

    if len(tokens) <= max_tokens:
        return [text]

    chunks = []
    for i in range(0, len(tokens), max_tokens):
        chunk_tokens = tokens[i:i + max_tokens]
        chunk_text = encoding.decode(chunk_tokens)
        chunks.append(chunk_text)

    return chunks

def get_embedding(text):
    chunks = split_text_if_needed(text)
    embeddings = []
    for chunk in chunks:
        response = client.embeddings.create(
            input=[chunk],
            model=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
        )
        embeddings.append(response.data[0].embedding)

    if len(embeddings) == 1:
        return embeddings[0]
    else:
        avg = [sum(values) / len(values) for values in zip(*embeddings)]
        return avg

def insert_documents_from_folder(base_path=DOCUMENTS_DIR, subfolder=None, dry_run=False):
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cursor = conn.cursor()

    folders = [subfolder] if subfolder else os.listdir(base_path)

    for convocatoria_dir in folders:
        full_dir_path = os.path.join(base_path, convocatoria_dir)
        if not os.path.isdir(full_dir_path):
            continue

        cursor.execute("SELECT id FROM convocatorias WHERE nombre = %s", (convocatoria_dir,))
        result = cursor.fetchone()

        if result:
            convocatoria_id = result[0]
            log(f"Convocatòria existent: {convocatoria_dir} (ID {convocatoria_id})")
        else:
            if dry_run:
                log(f"[DRY-RUN] Nova convocatòria: {convocatoria_dir}")
                convocatoria_id = -1
            else:
                cursor.execute(
                    "INSERT INTO convocatorias (organismo, nombre) VALUES (%s, %s) RETURNING id",
                    ("CDTI", convocatoria_dir)
                )
                convocatoria_id = cursor.fetchone()[0]
                conn.commit()
                log(f"Nova convocatòria creada: {convocatoria_dir} (ID {convocatoria_id})")

        for file in os.listdir(full_dir_path):
            if not file.endswith(".pdf"):
                continue

            path = os.path.join(full_dir_path, file)
            file_mtime = datetime.fromtimestamp(os.path.getmtime(path))

            if not dry_run:
                cursor.execute("""
                    SELECT id, created_at FROM documentos
                    WHERE convocatoria_id = %s AND titulo = %s
                """, (convocatoria_id, file))
                doc = cursor.fetchone()
            else:
                doc = None

            if doc:
                doc_id, created_at = doc
                if file_mtime <= created_at:
                    log(f"{file} no actualitzat (sense canvis)")
                    continue
                else:
                    cursor.execute("DELETE FROM documentos WHERE id = %s", (doc_id,))
                    conn.commit()
                    log(f"{file} actualitzat (fitxer més recent)")

            text = extract_text_from_pdf(path)
            if not text.strip():
                log(f"PDF buit: {file}")
                continue

            embedding = get_embedding(text) if not dry_run else [0.0] * 1536

            if dry_run:
                log(f"[DRY-RUN] {file} es registraria amb vector i text")
            else:
                cursor.execute("""
                    INSERT INTO documentos (convocatoria_id, fuente, url, titulo, texto, embedding, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (convocatoria_id, "pdf", None, file, text, embedding, file_mtime))
                conn.commit()
                log(f"{file} inserit correctament (ID convocatòria {convocatoria_id})")

    cursor.close()
    conn.close()
    log("Procés finalitzat.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Insereix documents PDF vectoritzats a la base de dades")
    parser.add_argument("--subfolder", help="Nom d'una subcarpeta específica dins de documents/", default=None)
    parser.add_argument("--dry-run", action="store_true", help="Simula sense fer canvis a la base de dades")
    args = parser.parse_args()

    insert_documents_from_folder(subfolder=args.subfolder, dry_run=args.dry_run)
