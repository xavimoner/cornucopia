# Cornucopia: Consultor inteligente de subvenciones y ayudas públicas

Cornucopia es un sistema integral diseñado para la extracción, gestión y consulta inteligente de información sobre convocatorias de subvenciones y ayudas públicas. Utiliza un pipeline de procesamiento de datos que incluye scraping web, descarga y análisis de documentos (PDF, texto), generación de embeddings vectoriales para búsqueda semántica, y extracción estructurada de información mediante Grandes Modelos de Lenguaje (LLM) como Google Gemini.

El sistema cuenta con un backend FastAPI que expone una API para todas las funcionalidades, una base de datos PostgreSQL con la extensión pgvector para el almacenamiento eficiente de datos y vectores, y un frontend web interactivo que permite a los usuarios realizar consultas en lenguaje natural y a los administradores gestionar la ingesta de nuevas convocatorias.

---

## Características principales

* **Consulta en lenguaje natural**: Interfaz de chat para que los usuarios busquen subvenciones y ayudas.
* **Ingesta de convocatorias asistida por administrador**: Panel de administración para introducir URLs de convocatorias, con scraping automático de la página web y descarga de PDFs adjuntos.
* **Gestión de documentos**: Posibilidad de subir manualmente documentos adicionales (PDF, TXT, MD, DOCX) durante el proceso de ingesta.
* **Procesamiento de texto y vectorización**: Extracción de texto de documentos y generación de embeddings (vectores semánticos) mediante Azure OpenAI Embeddings para su posterior búsqueda.
* **Extracción estructurada de datos**: Uso de LLMs (configurable, por defecto Google Gemini) para analizar el texto de las convocatorias y rellenar automáticamente los campos detallados de la base de datos (organismo, fechas, presupuesto, etc.). Esta extracción se puede ejecutar para convocatorias individuales o para todas las pendientes.
* **Autenticación y roles**: Sistema de usuarios con roles (usuario, administrador) y autenticación basada en tokens JWT.
* **Arquitectura modular y escalable**: Basada en contenedores Docker y Docker Compose para facilitar el despliegue y la gestión.

---

## Stack tecnológico

* **Backend**: Python, FastAPI, SQLAlchemy, Psycopg2 (para scripts), Playwright (para scraping).
* **Frontend**: HTML, CSS, JavaScript vainilla, Nginx (como servidor web y reverse proxy).
* **Base de datos**: PostgreSQL + pgvector.
* **LLMs & embeddings**:
    * Embeddings: Azure OpenAI API.
    * Extracción Estructurada y Chat (configurable): Google Gemini API (vía `llm_client.py` o Google ADK).
    * Agentes de Chat: Google Agent Development Kit (ADK).
* **Contenerización**: Docker, Docker Compose.
* **Otros**: Tiktoken (para tokenización de texto).

---

## Componentes experimentales y desarrollos previos (cadáveres que hemos dejado por el camino)

Durante el desarrollo de Cornucopia, se exploraron diversas aproximaciones y herramientas que, aunque no forman parte de la versión final del sistema principal, representan etapas importantes de investigación y aprendizaje. Los directorios correspondientes a estos desarrollos se conservan en el repositorio como referencia:

* **`OLLAMA/`**:
    Este directorio contiene la configuración para un contenedor Docker con Ollama. Representó un primer intento de integrar y utilizar modelos de lenguaje grandes (LLMs) de forma local, buscando alternativas a las APIs de modelos propietarios.

* **`VLLM/`**:
    Aquí se encuentra la configuración para un contenedor Docker con vLLM. Esta herramienta, más potente y versátil que Ollama para la inferencia de LLMs, se exploró inicialmente para ejecución en CPU y posteriormente se investigó su compatibilidad con GPUs NVIDIA, con el objetivo de optimizar la velocidad y eficiencia de los modelos locales.

* **`crawler_cdti/`**:
    Este fue el primer *crawler* desarrollado específicamente para automatizar la navegación y extracción de información de la página web del CDTI (Centro para el Desarrollo Tecnológico Industrial). Aunque funcional para su objetivo, se descartó como solución general debido a que su diseño era demasiado específico para una única fuente de datos, cuya estructura y tecnología presentaban una complejidad técnica considerable. Replicar un *crawler* a medida para cada nueva fuente de convocatorias no resultaba escalable.

