-- init_pgvector.sql
-- Crear l'extensió pgvector si no existeix
CREATE EXTENSION IF NOT EXISTS vector;

-- Comprovar si l'extensió s'ha creat correctament
SELECT * FROM pg_extension WHERE extname = 'vector';
