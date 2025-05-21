# Cornucopia: Agente de automatización web

Este proyecto implementa un agente inteligente con `smolagents` + `Playwright`, diseñado para navegar automáticamente por sitios web, descargar archivos PDF y extraer su contenido de forma fiable.

---

## Agente: `run_natural_agent.py`

El agente utiliza un modelo LLM (Large Language Model) para interpretar instrucciones y ejecutarlas mediante un conjunto de **herramientas** (tools) decoradas.

### Tecnologías:
- `smolagents`
- `playwright`
- `requests`
- `PyMuPDF` (para leer PDFs, también conocido como `fitz`)
- `meta-llama/Llama-3.3-70B-Instruct` (modelo LLM accedido vía HuggingFace)

---

## Estructura del proyecto

auto_crawler/    
├── agents/ 
│   ├── run_natural_agent.py  # Agente principal  
│   └── navigation_tools.py   # Todas las herramientas decoradas con @tool  
├── instructions/  
│   └── cdti_debug_task.py    # Instrucción específica (ejemplo para el CDTI)
└── navigation.log            # Registro de actividad de navegación del agente

---

## Herramientas disponibles

Estas son las herramientas registradas que el modelo puede invocar. Se definen en `navigation_tools.py` y se cargan dinámicamente si están decoradas con `@tool`.

* `go_to_url`
* `click_by_text`
* `click_by_role`
* `wait_for`
* `scroll_down`
* `element_exists`
* `hover_by_text`
* `click_menu_item`
* `try_click_multiple_texts`
* `robust_click_link`
* `screenshot_page`
* `switch_to_new_page`
* `get_pdf_links`
* `get_visible_links`
* `download_pdf_playwright`
* `download_pdf_direct` 
* `open_link_in_new_tab_by_role`
* `download_current_tab_pdf`
* `get_page_text`
* `extract_text_from_pdf`
* `hover_and_click_submenu`
* `force_download_via_header_intercept`
* `force_pdf_download_from_tab`
* `process_opened_pdf_tab`
* `extract_pdf_text_from_tab`
* `inspect_extracted_texts`
* `get_current_tab_url`
* `get_href_by_text`

*(Asegúrate de que esta lista coincida exactamente con las herramientas definidas y decoradas en `navigation_tools.py`)*

---

## Cómo ejecutarlo

1.  Asegúrate de tener instalado el entorno y las dependencias:
    ```bash
    pip install -r requirements.txt 
    # (requirements.txt debería incluir smolagents, playwright, requests, PyMuPDF)
    playwright install # Para instalar los navegadores necesarios para Playwright
    ```

2.  Ejecuta el agente:
    ```bash
    python -m agents.run_natural_agent
    ```
    *(Esto asume que `run_natural_agent.py` está dentro de una carpeta `agents` que es un paquete Python, y lo ejecutas desde el directorio `auto_crawler/`)*

---

## Añadir una nueva herramienta

1.  Define una nueva función en `navigation_tools.py` con el decorador `@tool`.
2.  Asegúrate de que la función tenga un *docstring* claro, ya que el LLM lo utiliza para entender cómo y cuándo usar la herramienta.
    ```python
    # En navigation_tools.py
    from smolagents import tool

    @tool
    def nueva_funcion(texto: str) -> str:
        """
        Descripción concisa de lo que hace esta nueva función.
        Por ejemplo: Recibe un texto y devuelve una versión procesada.
        """
        # Tu código aquí
        return f"He recibido: {texto}"
    ```
3.  No es necesario importarla manualmente en `run_natural_agent.py`; las funciones decoradas con `@tool` en `navigation_tools.py` (si el módulo se importa o se inspecciona correctamente) deberían cargarse. El script `run_natural_agent.py` ya tiene una lógica para cargar dinámicamente las herramientas del módulo `navigation_tools`:
    ```python
    # Lógica de carga de herramientas (ejemplo conceptual, tu implementación puede variar)
    # import agents.navigation_tools as tools_module
    # all_tools = [
    #     getattr(tools_module, attr)
    #     for attr in dir(tools_module)
    #     if callable(getattr(tools_module, attr)) and hasattr(getattr(tools_module, attr), "__tool_name__")
    # ]
    ```
    *(El `CodeAgent` de `smolagents` se encarga de esto si le pasas la lista de funciones herramienta directamente).*

---

## Prompt del sistema

El `custom_prompt` (definido en `run_natural_agent.py`) instruye al LLM sobre cómo debe razonar y actuar:
* Qué conjunto de herramientas puede utilizar.
* Cómo razonar paso a paso (Thought -> Code -> Observation).
* Restricciones (no escribir HTML/JS, no usar librerías no autorizadas).
* Estrategias específicas para ciertas situaciones (manejo de menús, descarga de PDFs, etc.).

---

## Notas adicionales

* El archivo `navigation.log` (si está configurado) guarda las interacciones con la web (clics, scrolls, errores, etc.) realizadas por el agente.
* El sistema está preparado para ejecutar instrucciones multi-paso y navegar por pestañas nuevas.
* Para depuración visual, puedes establecer `headless=False` en la inicialización de Playwright (ej: `playwright.chromium.launch(headless=False)`).

---

## Contacto

Para dudas, colaboraciones o mejoras, puedes contactar con el autor del proyecto o abrir un *issue* en el repositorio.

---

## Estado actual (ejemplo, adaptar según el progreso real)

* El agente puede navegar al sitio web del CDTI (según la tarea `cdti_debug_task.py`).
* Puede gestionar menús desplegables u ocultos.
* Detecta enlaces a PDFs.
* Intenta descargar PDFs, incluyendo la gestión de apertura en nuevas pestañas.
* Extrae texto de los PDFs descargados.
* Guarda el contenido HTML de las páginas y realiza capturas de pantalla para depuración.

---

## Requisitos

* Python 3.10+
* Playwright (`pip install playwright`)
* Smol Dents (`pip install smolagents`)
* Requests (`pip install requests`)
* PyMuPDF (`pip install pymupdf`)

Para inicializar Playwright (descarga de navegadores):
```bash
playwright install