* **`auto_crawler/`**:
    Este directorio contiene los desarrollos relacionados con un agente de Hugging Face (Smolagents )de navegación y crawling autonomo. Representó un segundo intento de crear una herramienta más genérica capaz de automatizar la búsqueda y actualización de información de convocatorias en diversas páginas web. A pesar de desarrollar hasta 30 herramientas (`tools`) específicas para este agente, y de lograr que navegara con éxito por la página del CDTI, se encontraron dificultades significativas para generalizar su comportamiento a otras páginas con estructuras y tecnologías web variadas. La investigación sobre cómo mejorar la adaptabilidad de estos agentes autónomos queda como un área de estudio pendiente.

El principal desafío encontrado durante estos desarrollos fue la enorme diversidad en las formas en que las entidades publican documentos, presentan enlaces, estructuran los menús y utilizan scripts en sus sitios web. Esta heterogeneidad dificulta enormemente la creación de un sistema de *crawling* y extracción de información completamente automatizado y universal, lo que llevó a la solución actual de ingesta asistida por administrador para el `backend` principal.

---



---

## Estructura del proyecto

cornucopia/  
├── backend/                # API FastAPI, lógica de ingesta, autenticación,   endpoints de chat  
├── crawler_rag/            # Scripts para carga masiva inicial, vectorización y extracción estructurada  
│   ├── agents/             # Agentes LLM (unified_extraction_agent.py, unified_extraction_agent_crono.py)  
│   ├── scripts/            # Scripts de utilidad, entrypoint.sh, crontab  
│   └── documents/          # (Local) Directorio para la carga masiva inicial de PDFs (organizados en subcarpetas    por convocatoria)
├── db/                     # Scripts SQL para inicialización del esquema de la BD  
├── frontend/               # Interfaz web estática (HTML, CSS, JS, Nginx config)  
├── backups/                # (Local) Directorio para copias de seguridad de la BD  
├── .env                    # (Local, NO SUBIR A GIT) Variables de entorno  
├── .env.example            # Plantilla para el archivo .env  
├── .env.deploy             # (Opcional) Variables para despliegue (usado por Makefile)  
├── .env.deploy.example     # Plantilla para .env.deploy  
├── Makefile                # Tareas automatizadas para desarrollo, build, deploy, etc.  
├── docker-compose.yml      # Orquestación de los servicios Docker  
├── requirements.txt        # Dependencias globales (si alguna, aunque cada servicio tiene la suya)  
├── backend/requirements.txt # Dependencias del backend  
├── crawler_rag/requirements.txt # Dependencias de crawler_rag  
├── LICENSE                 # Licencia del proyecto  
└── README.md               # Este documento  

*(Nota: Los directorios `ollama/` y `vllm/` se han omitido, ya que no forman parte del proyecto actual).*

---

## Instalación y puesta en marcha local

1.  **Clonar el repositorio**:
    ```bash
    git clone [https://github.com/tu_usuario/cornucopia.git](https://github.com/tu_usuario/cornucopia.git) # Reemplaza con tu URL
    cd cornucopia
    ```

2.  **Configurar variables de entorno**:
    * Copia `.env.example` a `.env` y rellena todas las variables requeridas:
        ```bash
        cp .env.example .env
        nano .env # O tu editor preferido
        ```
    * Variables clave a configurar en `.env`:
        * `DATABASE_URL`: URL de conexión a PostgreSQL (ej: `postgresql://admin:adminpass@db:5432/cornucopia`).
        * `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_VERSION`, `AZURE_OPENAI_EMBEDDING_DEPLOYMENT`: Para los embeddings.
        * `GEMINI_API_KEY`: Para el LLM de Google Gemini (usado por ADK y/o extracción estructurada).
        * `ADK_GEMINI_MODEL_NAME`: Modelo específico de Gemini para ADK (ej: `gemini-1.5-flash-latest`).
        * `LLM_PROVIDER`: Proveedor de LLM para `crawler_rag` (ej: `GEMINI` o `AZURE_OPENAI`).
        * `AZURE_OPENAI_CHAT_DEPLOYMENT`: Si `LLM_PROVIDER` es `AZURE_OPENAI`, el nombre del despliegue de chat.
        * `INITIAL_ADMIN_USERNAME`, `INITIAL_ADMIN_PASSWORD`, etc.: Para la creación de usuarios iniciales.
        * `FRONTEND_URL`: Para la configuración CORS del backend (ej: `http://localhost:3000`).
        * `SECRET_KEY`: Clave secreta para JWT.
        * `ALGORITHM`: Algoritmo para JWT (ej: `HS256`).
        * `ACCESS_TOKEN_EXPIRE_MINUTES`: Duración del token.

