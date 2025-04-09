# crawler_rag/crawler_cdti_ID.py
import asyncio
from playwright.async_api import async_playwright
import logging
from bs4 import BeautifulSoup
import pdfplumber
import requests
import io
import time

# Configuració bàsica del logging
logging.basicConfig(
    filename="crawler_cdti_ID_async.log",
    filemode="w",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

async def run(playwright):
    logging.info("Llançant el navegador...")
    browser = await playwright.chromium.launch(headless=False, slow_mo=500)  # Augmentat slow_mo
    context = await browser.new_context(viewport={"width": 1280, "height": 800})
    page = await context.new_page()

    # Pas 1: Navegació a la pàgina principal i gestió del popup de cookies
    logging.info("Navegant a https://www.cdti.es/")
    await page.goto("https://www.cdti.es/", wait_until="networkidle")
    await asyncio.sleep(2)  # Espera addicional

    try:
        logging.info("Tancant el popup de cookies...")
        await page.click("text=De acuerdo", timeout=5000)  # Augmentat timeout
    except Exception as e:
        logging.warning("Popup de cookies no trobat: " + str(e))

    # Pas 2: Navegació pel menú principal
    logging.info("Clic a 'Ayudas y servicios'...")
    await page.get_by_role("link", name="Ayudas y servicios").click()
    await page.wait_for_load_state("networkidle")
    await asyncio.sleep(1)

    logging.info("Clic a 'Buscadores de ayudas'...")
    await page.get_by_role("link", name="Buscadores de ayudas").first.click()
    await page.wait_for_load_state("networkidle")
    await asyncio.sleep(1)

    # Pas 3: Intentar clicar "Matriz de ayudas" amb fallback a "Ver Matriz"
    try:
        logging.info("Intentant clicar 'Matriz de ayudas'...")
        await page.wait_for_selector("text=Matriz de ayudas", timeout=10000)  # Augmentat timeout
        await page.get_by_role("link", name="Matriz de ayudas", exact=True).click()
        logging.info("'Matriz de ayudas' clicat correctament.")
    except Exception as e:
        logging.warning("No s'ha pogut clicar 'Matriz de ayudas': " + str(e))
        logging.info("Fent fallback a 'Ver Matriz'...")
        await page.evaluate("window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });")
        await asyncio.sleep(2)  # Augmentat temps d'espera
        await page.get_by_role("link", name="Ver Matriz").click()
        logging.info("'Ver Matriz' clicat correctament.")

    await page.wait_for_load_state("networkidle")
    await asyncio.sleep(2)  # Espera addicional

    # Pas 4: Clicar la targeta "Proyectos de I + D" i gestionar nova pàgina
    try:
        logging.info("Clicant targeta 'Proyectos de I + D'...")
        
        # Esperem el selector i fem scroll per assegurar visibilitat
        await page.wait_for_selector("text=Proyectos de I + D", state="visible", timeout=15000)  # Augmentat timeout
        await page.locator("text=Proyectos de I + D").scroll_into_view_if_needed()
        await asyncio.sleep(1)
        
        # Esperem el popup abans de fer clic
        async with page.expect_popup() as popup_info:
            await page.click("text=Proyectos de I + D", delay=200)  # Augmentat delay
            await asyncio.sleep(3)  # Espera addicional després del clic
        
        # Canviem a la nova pàgina
        new_page = await popup_info.value
        await new_page.wait_for_load_state("networkidle")
        logging.info(f"Nova pàgina oberta: {new_page.url}")
        await new_page.screenshot(path="debug_new_page.png")  # Captura de pantalla per depuració
        await asyncio.sleep(2)
        
        # Pas 4.1: Extreure i mostrar les primeres línies del contingut de la pàgina web
        web_content = await new_page.content()
        soup = BeautifulSoup(web_content, 'html.parser')
        web_text = soup.get_text()
        web_lines = [line.strip() for line in web_text.splitlines() if line.strip()]
        logging.info("Primeres línies del contingut de la pàgina web:")
        for line in web_lines[:20]:  # Mostrem més línies
            logging.info(line)

        # Pas 5: Clicar l'enllaç PDF a la nova pàgina
        try:
            logging.info("Buscant enllaç PDF...")
            # Selector més específic per l'enllaç PDF
            pdf_selector = "a[href*='proyectos_de_id.pdf']"
            await new_page.wait_for_selector(pdf_selector, state="visible", timeout=15000)
            
            # Obtenim l'URL del PDF abans de clicar
            pdf_href = await new_page.get_attribute(pdf_selector, "href")
            if not pdf_href.startswith('http'):
                pdf_href = f"https://www.cdti.es{pdf_href}"
            logging.info(f"URL del PDF trobat: {pdf_href}")
            
            # Opció 1: Descarregar directament el PDF sense obrir nova pestanya
            try:
                logging.info("Descarregant PDF directament...")
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                response = requests.get(pdf_href, headers=headers, stream=True)
                response.raise_for_status()
                
                # Verifiquem que sigui un PDF vàlid
                if response.headers.get('Content-Type') != 'application/pdf':
                    raise ValueError("El contingut no és un PDF vàlid")
                
                # Guardem el PDF temporalment per verificar-lo
                with open("temp_pdf.pdf", "wb") as f:
                    f.write(response.content)
                
                # Intentem llegir el PDF
                try:
                    with pdfplumber.open("temp_pdf.pdf") as pdf:
                        first_page = pdf.pages[0]
                        pdf_text = first_page.extract_text()
                        logging.info("Contingut de la primera pàgina del PDF:")
                        logging.info(pdf_text[:500])  # Mostrem els primers 500 caràcters
                except Exception as pdf_read_error:
                    logging.error(f"Error en llegir el PDF: {str(pdf_read_error)}")
                    raise
                
            except Exception as download_error:
                logging.error(f"Error en descarregar el PDF directament: {str(download_error)}")
                
                # Opció 2: Si falla la descàrrega directa, provem obrint la pestanya
                logging.info("Provant mètode alternatiu amb pestanya...")
                async with new_page.expect_popup() as pdf_popup_info:
                    await new_page.click(pdf_selector, delay=200)
                    await asyncio.sleep(5)  # Espera llarga per a PDFs grans
                
                pdf_page = await pdf_popup_info.value
                await pdf_page.wait_for_load_state("networkidle")
                pdf_url = pdf_page.url
                logging.info(f"PDF obert en nova pestanya: {pdf_url}")
                
                # Fem scroll i esperem
                await pdf_page.evaluate("window.scrollBy(0, 300);")
                await asyncio.sleep(3)
                await pdf_page.screenshot(path="debug_pdf_page.png")
                
        except Exception as pdf_e:
            logging.error(f"Error al obrir o processar el PDF: {str(pdf_e)}")
            await new_page.screenshot(path="debug_pdf_error.png")
            raise

    except Exception as e:
        logging.error(f"Error al navegar a la pàgina de projectes: {str(e)}")
        await page.screenshot(path="debug_project_page_error.png")
        raise

    # Pas final: Tancament
    await asyncio.sleep(5)  # Espera final més llarga
    await browser.close()
    logging.info("Navegador tancat.")

async def main():
    async with async_playwright() as playwright:
        await run(playwright)

if __name__ == "__main__":
    asyncio.run(main())