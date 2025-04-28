# scripts/run_extraction.sh

# Aquest script executa l'agent d'extracció unified_extraction_agent.py
# per extreure tots els camps definits per a una convocatòria concreta.

if [ -z "$1" ]; then
  echo "Has d'indicar l'ID de la convocatòria."
  echo "Ús: ./scripts/run_extraction.sh <convocatoria_id>"
  exit 1
fi

CONVOCATORIA_ID=$1

# Executem dins del contenidor crawler_rag

docker exec -it crawler_rag python crawler_rag/agents/unified_extraction_agent.py $CONVOCATORIA_ID
