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
        
        # Esperem el selector i fem scroll per assegurar visibilitat
        await page.wait_for_selector("text=Proyectos de I + D", state="visible", timeout=10000)
        await page.locator("text=Proyectos de I + D").scroll_into_view_if_needed()
        
        # Esperem el popup abans de fer clic
        async with page.expect_popup() as popup_info:
            await page.click("text=Proyectos de I + D", delay=100)
        
        # Canviem a la nova pàgina
        new_page = await popup_info.value
        await new_page.wait_for_load_state("networkidle")
        logging.info(f"Nova pàgina oberta: {new_page.url}")
        
        # Pas 4.1: Extreure i mostrar les primeres línies del contingut de la pàgina web
        web_content = await new_page.content()
        soup = BeautifulSoup(web_content, 'html.parser')
        web_text = soup.get_text()
        web_lines = web_text.splitlines()
        logging.info("Primeres línies del contingut de la pàgina web:")
        for line in web_lines[:10]:
            logging.info(line)

        # Pas 5: Clicar l'enllaç PDF a la nova pàgina
        try:
            logging.info("Buscant enllaç PDF...")
            pdf_selector = "a[href$='.pdf']"  # Selector per a enllaços que apunten a PDFs
            await new_page.wait_for_selector(pdf_selector, state="visible", timeout=10000)
            
            async with new_page.expect_popup() as pdf_popup_info:
                await new_page.click(pdf_selector)
            
            pdf_page = await pdf_popup_info.value
            await pdf_page.wait_for_load_state("networkidle")
            pdf_url = pdf_page.url
            logging.info(f"PDF obert correctament: {pdf_url}")
            
            # Pas 5.1: Descarregar el PDF i extreure'n el text
            response = requests.get(pdf_url)
            pdf_file = io.BytesIO(response.content)
            with pdfplumber.open(pdf_file) as pdf:
                pdf_text = ''
                for page in pdf.pages:
                    pdf_text += page.extract_text() + '\n'
            
            pdf_lines = pdf_text.splitlines()
            logging.info("Primeres línies del contingut del PDF:")
            for line in pdf_lines[:10]:
                logging.info(line)
            
        except Exception as pdf_e:
            logging.error(f"Error al obrir o processar el PDF: {str(pdf_e)}")
            await new_page.screenshot(path="debug_pdf_error.png")
            raise

    except Exception as e:
        logging.error(f"Error al navegar a la pàgina de projectes: {str(e)}")
        await page.screenshot(path="debug_project_page_error.png")
        raise

    # Pas final: Tancament
    await asyncio.sleep(3)
    await browser.close()
    logging.info("Navegador tancat.")

async def main():
    async with async_playwright() as playwright:
        await run(playwright)

if __name__ == "__main__":
    asyncio.run(main())