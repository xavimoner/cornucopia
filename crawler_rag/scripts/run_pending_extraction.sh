#!/bin/sh
# crawler_rag/scripts/run_pending_extraction.sh

LOG_DIR="/app/logs"
CRON_LOG_FILE="${LOG_DIR}/cron_pending_extraction.log" # Log específic per a aquesta tasca

echo "----------------------------------------------------" >> $CRON_LOG_FILE
echo "CRON_TASK: $(date +'%Y-%m-%d %H:%M:%S') - Iniciando extracción de convocatorias pendientes..." >> $CRON_LOG_FILE

cd /app 

python agents/unified_extraction_agent_crono.py --process-pending >> $CRON_LOG_FILE 2>&1
# Redirigim stdout i stderr de l'script de Python al mateix fitxer de log

echo "CRON_TASK: $(date +'%Y-%m-%d %H:%M:%S') - Extracción de convocatorias pendientes finalizada." >> $CRON_LOG_FILE
echo "----------------------------------------------------" >> $CRON_LOG_FILE