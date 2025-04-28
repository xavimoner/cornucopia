# Cornucopia - Comandos Rápidos

Guía rápida de comandos para trabajar con el proyecto Cornucopia.

---

## 1. Docker

**Levantar contenedores:**

```bash
docker compose up -d --build
```

**Parar contenedores:**

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

---

## 2. Vectorización de documentos

**Vectorizar toda la carpeta de documentos:**

```bash
docker exec -it crawler_rag python scripts/insert_documents_from_folder.py
```

**Vectorizar una subcarpeta específica:**

```bash
docker exec -it crawler_rag python scripts/insert_documents_from_folder.py --subfolder "Nombre_Subcarpeta"
```

**Simular vectorización (modo prueba):**

```bash
docker exec -it crawler_rag python scripts/insert_documents_from_folder.py --dry-run
```

---

## 3. Extracción de campos

**Ejecutar extracción de todos los campos definidos:**

```bash
docker exec -it crawler_rag bash scripts/run_extraction.sh
```

---

## 4. Administración de Base de Datos

**Listar todas las convocatorias registradas:**

```bash
docker exec -it crawler_rag python scripts/list_convocatorias.py
```

**Resetear la base de datos (borrar todo y recrear esquema):**

```bash
docker exec -it crawler_rag bash scripts/reset_schema.sh
```

**Testear conexión a la base de datos:**

```bash
docker exec -it crawler_rag python scripts/test_db_connection.py
```

---

## 5. Logs

**Consultar logs de vectorización:**

```bash
cat crawler_rag/logs/insert_documents.log
```

**Consultar logs de extracción de campos:**

```bash
cat crawler_rag/logs/extraction_agent.log
```

---

## 6. Otros

**Ver servicios activos:**

```bash
docker ps
```

**Reconstruir solo el contenedor `crawler_rag`:**

```bash
docker compose up -d --build crawler_rag
```

---

# Tabla Resumen

| Acción                        | Comando principal                                                      |
|:-------------------------------|:------------------------------------------------------------------------|
| Vectorizar documentos          | docker exec -it crawler_rag python scripts/insert_documents_from_folder.py |
| Extraer campos de convocatorias| docker exec -it crawler_rag bash scripts/run_extraction.sh              |
| Ver convocatorias registradas  | docker exec -it crawler_rag python scripts/list_convocatorias.py        |
| Resetear base de datos         | docker exec -it crawler_rag bash scripts/reset_schema.sh                |

---

