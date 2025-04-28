# readme.md
# Cornucopia

Sistema de extracción de información de convocatorias de subvenciones mediante agentes LLM (Azure OpenAI o Google Gemini), almacenamiento vectorial y base de datos PostgreSQL con pgvector.

---

## Estructura de carpetas

cornucopia/
├── backend/                    # Servicio FastAPI
├── crawler_rag/
│   ├── agents/                  # Agentes de extracción
│   ├── documents/               # Documentos a procesar
│   ├── logs/                    # Registros de vectorización y extracción
│   ├── scripts/                 # Scripts operativos
│   ├── utils/                   # Funciones auxiliares
│   └── vault/                   # Archivos antiguos o de pruebas
├── db/                          # Scripts de base de datos
├── docker-compose.yml           # Configuración de servicios Docker
├── requirements.txt             # Dependencias Python
├── .dockerignore                # Ignorar archivos Docker
├── .gitignore                   # Ignorar archivos Git
└── README.md                    # Este documento

(Servicios en staandby)
- `vllm/` → Configuración de servidor vLLM (opcional)
- `ollama/` → Configuración de servidor Ollama (opcional)

---

## Instalación

### 1. Clonar el repositorio

git clone https://github.com/<usuario>/cornucopia.git  
cd cornucopia

### 2. Crear el archivo `.env`

Crear manualmente un archivo `.env` con contenido como:

DATABASE_URL=postgresql://admin:adminpass@db:5432/cornucopia  
AZURE_OPENAI_API_KEY=...  
AZURE_OPENAI_ENDPOINT=...  
AZURE_OPENAI_API_VERSION=...  
GEMINI_API_KEY=...  
GEMINI_MODEL=gemini-1.5-flash  
DOCUMENTS_DIR=crawler_rag/documents  

*(Rellenar solo Azure o Gemini según el modelo que se quiera usar.)*

---

## Lanzar servicios Docker

### 1. Construir y levantar servicios

docker compose up -d --build

### 2. Comprobar servicios activos

docker ps

**Servicios disponibles:**
- `db` ➔ PostgreSQL + pgvector
- `backend` ➔ FastAPI
- `crawler_rag` ➔ Vectorización y extracción

---

## Cargar documentos

Colocar documentos PDF o Word en:

crawler_rag/documents/Nombre_Convocatoria/

Ejemplo:

crawler_rag/documents/CDTI - PID Individual/Convocatoria_PID.pdf

---

## Vectorizar documentos

### 1. Entrar en el contenedor `crawler_rag`

docker exec -it crawler_rag bash

### 2. Vectorizar todos los documentos

python scripts/insert_documents_from_folder.py

### Vectorizar solo una subcarpeta

python scripts/insert_documents_from_folder.py --subfolder "CDTI - PID Individual"

### Vectorizar en modo simulación (sin modificar base de datos)

python scripts/insert_documents_from_folder.py --dry-run

---

## Extracción de información (Agentes LLM)

### Lanzar extracción

python scripts/run_extraction.sh

Extracción de campos: línea, objetivo, beneficiarios, duración, presupuesto, etc.

---

## Utilidades adicionales

### Reiniciar base de datos (elimina todo)

bash scripts/reset_schema.sh

### Listar convocatorias existentes

python scripts/list_convocatorias.py

### Test de conexión a la base de datos

python scripts/test_db_connection.py

---

## Ejemplo de uso completo

# 1. Subir documentos a `crawler_rag/documents/`
# 2. Vectorizar

docker exec -it crawler_rag bash  
python scripts/insert_documents_from_folder.py

# 3. Lanzar extracción

python scripts/run_extraction.sh

# 4. Consultar base de datos

python scripts/list_convocatorias.py

---

# ¡Listo para usar!

Con estos pasos podrás vectorizar, extraer y consultar automáticamente información de convocatorias de ayudas.

---


---
