# Makefile - Arrel del projecte Cornucopia

include .env.deploy
export

.PHONY: help reset reset_data init vectoritza extract extract_all comparacio \
        exporta export_one export_all_csv backup_db restore_db check_sql validate \
        check_model set_model frontend ensure_results_dir build push deploy_backend \
		deploy_crawler deploy_frontend deploy_all clean-repo force-push push-updates

ACR=cornucopiaacr.azurecr.io
RG=rg-fmoner
DB_IMAGE=postgres

# ─────────────────────────────────────────────
# AJUDA
# ─────────────────────────────────────────────
help:
	@echo "== SQL =="
	@echo " make reset, reset_data, check_sql"
	@echo "== EXTRACCIÓ =="
	@echo " make init, vectoritza, extract, extract_all, comparacio"
	@echo "== EXPORT =="
	@echo " make exporta, export_one, export_all_csv"
	@echo "== BACKUP =="
	@echo " make backup_db, restore_db"
	@echo "== CONFIG =="
	@echo " make set_model MODEL=..., check_model"
	@echo "== FRONTEND =="
	@echo " make frontend"
	@echo "== VALIDACIÓ =="
	@echo " make validate"
	@echo "== AZURE =="
	@echo " make build, push, deploy_backend, deploy_crawler, deploy_frontend, deploy_all"
	@echo "== GIT =="
	@echo " make push-updates, clean-repo, force-push"

# ─────────────────────────────────────────────
# SQL
# ─────────────────────────────────────────────
check_sql: ensure_results_dir
	docker exec -it crawler_rag bash -c "cd /app && python scripts/check_sql_acomplitud.py"

reset:
	docker compose down --volumes --remove-orphans
	docker volume rm cornucopia_postgres_data || true
	docker compose up -d db
	sleep 5
	docker compose up -d crawler_rag

reset_data:
	docker exec -it db psql -U admin -d cornucopia -c "TRUNCATE documentos, convocatorias RESTART IDENTITY CASCADE;"


# ─────────────────────────────────────────────
# EXTRACCIÓ
# ─────────────────────────────────────────────
init:
	docker compose up -d crawler_rag
	docker exec -it crawler_rag bash -c "cd /app && python scripts/insert_documents_from_folder.py"

vectoritza:
	docker exec -it crawler_rag bash -c "cd /app && python scripts/insert_documents_from_folder.py"

extract:
	docker exec -it crawler_rag bash -c "cd /app && python agents/unified_extraction_agent.py $(ID)"

extract_all:
	@docker exec db psql -U admin -d cornucopia -t -A -c "SELECT id FROM convocatorias" | \
	while read id; do \
		docker exec crawler_rag bash -c "cd /app && python agents/unified_extraction_agent.py $$id"; \
	done

comparacio: ensure_results_dir
	docker exec -it crawler_rag bash -c "cd /app && python scripts/extract_comparison_csv.py"

# ─────────────────────────────────────────────
# EXPORT
# ─────────────────────────────────────────────
exporta:
	docker exec -it crawler_rag bash -c "cd /app && python scripts/export_convocatoria_csv.py"

export_one:
	@if [ -z "$(ID)" ] || [ -z "$(FILE)" ]; then \
		echo "Ús: make export_one ID=<id> FILE=<nom_fitxer.csv>"; exit 1; \
	fi; \
	docker exec -it crawler_rag bash -c "cd /app && python scripts/export_convocatoria_csv.py $(ID) $(FILE)"

export_all_csv: ensure_results_dir
	docker exec -it crawler_rag bash -c "cd /app && python scripts/export_convocatoria_csv.py all all_convocatories.csv"

# ─────────────────────────────────────────────
# BACKUP
# ─────────────────────────────────────────────
backup_db:
	@mkdir -p backups
	@fecha=$$(date +"%Y%m%d_%H%M"); \
	docker exec db pg_dump -U admin -d cornucopia > backups/cornucopia_backup_$$fecha.sql; \
	echo "Còpia de seguretat creada a backups/cornucopia_backup_$$fecha.sql"

restore_db:
	@if [ -z "$(FILE)" ]; then \
		echo "Falta indicar el fitxer de còpia de seguretat."; \
		echo "Ús: make restore_db FILE=backups/nom_de_la_copia.sql"; exit 1; \
	fi; \
	cat $(FILE) | docker exec -i db psql -U admin -d cornucopia && \
	echo "Base de dades restaurada des de $(FILE)"

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
set_model:
	@if [ -z "$(MODEL)" ]; then \
		echo "Cal passar MODEL=OPENAI | GEMINI | DEEPSEEK"; exit 1; \
	fi; \
	sed -i 's/^LLM_PROVIDER=.*/LLM_PROVIDER=$(MODEL)/' .env && \
	echo "Model establert a $(MODEL). Reiniciant crawler..." && \
	docker compose restart crawler_rag

check_model:
	docker exec -it crawler_rag bash -c "cd /app && python scripts/check_active_model.py"