3.  **Construir y levantar los contenedores Docker**:
    ```bash
    docker compose build
    docker compose up -d
    ```
    Esto construirá las imágenes (si es la primera vez o si hay cambios) y levantará los servicios: `frontend`, `backend`, `db`, y `crawler_rag`.

4.  **Carga inicial de documentos (opcional, si tienes PDFs en `crawler_rag/documents/`)**:
    El contenedor `crawler_rag` está configurado para ejecutar `scripts/insert_documents_from_folder.py` automáticamente al iniciarse. Este script procesará los PDFs que hayas colocado en subcarpetas dentro de `crawler_rag/documents/`, extraerá su texto, generará embeddings y los insertará en la base de datos.
    * Estructura esperada: `crawler_rag/documents/NOMBRE_CONVOCATORIA_1/doc1.pdf`, `crawler_rag/documents/NOMBRE_CONVOCATORIA_2/docA.pdf`, etc.

5.  **Extracción estructurada inicial (opcional)**:
    Una vez que la carga inicial de documentos (Paso 4) haya finalizado y las convocatorias básicas y sus documentos (con texto y embeddings) estén en la BD, puedes ejecutar la extracción estructurada para rellenar los campos detallados de la tabla `convocatorias`.
    * Para procesar todas las convocatorias que tengan campos pendientes (ej: `organismo = '[Extracción Pendiente]'`):
        ```bash
        make extract_pending
        ```
    * O para una convocatoria específica por su ID:
        ```bash
        make extract ID=<id_de_convocatoria>
        ```

6.  **Acceder a la aplicación**:
    * Frontend: `http://localhost:3000`
    * API Backend (Swagger UI): `http://localhost:8000/docs`

---

## Uso del panel de administración (Frontend)

1.  **Login**: Accede a `http://localhost:3000` e inicia sesión con las credenciales de administrador definidas en tu `.env`.
2.  **Ingesta de nuevas convocatorias**:
    * En el "Panel de Administración", introduce la URL de la página principal de la convocatoria y un nombre descriptivo para la misma.
    * Clica "Verificar y Descargar Archivos".
    * **Comprobación de conflictos**: El sistema verificará si ya existe una convocatoria con el mismo nombre o URL en la base de datos, o si ya existe una carpeta con ese nombre y contenido. Se te informará de cualquier conflicto.
    * **Scraping y descarga**: Si no hay conflictos bloqueantes, el sistema extraerá el texto de la página web (guardándolo como `_NOMBRE_CONVOCATORIA_web_content.txt` en la carpeta de la convocatoria) y descargará los PDFs enlazados a dicha carpeta (ubicada en `./crawler_rag/documents/NOMBRE_CONVOCATORIA/` en tu sistema host, mapeada a `/app/shared_documents_output/` en el backend).
    * **Gestión de archivos**:
        * Verás una lista de los archivos gestionados automáticamente (texto web y PDFs).
        * Puedes subir archivos adicionales (PDF, TXT, MD, DOCX) usando el formulario provisto. Los archivos se subirán a la misma carpeta de la convocatoria. *(Nota: Actualmente, la subida de archivos se realiza directamente al backend en `http://localhost:8000` para evitar problemas con Nginx en desarrollo. En un entorno de producción, Nginx debería configurarse para gestionar correctamente estas subidas).*
        * Puedes "Reiniciar Ingesta" para limpiar los campos y la selección actual y volver al formulario inicial (esto NO borra archivos del servidor).
        * Cuando estés listo, clica "Confirmar y Procesar Documentos para BD".
    * **Procesamiento para BD**: Al confirmar, el sistema leerá todos los archivos relevantes de la carpeta de la convocatoria (texto web, PDFs descargados, PDFs/documentos subidos manualmente), extraerá su texto, generará los embeddings, creará una entrada básica para la convocatoria en la tabla `convocatorias` (o la usará si ya existe por el nombre) y guardará cada documento con su texto y embedding en la tabla `documentos`.
    * **Extracción estructurada detallada**: La extracción de campos como organismo, fechas, presupuesto, etc., para la tabla `convocatorias` se realizará posteriormente mediante el script `agents/unified_extraction_agent_crono.py` (que se puede ejecutar con `make extract_pending` o mediante la tarea CRON configurada).

