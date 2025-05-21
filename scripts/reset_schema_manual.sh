#!/bin/bash
# reset_schema_manual.sh

echo "🧹 Eliminant i recreant l'esquema de la base de dades..."

# Variables (ajusta-les si cal)
DB_NAME="cornucopia"
DB_USER="admin"
SQL_FILE="db/init_db_schema.sql"

# Eliminar taules manualment en ordre de dependències
psql -U "$DB_USER" -d "$DB_NAME" -c "DROP TABLE IF EXISTS documentos CASCADE;"
psql -U "$DB_USER" -d "$DB_NAME" -c "DROP TABLE IF EXISTS convocatorias CASCADE;"

# Executar l'script SQL per crear les taules
psql -U "$DB_USER" -d "$DB_NAME" -f "$SQL_FILE"

echo "Esquema recreat correctament."
