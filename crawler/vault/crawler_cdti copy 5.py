import asyncio
from playwright.async_api import async_playwright
import logging
import json
from datetime import datetime

# Configuració del logging
logging.basicConfig(
    filename="crawler_cdti_ID_async.log",
    filemode="w",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

async def force_download_via_header_intercept(pdf_url: str, filename: str = "convocatoria.pdf", browser_instance=None) -> str:
    """
    Força la descàrrega d'un PDF interceptant les capçaleres per obtenir el contingut real.
    """
    try:
        if browser_instance is None:
            return "No s'ha proporcionat una instància del navegador."
        context = await browser_instance.new_context(accept_downloads=True)
        page = await context.new_page()

        async def handle_route(route, request):
            if request.url.endswith(".pdf"):
                response = await page.request.get(request.url)
                body = await response.body()
                headers = dict(request.headers)
                headers["Content-Disposition"] = "attachment"
                await route.fulfill(status=200, headers=headers, body=body)
            else:
                await route.continue_()

        await context.route("**/*", handle_route)
        download_future = page.wait_for_event("download")
        await page.goto(pdf_url)
        download = await download_future
        await download.save_as(filename)
        await context.close()
        return f"✅ PDF descarregat forçadament com a {filename} des de {pdf_url}"
    except Exception as e:
        return f"❌ Error durant la descàrrega forçada del PDF: {e}"

async def run(playwright):
    logging.info("Llançant el navegador...")
    browser = await playwright.chromium.launch(headless=False, slow_mo=300)
    context = await browser.new_context(viewport={"width": 1280, "height": 800})
    page = await context.new_page()

    logging.info("Navegant a https://www.cdti.es/")
    await page.goto("https://www.cdti.es/")
    await page.wait_for_load_state("networkidle")

    try:
        logging.info("Tancant el popup de cookies...")
        await page.click("text=De acuerdo", timeout=3000)
    except Exception as e:
        logging.warning("Popup de cookies no trobat: " + str(e))

    logging.info("Clic a 'Ayudas y servicios'...")
    await page.get_by_role("link", name="Ayudas y servicios").click()
    await page.wait_for_timeout(1000)

    logging.info("Clic a 'Buscadores de ayudas'...")
    await page.get_by_role("link", name="Buscadores de ayudas").first.click()
    await page.wait_for_timeout(500)

    # Esperar i clicar "Matriz de ayudas"
    logging.info("Esperant que aparegui l'enllaç 'Matriz de ayudas'...")
    await page.wait_for_selector("text=Matriz de ayudas", timeout=10000)
    logging.info("Clic a 'Matriz de ayudas'...")
    await page.get_by_role("link", name="Matriz de ayudas", exact=True).click()
    await page.wait_for_load_state("networkidle")

    # Primer popup: clicar "Proyectos de I + D" des de la pàgina principal
    logging.info("Esperant popup per 'Proyectos de I + D'...")
    page1_future = page.wait_for_event("popup", timeout=30000)
    await page.get_by_role("link", name="Proyectos de I + D").click()
    page1 = await page1_future
    await page1.wait_for_load_state("networkidle")
    logging.info("Popup page1 carregat correctament.")

    # Segon popup: des de page1, clicar "Proyectos de I+D" (exact) i esperar el popup
    logging.info("Esperant popup des de page1 per 'Proyectos de I+D' (exact)...")
    page2_future = page1.wait_for_event("popup", timeout=30000)
    await page1.get_by_role("link", name="Proyectos de I+D", exact=True).click()
    page2 = await page2_future
    await page2.wait_for_load_state("networkidle")
    logging.info("Popup page2 carregat correctament.")

    # Extracció del contingut de page2 (convocatòria)
    logging.info("Extrayent contingut de la pàgina final (page2)...")
    content = await page2.inner_text("body")

    # Desa metadades del text web
    url_web = page2.url
    extraction_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    web_metadata = {
        "url": url_web,
        "fecha": extraction_date,
        "tipo_documento": "web",
        "contenido_texto": content
    }

    # Buscar enllaç PDF a page2
    logging.info("Cercant enllaç PDF a la pàgina final...")
    pdf_locator = page2.locator('a[href$=".pdf"]')
    count = await pdf_locator.count()
    if count > 0:
        pdf_url = await pdf_locator.first.get_attribute("href")
        logging.info("Enllaç PDF trobat: " + str(pdf_url))
        if pdf_url and not pdf_url.startswith("http"):
            pdf_url = "https://www.cdti.es" + pdf_url
        download_message = await force_download_via_header_intercept(pdf_url, "convocatoria.pdf", browser)
        logging.info(download_message)
        pdf_metadata = {
            "url": pdf_url,
            "fecha": extraction_date,
            "tipo_documento": "pdf",
            "filename": "convocatoria.pdf"
        }
    else:
        logging.error("No s'ha trobat cap enllaç PDF a la pàgina final.")
        pdf_metadata = None

    metadata = {
        "web": web_metadata,
        "pdf": pdf_metadata
    }
    
    logging.info("Metadades finals: " + str(metadata))
    print("Metadades:", metadata)

    with open("metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=4)

    await browser.close()
    logging.info("Navegador tancat.")

async def main():
    async with async_playwright() as playwright:
        await run(playwright)

if __name__ == "__main__":
    asyncio.run(main())