---

## Comandos útiles del `Makefile`

El `Makefile` proporciona atajos para operaciones comunes:

* `make help`: Muestra todos los comandos disponibles.
* **Inicialización y datos**:
    * `make init`: (Ya no tan relevante si el entrypoint de `crawler_rag` lo hace) Levanta `crawler_rag` y ejecuta `insert_documents_from_folder.py` para la carga masiva inicial.
    * `make vectoritza`: Equivalente a `make init`, para la carga masiva.
    * `make reset`: Detiene y elimina todos los contenedores, volúmenes y redes. **¡Borra todos los datos!**
    * `make reset_data`: Trunca las tablas `documentos` y `convocatorias`.
* **Extracción estructurada**:
    * `make extract ID=<id_convocatoria>`: Extrae datos para una convocatoria específica.
    * `make extract_all`: Intenta extraer datos para todas las convocatorias.
    * `make extract_pending`: (Recomendado) Extrae datos solo para las convocatorias marcadas como pendientes.
* **Backup y restauración BD**:
    * `make backup_db`: Crea un backup de la base de datos en la carpeta `backups/`.
    * `make restore_db FILE=backups/nombre_backup.sql`: Restaura la BD desde un archivo.
* **Otros**:
    * `make check_sql`: Ejecuta un script para validar la completitud de datos SQL.
    * `make set_model MODEL=GEMINI|AZURE_OPENAI|DEEPSEEK`: Cambia el proveedor LLM en `.env` (afecta principalmente a `crawler_rag`).
    * `make check_model`: Muestra el modelo LLM activo según `.env`.

*(Revisa el Makefile para ver la lista completa y actualizada de comandos).*

---

## Despliegue (visión general)

El `Makefile` incluye objetivos para construir (`make build`), etiquetar y subir (`make push`) las imágenes Docker a un Azure Container Registry (ACR), y para desplegar/actualizar los servicios en Azure Container Apps (`make deploy_backend`, `deploy_crawler`, `deploy_frontend`, `deploy_db`, `deploy_all`).

Se requiere tener Azure CLI configurado, un grupo de recursos (`RG`) y un ACR (`ACR`) definidos en `.env.deploy`.

---

## Limitaciones conocidas

* La descarga de PDFs de ciertos servidores con configuraciones SSL estrictas (ej: `aei.gob.es`) puede fallar con `requests`.
* La calidad de la extracción estructurada de datos depende de la efectividad de los prompts y la capacidad del LLM.
* La subida de archivos desde el frontend en el entorno de desarrollo local actual se realiza directamente al puerto del backend (8000) como *workaround* a problemas con Nginx y `multipart/form-data`. En producción, Nginx debería configurarse adecuadamente.

---

## Futuras mejoras

* Interfaz de usuario más avanzada para la selección y confirmación de archivos durante la ingesta.
* Soporte para extraer texto de más tipos de archivo (ej: DOC, ODT).
* Mecanismo de "actualización" o "fusión" para convocatorias existentes detectadas durante la ingesta.
* Refinar la configuración de Nginx para la subida de archivos.
* Notificaciones al administrador sobre el estado de las tareas CRON de extracción.
* Mejorar las tasks de los prompts la extracción de datos.
* Fine tunning. 

---

## Licencia

Este proyecto se distribuye bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.