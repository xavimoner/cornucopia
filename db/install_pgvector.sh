#!/bin/bash
# install_pgvector.sh

# Actualitzem els repositoris
apt-get update -y

# Instal·lem pgvector per a PostgreSQL 17
apt-get install -y postgresql-17-pgvector

# Si no existeix, creem extensió pgvector a la base de dades
psql -U admin -d cornucopia -c "CREATE EXTENSION IF NOT EXISTS vector;"

# Verifiquem que extensió pgvector s'ha creat 
psql -U admin -d cornucopia -c "SELECT * FROM pg_extension WHERE extname = 'vector';"
