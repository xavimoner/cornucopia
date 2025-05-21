# crawler_rag/crawler_cdti_ID.py
import asyncio
from playwright.async_api import async_playwright
import logging
from bs4 import BeautifulSoup
import pdfplumber
import requests
import io

# Configuració bàsica del logging
logging.basicConfig(
    filename="crawler_cdti_ID_async.log",
    filemode="w",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

async def run(playwright):
    logging.info("Llançant el navegador...")
    browser = await playwright.chromium.launch(headless=False, slow_mo=300)
    context = await browser.new_context(viewport={"width": 1280, "height": 800})
    page = await context.new_page()

    # Pas 1: Navegació a la pàgina principal i gestió del popup de cookies
    logging.info("Navegant a https://www.cdti.es/")
    await page.goto("https://www.cdti.es/", wait_until="networkidle")
    try:
        logging.info("Tancant el popup de cookies...")
        await page.click("text=De acuerdo", timeout=3000)
    except Exception as e:
        logging.warning("Popup de cookies no trobat: " + str(e))

    # Pas 2: Navegació pel menú principal
    logging.info("Clic a 'Ayudas y servicios'...")
    await page.get_by_role("link", name="Ayudas y servicios").click()
    await page.wait_for_load_state("networkidle")
    logging.info("Clic a 'Buscadores de ayudas'...")
    await page.get_by_role("link", name="Buscadores de ayudas").first.click()
    await page.wait_for_load_state("networkidle")

    # Pas 3: Intentar clicar "Matriz de ayudas" amb fallback a "Ver Matriz"
    try:
        logging.info("Intentant clicar 'Matriz de ayudas'...")
        await page.wait_for_selector("text=Matriz de ayudas", timeout=5000)
        await page.get_by_role("link", name="Matriz de ayudas", exact=True).click()
        logging.info("'Matriz de ayudas' clicat correctament.")
    except Exception as e:
        logging.warning("No s'ha pogut clicar 'Matriz de ayudas': " + str(e))
        logging.info("Fent fallback a 'Ver Matriz'...")
        await page.evaluate("window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });")
        await asyncio.sleep(1)
        await page.get_by_role("link", name="Ver Matriz").click()
        logging.info("'Ver Matriz' clicat correctament.")

    await page.wait_for_load_state("networkidle")

    # Pas 4: Clicar la targeta "Proyectos de I + D" i gestionar nova pàgina
    try:
        logging.info("Clicant targeta 'Proyectos de I + D'...")
        await page.wait_for_selector("text=Proyectos de I + D", state="visible", timeout=15000)
        await page.locator("text=Proyectos de I + D").scroll_into_view_if_needed()
        await asyncio.sleep(1)
        async with page.expect_popup() as popup_info:
            await page.click("text=Proyectos de I + D", delay=100)
            await asyncio.sleep(3)
        new_page = await popup_info.value
        await new_page.wait_for_load_state("networkidle")
        logging.info(f"Nova pàgina oberta: {new_page.url}")
        
        # Pas 4.1: Extreure tot el contingut de la pàgina web i guardar-lo
        web_html = await new_page.content()
        soup = BeautifulSoup(web_html, 'html.parser')
        web_content_text = soup.get_text(separator="\n")
        logging.info("Contingut complet de la pàgina web 'Proyectos de I + D' obtingut correctament.")
        web_lines = [line.strip() for line in web_content_text.splitlines() if line.strip()]
        logging.info("Primeres línies del contingut de la pàgina web:")
        for line in web_lines[:20]:
            logging.info(line)
        
    except Exception as e:
        logging.error(f"Error al navegar a la pàgina de projectes: {str(e)}")
        await page.screenshot(path="debug_project_page_error.png")
        raise

    # Pas 5: Clicar l'enllaç PDF a la nova pàgina
    try:
        logging.info("Buscant enllaç PDF específic 'proyectos_de_id.pdf'...")
        # Filtrar per l'enllaç que contingui "proyectos_de_id.pdf"
        pdf_selector = "a[href*='proyectos_de_id.pdf']"
        await new_page.wait_for_selector(pdf_selector, state="visible", timeout=15000)
        
        # Obtenir l'URL del PDF abans de clicar
        pdf_href = await new_page.get_attribute(pdf_selector, "href")
        if not pdf_href.startswith("http"):
            pdf_href = f"https://www.cdti.es{pdf_href}"
        logging.info(f"URL del PDF trobat: {pdf_href}")
        
        # Opció: Descarregar directament el PDF sense obrir nova pestanya
        logging.info("Descarregant PDF directament...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(pdf_href, headers=headers, stream=True)
        response.raise_for_status()
        if response.headers.get('Content-Type', '').lower() != 'application/pdf':
            raise ValueError("El contingut descarregat no és un PDF vàlid.")
        
        pdf_file = io.BytesIO(response.content)
        pdf_content_text = ""
        with pdfplumber.open(pdf_file) as pdf:
            for p in pdf.pages:
                page_text = p.extract_text() or ""
                pdf_content_text += page_text + "\n"
        
        logging.info("Contingut complet del PDF obtingut correctament.")
        pdf_lines = [line.strip() for line in pdf_content_text.splitlines() if line.strip()]
        logging.info("Primeres línies del contingut del PDF:")
        for line in pdf_lines[:10]:
            logging.info(line)
            
    except Exception as pdf_e:
        logging.error(f"Error al obrir o processar el PDF: {str(pdf_e)}")
        await new_page.screenshot(path="debug_pdf_error.png")
        raise

    
    # Inserir a la base de dades
    from crawler_rag.utils.insert_full_entry import insert_full_entry

    insert_full_entry(
        organismo="CDTI",
        nombre="Proyectos de I+D - CDTI",
        web_text=web_content_text,
        pdf_text=pdf_content_text
)



    await asyncio.sleep(3)
    await browser.close()
    logging.info("Navegador tancat.")
    
    # imprimir per consola les primeres línies
    print("--- Primeres línies de la pàgina web ---")
    for line in web_lines[:10]:
        print(line)
    print("--- Primeres línies del PDF ---")
    for line in pdf_lines[:10]:
        print(line)

async def main():
    async with async_playwright() as playwright:
        await run(playwright)

if __name__ == "__main__":
    asyncio.run(main())
