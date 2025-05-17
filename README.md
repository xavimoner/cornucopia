# readme.md
# Cornucopia

Cornucopia es un sistema modular de extracción automática de información a partir de convocatorias de subvenciones. Utiliza agentes basados en modelos de lenguaje (LLM como Azure OpenAI o Google Gemini), un sistema de almacenamiento vectorial con PostgreSQL y pgvector, y un backend consultable mediante API.

---

## Estructura del proyecto

```
cornucopia/
├── backend/                # Backend FastAPI con agentes y modelos
├── crawler_rag/            # Agentes de extracción y vectorización de documentos
├── db/                     # Scripts de inicialización de la base de datos
├── frontend/               # Interfaz web del sistema
├── ollama/                 # Contenedor experimental para Ollama
├── vllm/                   # Contenedor experimental para vLLM
├── scripts/                # Scripts de gestión e inicialización
├── tests/                  # Pruebas unitarias
├── Makefile                # Tareas automatizadas del proyecto
├── docker-compose.yml      # Orquestador de servicios con Docker
├── requirements.txt        # Dependencias globales
├── LICENSE                 # Licencia del proyecto
├── README.md               # Este documento
└── .env.example            # Plantilla de variables de entorno
```

---

## Instalación

1. Clonar el repositorio y acceder al directorio:

```bash
git clone https://github.com/<usuario>/cornucopia.git
cd cornucopia
```

2. Crear el archivo `.env` a partir de `.env.example` y completar con tus claves:

```env
DATABASE_URL=postgresql://admin:adminpass@db:5432/cornucopia
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_ENDPOINT=...
GEMINI_API_KEY=...
LLM_PROVIDER=OPENAI
DOCUMENTS_DIR=crawler_rag/documents
```

---

## Lanzamiento con Docker

```bash
docker compose up -d --build
```

Para verificar que los servicios están activos:

```bash
docker ps
```

Servicios principales:

- `backend`: API FastAPI con agentes SQL y RAG
- `crawler_rag`: vectorización y extracción de documentos
- `db`: PostgreSQL + pgvector
- `frontend`: interfaz de usuario estática

---

## Carga de documentos

Coloca los documentos en subcarpetas dentro de `crawler_rag/documents/`.

Ejemplo:

```
crawler_rag/documents/CDTI - PID Individual/Convocatoria.pdf
```

---

## Vectorización de documentos

Desde el contenedor `crawler_rag`:

```bash
docker exec -it crawler_rag bash
python scripts/insert_documents_from_folder.py
```

Otras opciones:

- Vectorizar una carpeta concreta:

```bash
python scripts/insert_documents_from_folder.py --subfolder "CDTI - PID Individual"
```

- Simular vectorización sin guardar datos:

```bash
python scripts/insert_documents_from_folder.py --dry-run
```

---

## Extracción automática (Agentes LLM)

Ejecutar extracción por ID de convocatoria:

```bash
python scripts/run_extraction.sh 3
```

O bien:

```bash
make extract ID=3
```

---

## Uso del Makefile

El archivo `Makefile` permite ejecutar tareas frecuentes como reiniciar servicios, vectorizar documentos, cambiar de modelo, etc.

Consultar las opciones disponibles:

```bash
make help
```
---

## Tablas resumen de comandos

### Comandos con Docker

| Acción                           | Comando principal                                                           |
|----------------------------------|------------------------------------------------------------------------------|
| Vectorizar documentos            | docker exec -it crawler_rag python scripts/insert_documents_from_folder.py  |
| Extraer campos de convocatorias | docker exec -it crawler_rag bash scripts/run_extraction.sh                  |
| Ver convocatorias registradas    | docker exec -it crawler_rag python scripts/list_convocatorias.py            |
| Resetear base de datos           | docker exec -it crawler_rag bash scripts/reset_schema.sh                    |

### Comandos con Makefile

| Acción                                  | Comando con Makefile                          |
|-----------------------------------------|-----------------------------------------------|
| Iniciar contenedores y vectorizar       | make init                                     |
| Vectorizar nuevos documentos            | make vectoritza                               |
| Extraer una convocatoria concreta       | make extract ID=3                             |
| Extraer todas las convocatorias         | make extract_all                              |
| Exportar convocatorias a CSV            | make exporta                                  |
| Exportar convocatoria concreta a CSV    | make export_one ID=3 FILE=nombre.csv          |
| Validar campos extraídos                | make validate                                 |
| Cambiar modelo de lenguaje activo       | make set_model MODEL=GEMINI                   |
| Ver modelo actual                       | make check_model                              |
| Resetear completamente el sistema       | make reset                                    |
| Resetear solo los datos (no el esquema) | make reset_data                               |
| Hacer copia de seguridad de la BD       | make backup_db                                |
| Restaurar una copia de seguridad        | make restore_db FILE=backups/archivo.sql      |
| Reconstruir el frontend                 | make frontend                                 |
| Ver ayuda de todos los comandos         | make help                                     |


---

## Ejemplo completo

```bash
# 1. Colocar documentos en la carpeta documents/<Nombre>
# 2. Ejecutar:
make vectoritza
make extract ID=3
python scripts/list_convocatorias.py
```

---

## Desarrollo y pruebas

- Pruebas: `tests/`
- Scripts auxiliares: `scripts/`
- Colaboraciones: ver `CONTRIBUTING.md`

---

## Licencia

Este proyecto se distribuye bajo licencia MIT.
