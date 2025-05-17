#!/bin/bash
# reset_schema_docker.sh

# crawler_rag/scripts/reset_schema.sh
#!/bin/bash

echo "Això esborrarà completament la base de dades 'cornucopia'. Vols continuar? (sí/no)"
read confirm

if [[ "$confirm" != "sí" ]]; then
  echo "Cancel·lat."
  exit 1
fi

echo "Aturant i esborrant el contenidor i el volum de la base de dades..."
docker compose down -v

echo "Tornant a aixecar els contenidors amb el nou esquema..."
docker compose up -d --build

echo "Esquema reiniciat correctament. Comprova amb: docker exec -it db psql -U admin -d cornucopia"

