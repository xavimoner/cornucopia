-- ./db/init_pgvector.sql
\echo 'SCRIPT: Iniciant creació extensió pgvector...'
CREATE EXTENSION IF NOT EXISTS vector;
\echo 'SCRIPT: Extensió pgvector creada (o ja existia).'