
# backend/tasks/rag_task.py

from sqlalchemy import text
from db import get_db
from fastapi import Depends
from sentence_transformers import SentenceTransformer

class RAGTask:
    def __init__(self, db=Depends(get_db)):
        self.db = db
        self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    async def run(self, query: str) -> str:
        # Obtenir l'embedding de la consulta
        query_embedding = self.model.encode(query, normalize_embeddings=True).tolist()

        # Fer la consulta vectorial amb pgvector x coseno
        sql = text("""
            SELECT titulo, fuente, url, texto,
                   1 - (embedding <#> CAST(:embedding AS vector)) AS similarity
            FROM documentos
            ORDER BY embedding <#> CAST(:embedding AS vector)
            LIMIT 3;
        """)

        resultats = self.db.execute(sql, {"embedding": query_embedding}).fetchall()

        if not resultats:
            return "No s'ha trobat cap document rellevant per la teva consulta."

        resposta = ""
        for i, row in enumerate(resultats, 1):
            resposta += (
                f"[{i}] {row.titulo or '(Sense títol)'} — {row.fuente or ''}\n"
                f"{row.texto[:400].strip()}...\n"
                f"Enllaç: {row.url or 'No disponible'}\n\n"
            )

        return resposta.strip()