# ─────────────────────────────────────────────
# FRONTEND
# ─────────────────────────────────────────────
frontend:
	docker compose build frontend
	docker compose up -d frontend

# ─────────────────────────────────────────────
# VALIDACIÓ
# ─────────────────────────────────────────────
validate: ensure_results_dir
	docker exec -it crawler_rag bash -c "cd /app && python scripts/validate_fields.py"

# ─────────────────────────────────────────────
# AZURE
# ─────────────────────────────────────────────
build:
	docker build -t backend ./backend
	docker build -t crawler_rag ./crawler_rag
	docker build -t frontend ./frontend
	docker pull $(DB_IMAGE)

push:
	docker tag backend $(ACR)/backend:latest
	docker tag crawler_rag $(ACR)/crawler_rag:latest
	docker tag frontend $(ACR)/frontend:latest
	docker tag $(DB_IMAGE) $(ACR)/db:latest
	docker push $(ACR)/backend:latest
	docker push $(ACR)/crawler_rag:latest
	docker push $(ACR)/frontend:latest
	docker push $(ACR)/db:latest

deploy_backend:
	az containerapp update --name cornucopia-backend --resource-group $(RG) \
		--image $(ACR)/backend:latest \
		--env-vars \
			ENVIRONMENT=production \
			AZURE_OPENAI_API_KEY=$(AZURE_OPENAI_API_KEY) \
			AZURE_OPENAI_ENDPOINT=$(AZURE_OPENAI_ENDPOINT) \
			AZURE_OPENAI_API_VERSION=$(AZURE_OPENAI_API_VERSION) \
			AZURE_OPENAI_EMBEDDING_DEPLOYMENT=$(AZURE_OPENAI_EMBEDDING_DEPLOYMENT) \
			AZURE_OPENAI_CHAT_DEPLOYMENT=$(AZURE_OPENAI_CHAT_DEPLOYMENT) \
			DATABASE_URL=$(DATABASE_URL) \
			LLM_PROVIDER=$(LLM_PROVIDER)

deploy_crawler:
	az containerapp update --name cornucopia-crawler --resource-group $(RG) \
		--image $(ACR)/crawler_rag:latest \
		--env-vars \
			ENVIRONMENT=production \
			AZURE_OPENAI_API_KEY=$(AZURE_OPENAI_API_KEY) \
			AZURE_OPENAI_ENDPOINT=$(AZURE_OPENAI_ENDPOINT) \
			AZURE_OPENAI_API_VERSION=$(AZURE_OPENAI_API_VERSION) \
			AZURE_OPENAI_EMBEDDING_DEPLOYMENT=$(AZURE_OPENAI_EMBEDDING_DEPLOYMENT) \
			AZURE_OPENAI_CHAT_DEPLOYMENT=$(AZURE_OPENAI_CHAT_DEPLOYMENT) \
			DOCUMENTS_DIR=$(DOCUMENTS_DIR) \
			DATABASE_URL=$(DATABASE_URL) \
			LLM_PROVIDER=$(LLM_PROVIDER)

deploy_frontend:
	az containerapp update --name cornucopia-frontend --resource-group $(RG) \
		--image $(ACR)/frontend:latest

deploy_db:
	az containerapp create \
	  --name cornucopia-db \
	  --resource-group $(RG) \
	  --environment cornucopia-env \
	  --image $(ACR)/db:latest \
	  --target-port 5432 \
	  --ingress internal \
	  --registry-server $(ACR) \
	  --registry-username $$(az acr credential show --name cornucopiaacr --query username -o tsv) \
	  --registry-password $$(az acr credential show --name cornucopiaacr --query passwords[0].value -o tsv) \
	  --cpu 0.5 \
	  --memory 1.0Gi \
	  --env-vars \
	    POSTGRES_DB=cornucopia \
	    POSTGRES_USER=admin \
	    POSTGRES_PASSWORD=adminpass

deploy_all: deploy_db deploy_backend deploy_crawler deploy_frontend


# ─────────────────────────────────────────────
# COMANDES PER VEURE LOGS AZURE
# ─────────────────────────────────────────────
logs_backend:
	az containerapp logs show --name cornucopia-backend --resource-group $(RG)

logs_crawler:
	az containerapp logs show --name cornucopia-crawler --resource-group $(RG)

logs_frontend:
	az containerapp logs show --name cornucopia-frontend --resource-group $(RG)

logs_db:
	az containerapp logs show --name cornucopia-db --resource-group $(RG)



# ─────────────────────────────────────────────
# GIT
# ─────────────────────────────────────────────

clean-repo:
    # Elimina l'historial local i reinicialitza el repo
	rm -rf .git
	git init
	git add .
	git commit -m "Commit inicial net"

force-push:
	# Enllaça amb el remot i fa force push (sobrescriu tot)
	git remote add origin https://github.com/xavimoner/cornucopia.git || true
	git branch -M main
	git push --force origin main

push-updates:
	# Actualitza el repositori remot només amb els canvis locals
	git add .
	git commit -m "Actualització: $(shell date +'%Y-%m-%d %H:%M:%S')"
	git push origin main