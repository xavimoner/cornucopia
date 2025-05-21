# crawler_ragutils/insert_embeddings.py

import os
import psycopg2
from dotenv import load_dotenv
from openai import AzureOpenAI
import textwrap


load_dotenv()


client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

def split_paragraphs(text):
    return [p.strip() for p in textwrap.dedent(text).split("\n") if p.strip()]

def insert_fragments(documento_id, text):
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cursor = conn.cursor()

    parrafos = split_paragraphs(text)

    embeddings = client.embeddings.create(
        input=parrafos,
        model=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
    )

    for i, item in enumerate(embeddings.data):
        cursor.execute(
            """
            INSERT INTO fragmentos (documento_id, orden, parrafo, embedding)
            VALUES (%s, %s, %s, %s)
            """,
            (documento_id, i, parrafos[i], item.embedding)
        )

    conn.commit()
    cursor.close()
    conn.close()
    print(f"{len(parrafos)} fragments inserits per al document {documento_id}")
