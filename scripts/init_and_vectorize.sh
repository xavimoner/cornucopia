#!/bin/bash
# scripts/init_and_vectorize.sh

echo "Comprovant si hi ha documents nous o modificats per vectoritzar..."

docker compose up -d crawler_rag

echo "Entrant al contenidor i llançant la vectorització..."

docker exec -it crawler_rag bash -c "cd /app && python scripts/insert_documents_from_folder.py"

echo "Comprovació i vectorització completada."
