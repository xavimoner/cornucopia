#!/bin/bash
# scripts/reset_full_db.sh

echo "Aturant i eliminant el contenidor i volum de la base de dades..."

docker compose down -v --remove-orphans

echo "Tornant a crear els contenidors..."
docker compose up -d db

echo "Esperant que la base de dades estigui disponible..."
sleep 5

echo "Executant l'script SQL de creació d'esquema..."
docker exec -i db psql -U admin -d cornucopia < db/init_db_schema.sql

echo "Base de dades reiniciada i esquema aplicat correctament!"
