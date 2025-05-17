# todo.md
# Cornucopia - Guía rápida de comandos

Este documento reúne los comandos principales para operar el sistema Cornucopia desde la línea de comandos, mediante Docker o el Makefile.

---

## 1. Gestión de contenedores

**Levantar los contenedores:**

```bash
docker compose up -d --build
```

**Detener todos los contenedores:**

```bash
docker compose down
```

**Acceder al contenedor `crawler_rag`:**

```bash
docker exec -it crawler_rag bash
```

**Acceder al contenedor `db` (PostgreSQL):**

```bash
docker exec -it db psql -U admin -d cornucopia
```

**Ver contenedores activos:**

```bash
docker ps
```

---

## 2. Vectorización de documentos

**Vectorizar todos los documentos:**

```bash
docker exec -it crawler_rag python scripts/insert_documents_from_folder.py
```

**Vectorizar una subcarpeta concreta:**

```bash
docker exec -it crawler_rag python scripts/insert_documents_from_folder.py --subfolder "Nombre_Subcarpeta"
```

**Vectorizar en modo simulación (sin guardar datos):**

```bash
docker exec -it crawler_rag python scripts/insert_documents_from_folder.py --dry-run
```

---

## 3. Extracción de información

**Extraer campos definidos para todas las convocatorias:**

```bash
docker exec -it crawler_rag bash scripts/run_extraction.sh
```

---

## 4. Base de datos

**Listar convocatorias registradas:**

```bash
docker exec -it crawler_rag python scripts/list_convocatorias.py
```

**Resetear la base de datos (eliminar datos y recargar esquema):**

```bash
docker exec -it crawler_rag bash scripts/reset_schema.sh
```

**Probar conexión con la base de datos:**

```bash
docker exec -it crawler_rag python scripts/test_db_connection.py
```

---

## 5. Logs

**Consultar logs de vectorización:**

```bash
cat crawler_rag/logs/insert_documents.log
```

**Consultar logs de extracción:**

```bash
cat crawler_rag/logs/extraction_agent.log
```

---

## 6. Otros

**Reconstruir solo el contenedor `crawler_rag`:**

```bash
docker compose up -d --build crawler_rag
```

---

## Tabla resumen - comandos con Docker

| Acción                           | Comando principal                                                           |
|----------------------------------|------------------------------------------------------------------------------|
| Vectorizar documentos            | docker exec -it crawler_rag python scripts/insert_documents_from_folder.py  |
| Extraer campos de convocatorias | docker exec -it crawler_rag bash scripts/run_extraction.sh                  |
| Ver convocatorias registradas    | docker exec -it crawler_rag python scripts/list_convocatorias.py            |
| Resetear base de datos           | docker exec -it crawler_rag bash scripts/reset_schema.sh                    |

---

## Tabla resumen - comandos con Makefile

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
| Resetear solo los datos (no esquema)    | make reset_data                               |
| Hacer copia de seguridad de la BD       | make backup_db                                |
| Restaurar una copia de seguridad        | make restore_db FILE=backups/archivo.sql      |
| Reconstruir el frontend                 | make frontend                                 |
| Ver ayuda de todos los comandos         | make help                                     |

---
