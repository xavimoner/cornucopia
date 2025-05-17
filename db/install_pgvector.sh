#!/bin/bash
# db/install_pgvector.sh

echo "🔹 Instal·lant pgvector per a PostgreSQL..."

# Actualitzem repositoris
apt-get update

# Instal·lem pgvector per a PostgreSQL 17
apt-get install -y postgresql-17-pgvector

# Creem l'extensió dins la base de dades cornucopia
psql -U admin -d cornucopia -c "CREATE EXTENSION IF NOT EXISTS vector;"

# Comprovació final
psql -U admin -d cornucopia -c "SELECT * FROM pg_extension WHERE extname = 'vector';"

echo "pgvector instal·lat i activat correctament."
