# scripts/run_extraction.sh

# executa l'agent d'extracció unified_extraction_agent.py
# per extreure tots els camps definits per a una convocatòria concreta.

if [ -z "$1" ]; then
  echo "Has d'indicar l'ID de la convocatòria."
  echo "Ús: ./scripts/run_extraction.sh <convocatoria_id>"
  exit 1
fi

CONVOCATORIA_ID=$1

echo "▶ Executant extracció per a la convocatòria ID $CONVOCATORIA_ID..."

docker exec -it crawler_rag bash -c "cd /app && python agents/unified_extraction_agent.py $CONVOCATORIA_ID"