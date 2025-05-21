#!/bin/sh
# crawler_rag/scripts/entrypoint.sh

echo "CRAWLER_RAG ENTRYPOINT: Iniciando..."

# Espera a PostgreSQL (si DB_HOST i DB_PORT estan definits)
DB_HOST=$(echo $DATABASE_URL | sed -n 's_.*@\([^:]*\):.*_\1_p')
DB_PORT=$(echo $DATABASE_URL | sed -n 's_.*:\([0-9]*\)/.*_\1_p')

if [ -n "$DB_HOST" ] && [ -n "$DB_PORT" ]; then
    echo "CRAWLER_RAG ENTRYPOINT: Esperando que PostgreSQL ($DB_HOST:$DB_PORT) esté disponible..."
    max_wait=30
    count=0
    while ! nc -z $DB_HOST $DB_PORT; do   
      sleep 1
      count=$(expr $count + 1)
      if [ $count -ge $max_wait ]; then
        echo "CRAWLER_RAG ENTRYPOINT ERROR: Timeout esperando a PostgreSQL."
        # Decideix si vols que l'script falli o continuï amb una advertència
        # exit 1 # Per fallar
        break  # Per continuar amb una advertència
      fi
    done
    if [ $count -lt $max_wait ]; then
      echo "CRAWLER_RAG ENTRYPOINT: PostgreSQL disponible!"
    fi
else
    echo "CRAWLER_RAG ENTRYPOINT WARN: No se han definido DB_HOST/DB_PORT. Continuando sin espera explícita para la BD."
fi

echo "CRAWLER_RAG ENTRYPOINT: Ejecutando carga inicial de documentos y embeddings (scripts/insert_documents_from_folder.py)..."
cd /app 
python scripts/insert_documents_from_folder.py # Processa totes les carpetes per defecte
echo "CRAWLER_RAG ENTRYPOINT: Carga inicial de documentos y embeddings finalizada."

#  extracció estructurada per a convocatòries pendents
echo "CRAWLER_RAG ENTRYPOINT: Ejecutando extracción estructurada para convocatorias pendientes (agents/unified_extraction_agent_crono.py --process-pending)..."
python agents/unified_extraction_agent_crono.py --process-pending
echo "CRAWLER_RAG ENTRYPOINT: Extracción estructurada para convocatorias pendientes finalizada."


echo "CRAWLER_RAG ENTRYPOINT: Iniciando servicio CRON en segundo plano..."
cron # start dimoni cron en segon pla
   
echo "CRAWLER_RAG ENTRYPOINT: Iniciando CMD original del Dockerfile: $@"
exec "$@" # Executa el CMD definit  Dockerfile 