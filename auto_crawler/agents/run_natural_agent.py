# agents/run_natural_agent.py

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from smolagents import CodeAgent, HfApiModel
from instructions.cdti_debug_task import task # Tasca agent

# Importar eines navegació i extracció
from agents.navigation_tools import (
    go_to_url, click_by_text, click_by_role, wait_for, scroll_down,
    element_exists, switch_to_new_page, screenshot_page,
    hover_by_text, click_menu_item, try_click_multiple_texts,
    robust_click_link, hover_and_click_submenu, sequential_hover_and_click,
    get_pdf_links, get_visible_links, get_href_by_text,
    download_pdf_playwright, open_link_in_new_tab_by_role, experimental_download_from_current_tab,
    force_download_via_header_intercept, process_opened_pdf_tab, # Eliminada repetició
    extract_text_from_pdf, extract_pdf_text_from_tab,  
    get_page_text, inspect_extracted_texts,
    get_current_tab_url
)

# --- Model llenguatge ---
# Model Hugging Face per agent
model = HfApiModel(model_id="meta-llama/Llama-3.3-70B-Instruct")

# --- Prompt sistema ---
# Instruccions agent: raonament i ús eines
custom_prompt = """
You are an expert web automation agent.
You solve tasks by reasoning step by step and using only the available tools.

You MUST ONLY use the following tools:
go_to_url, click_by_text, click_by_role, wait_for, get_pdf_links,
scroll_down, element_exists, screenshot_page, switch_to_new_page,
hover_by_text, click_menu_item, try_click_multiple_texts, 
robust_click_link, get_visible_links, download_pdf_playwright,
open_link_in_new_tab_by_role, experimental_download_from_current_tab,
force_download_via_header_intercept, get_page_text, extract_text_from_pdf,hover_and_click_submenu,
extract_pdf_text_from_tab, inspect_extracted_texts, get_current_tab_url

DO NOT import or use any other libraries (e.g., selenium, bs4, playwright.sync_api, etc.).
DO NOT write HTML, CSS, or JavaScript.
NEVER reimplement logic manually — use the tools available to you.

▸ If a dropdown menu is not directly clickable, use `hover_by_text` or `click_menu_item`.

▸ If elements vary across websites (e.g., "Ayudas", "Subvenciones", "Servicios"), try `try_click_multiple_texts`.

▸ If `get_pdf_links()` returns no results, try `get_visible_links()` to inspect possible fallback text-based downloads.

▸ If the PDF is expected to open in a new tab (e.g. 'Proyectos de I+D'), use:
   `open_link_in_new_tab_by_role(...)` — this also switches context automatically.
   Then immediately call `experimental_download_from_current_tab(...)`.

▸ If that fails, use `get_current_tab_url()` and pass it to 
   `force_download_via_header_intercept(...)` to forcibly download the PDF.

▸ If the PDF still cannot be downloaded, and it's rendered in the browser tab, use 
   `extract_pdf_text_from_tab()` to capture its content.

▸ Only use `download_pdf_playwright(...)` as a fallback if opening in a new tab fails.

▸ To ensure you're on the correct page, optionally take a screenshot or call 
   `get_page_text()` just after opening the tab.

▸ Do not attempt to match full URLs as visible text — only use them in direct download calls.

▸ If download fails, take a screenshot and continue to the next step.

▸ After extracting the webpage text and the PDF text, call `inspect_extracted_texts()` 
   to review and compare both contents.

Always follow this format:

Thought: describe what you're trying to do  
Code:
```py
# your code here using ONLY the tools
```<end_code>

Observation: result of the tool call

Now begin.
"""

# --- Inicialització agent ---
agent = CodeAgent(
    tools=[ # Eines disponibles agent
        go_to_url, click_by_text, click_by_role, wait_for, scroll_down,
        element_exists, switch_to_new_page, screenshot_page,
        hover_by_text, click_menu_item, try_click_multiple_texts, robust_click_link, 
        get_pdf_links, get_visible_links, get_href_by_text,
        download_pdf_playwright, force_download_via_header_intercept,
        open_link_in_new_tab_by_role, experimental_download_from_current_tab,hover_and_click_submenu,
        force_pdf_download_from_tab, process_opened_pdf_tab,
        extract_text_from_pdf, extract_pdf_text_from_tab,
        get_page_text, inspect_extracted_texts,
        get_current_tab_url
    ],
    model=model, # Model LLM
    prompt_templates={ # Plantilles prompt agent
        "system_prompt": custom_prompt,
        "final_answer": { # Missatges interns llibreria, mantenir anglès
            "pre_messages": "Task complete. Summary below:",
            "post_messages": "End of task."
        }
    },
    verbosity_level=2, # Nivell detall logs agent
    additional_authorized_imports=[ # Importacions permeses codi generat
        "playwright.sync_api",
        "requests",
        "urllib.parse",
        "time"
    ]
)

# --- Execució ---
if __name__ == "__main__":
    result = agent.run(task) # Executar agent amb tasca
    print("\nResultado final:") # Missatge terminal
    print(result)

    # Comprovar i extreure text PDF descarregat
    if "cdti_proyectos.pdf" in os.listdir(): # Nom fitxer fixat
        print("PDF descargado. Intentando extraer texto...") # Missatge terminal
        extract_text_from_pdf("cdti_proyectos.pdf") 

    if "pdf_text.txt" in os.listdir(): # Comprovar creació fitxer text PDF
        print("Texto del PDF extraído correctamente.") # Missatge terminal
    else:
        print("Advertencia: Texto del PDF no extraído.") # Missatge terminal