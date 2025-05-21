#!/bin/bash
#scripts/run_vectorization.sh
# Entrar al contenidor crawler_rag i executar la vectorització

echo "💡 Vectoritzant documents des de /crawler_rag/scripts/insert_documents_from_folder.py ..."

docker exec -it crawler_rag bash -c "cd /app && python crawler_rag/scripts/insert_documents_from_folder.py"

echo "🎉 Vectorització finalitzada!"
