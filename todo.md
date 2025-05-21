# Cornucopia - Guía Rápida de Comandos

Este documento reúne los comandos principales para operar el sistema Cornucopia desde la línea de comandos, principalmente mediante Docker Compose y el `Makefile` proporcionado.

---

## 1. Gestión de Contenedores Docker

**Levantar todos los servicios (en segundo plano) y construir imágenes si es necesario:**

    docker compose up -d --build

**Levantar servicios específicos (ej: backend y base de datos):**

    docker compose up -d backend db

**Detener todos los servicios:**

    docker compose down

**Detener y eliminar volúmenes (¡CUIDADO: borra datos de la BD!):**

    docker compose down -v

**Ver contenedores activos:**

    docker ps

**Ver logs de un servicio (ej: backend):**

    docker compose logs -f backend

**Acceder a la shell de un contenedor en ejecución (ej: `crawler_rag`):**

    docker exec -it crawler_rag bash

**Acceder a la base de datos PostgreSQL (contenedor `db`):**

    docker exec -it db psql -U admin -d cornucopia 
    # (Reemplazar 'admin' y 'cornucopia' si se usan otros valores en .env)

**Reconstruir una imagen específica (ej: `backend`):**

    docker compose build backend
    # O para forzar la reconstrucción sin caché:
    docker compose build --no-cache backend

---

## 2. Carga Inicial de Documentos y Vectorización (Crawler RAG)

Estos comandos se ejecutan dentro del contenedor `crawler_rag` o a través de `make`. El script `insert_documents_from_folder.py` procesa PDFs ubicados en subcarpetas dentro de `crawler_rag/documents/`.

**Ejecutar la carga y vectorización de todos los documentos (a través de `make`):**
*(Esta acción también se realiza automáticamente al iniciar el contenedor `crawler_rag` por primera vez o si el entrypoint está configurado para ello)*

    make init
    # o
    make vectoritza

**Ejecutar directamente el script dentro del contenedor:**

    docker exec -it crawler_rag python scripts/insert_documents_from_folder.py

**Vectorizar solo una subcarpeta específica:**

    docker exec -it crawler_rag python scripts/insert_documents_from_folder.py --subfolder "Nombre_De_Tu_Subcarpeta"

**Simular la vectorización sin escribir en la base de datos (dry run):**

    docker exec -it crawler_rag python scripts/insert_documents_from_folder.py --dry-run

---

## 3. Extracción Estructurada de Datos (Crawler RAG)

Estos comandos utilizan `agents/unified_extraction_agent_crono.py` (o `unified_extraction_agent.py`) para rellenar los campos detallados de la tabla `convocatorias` usando un LLM.

**Extraer datos para una convocatoria específica por su ID (a través de `make`):**

    make extract ID=<id_de_la_convocatoria>

**Extraer datos para TODAS las convocatorias en la base de datos (a través de `make`):**
*(Puede ser un proceso largo y costoso en tokens LLM)*

    make extract_all

**Extraer datos SOLO para convocatorias pendientes (recomendado para actualizaciones periódicas, a través de `make`):**
*(Busca convocatorias con campos como 'organismo' o 'objetivo' marcados como '[Extracción Pendiente]' o NULL)*

    make extract_pending

**Ejecutar directamente el script de extracción para pendientes dentro del contenedor:**

    docker exec -it crawler_rag python agents/unified_extraction_agent_crono.py --process-pending

---

## 4. Base de Datos (Operaciones Comunes)

**Listar convocatorias registradas (ejecuta un script Python):**

    docker exec -it crawler_rag python scripts/list_convocatorias.py

**Resetear datos (TRUNCATE) de las tablas `documentos` y `convocatorias` (a través de `make`):**
*(Mantiene el esquema de la BD, solo borra los datos)*

    make reset_data

**Resetear completamente el entorno Docker (incluyendo volúmenes de BD, borra TODO):**

    make reset

**Hacer una copia de seguridad de la base de datos (a través de `make`):**
*(Guarda en `backups/cornucopia_backup_YYYYMMDD_HHMM.sql`)*

    make backup_db

**Restaurar la base de datos desde una copia de seguridad (a través de `make`):**

    make restore_db FILE=backups/nombre_del_backup.sql

---

## 5. Scripts de Verificación y Exportación (Crawler RAG)

**Verificar completitud de datos SQL (ejecuta un script Python):**

    make check_sql

**Generar CSV de comparación de extracción (ejecuta un script Python):**

    make comparacio

**Exportar todas las convocatorias a un CSV único (ejecuta un script Python):**

    make export_all_csv 
    # (Crea results/all_convocatories.csv)

**Exportar una convocatoria específica a un CSV (ejecuta un script Python):**

    make export_one ID=<id_convocatoria> FILE=nombre_fichero_salida.csv

---

## 6. Configuración del Modelo LLM

**Ver el proveedor LLM y modelo activo (según `.env`):**

    make check_model

**Cambiar el proveedor LLM activo para `crawler_rag` (modifica `.env` y reinicia `crawler_rag`):**

    make set_model MODEL=GEMINI 
    # Opciones: OPENAI, GEMINI, DEEPSEEK

---

## Tabla Resumen - Comandos `Makefile`

| Acción                                      | Comando con `Makefile`                      |
|---------------------------------------------|-----------------------------------------------|
| **General** |                                               |
| Ver todos los comandos disponibles          | `make help`                                   |
| Resetear completamente el sistema           | `make reset`                                  |
| **Base de Datos** |                                               |
| Resetear solo datos (no esquema)            | `make reset_data`                             |
| Hacer copia de seguridad de la BD           | `make backup_db`                              |
| Restaurar copia de seguridad                | `make restore_db FILE=path/al/backup.sql`     |
| **Ingesta y Procesamiento Inicial** |                                               |
| Carga masiva y vectorización inicial        | `make init` o `make vectoritza`               |
| **Extracción Estructurada** |                                               |
| Extraer para una convocatoria por ID        | `make extract ID=<id>`                        |
| Extraer para TODAS las convocatorias        | `make extract_all`                            |
| Extraer para convocatorias PENDIENTES       | `make extract_pending`                        |
| **Verificación y Exportación** |                                               |
| Verificar completitud SQL                   | `make check_sql`                              |
| Generar CSV de comparación de extracción    | `make comparacio`                             |
| Exportar todas las convocatorias a CSV      | `make export_all_csv`                         |
| Exportar una convocatoria a CSV             | `make export_one ID=<id> FILE=fichero.csv`    |
| **Configuración LLM** |                                               |
| Ver modelo LLM activo                       | `make check_model`                            |
| Cambiar proveedor LLM para `crawler_rag`    | `make set_model MODEL=<PROVEEDOR>`            |
| **Despliegue Azure (Ejemplos)** |                                               |
| Construir todas las imágenes Docker         | `make build`                                  |
| Subir imágenes a ACR                        | `make push`                                   |
| Desplegar todos los servicios en Azure      | `make deploy_all`                             |
| Ver logs de un servicio en Azure (ej: backend) | `make logs_backend`                         |

*(Nota: Para los comandos de Azure iniciar sesión con `az login` y de tener configuradas las variables en `.env.deploy` o pasarlas al comando `make`).*

---