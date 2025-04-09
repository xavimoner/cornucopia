import asyncio
from playwright.async_api import async_playwright
import logging
from urllib.parse import urljoin

# Configuració bàsica del logging
logging.basicConfig(
    filename="crawler_cdti_ID_async.log",
    filemode="w",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Funció per obrir un enllaç en una nova pestanya basant-nos en el seu rol i accessible name
async def open_link_in_new_tab_by_role(page, role: str, name: str, exact: bool = True):
    new_tab_future = page.wait_for_event("popup")
    await page.get_by_role(role, name=name, exact=exact).click()
    new_tab = await new_tab_future
    await new_tab.wait_for_load_state("networkidle")
    return new_tab

# Funció per obtenir enllaços PDF de la pàgina
async def get_pdf_links(page) -> list:
    links = await page.eval_on_selector_all("a", "els => els.map(el => el.getAttribute('href'))")
    pdf_links = [link for link in links if link and ".pdf" in link.lower()]
    absolute_links = [urljoin(page.url, link) for link in pdf_links]
    logging.info("Found %d PDF link(s)", len(absolute_links))
    return absolute_links

# Funció per provar clics sobre diversos noms per un mateix rol
async def try_click_multiple_by_role(page, role: str, names: list, timeout: int = 7000) -> str:
    for name in names:
        try:
            locator = page.get_by_role(role, name=name, exact=True)
            await locator.wait_for(state="visible", timeout=timeout)
            await locator.click()
            return f"✅ Clicked {role} with name: {name}"
        except Exception as e:
            continue
    return f"❌ Could not click any {role} with names: {names}"

# Funció sincrònica per forçar la descàrrega d'un PDF modificant les capçaleres
def force_download_via_header_intercept(pdf_url: str = "", filename: str = "cdti_forced_download.pdf") -> str:
    from playwright.sync_api import sync_playwright
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(accept_downloads=True)
            page = context.new_page()
            context.route("**/*", lambda route, request: route.fulfill(
                status=200,
                headers={**request.headers, "Content-Disposition": "attachment"},
                body=context.request.get(request.url).body()
            ) if request.url.endswith(".pdf") else route.continue_())
            download_promise = page.wait_for_event("download")
            page.goto(pdf_url)
            download = download_promise.value
            download.save_as(filename)
            browser.close()
            return f"✅ PDF forcibly downloaded as {filename} from {pdf_url}"
    except Exception as e:
        return f"❌ Error during forced PDF download: {e}"

async def run(playwright):
    logging.info("Llançant el navegador...")
    browser = await playwright.chromium.launch(headless=False, slow_mo=300)
    context = await browser.new_context(viewport={"width": 1280, "height": 800})
    page = await context.new_page()

    # Navegar a la pàgina principal i tancar el popup de cookies
    logging.info("Navegant a https://www.cdti.es/")
    await page.goto("https://www.cdti.es/")
    await page.wait_for_load_state("networkidle")
    try:
        logging.info("Tancant el popup de cookies...")
        await page.click("text=De acuerdo", timeout=3000)
    except Exception as e:
        logging.warning("Popup de cookies no trobat: " + str(e))

    # Navegació pel menú: "Ayudas y servicios" -> "Buscadores de ayudas"
    logging.info("Clic a 'Ayudas y servicios'...")
    await page.get_by_role("link", name="Ayudas y servicios").click()
    await page.wait_for_timeout(1000)
    logging.info("Clic a 'Buscadores de ayudas'...")
    await page.get_by_role("link", name="Buscadores de ayudas").first.click()
    await page.wait_for_timeout(500)

    # Intentar clicar "Matriz de ayudas" amb fallback a "Ver Matriz"
    try:
        logging.info("Intentant clicar 'Matriz de ayudas'...")
        await page.wait_for_selector("text=Matriz de ayudas", timeout=3000)
        await page.get_by_role("link", name="Matriz de ayudas", exact=True).click()
        logging.info("'Matriz de ayudas' clicat correctament.")
    except Exception as e:
        logging.warning("No s'ha pogut clicar 'Matriz de ayudas': " + str(e))
        logging.info("Fent fallback a 'Ver Matriz'...")
        await page.evaluate("window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });")
        await asyncio.sleep(1)
        await page.get_by_role("link", name="Ver Matriz").click()
        logging.info("'Ver Matriz' clicat correctament.")

    # Un cop carregada la pàgina "Matriz de ayudas", clicar la targeta "Proyectos de I + D"
    try:
        logging.info("Clic a la targeta 'Proyectos de I + D'...")
        await page.wait_for_selector("text=Proyectos de I + D", timeout=5000)
        await page.get_by_text("Proyectos de I + D").click()
        logging.info("Targeta 'Proyectos de I + D' clicada correctament.")
    except Exception as e:
        logging.error("Error al clicar la targeta 'Proyectos de I + D': " + str(e))
        await browser.close()
        return

    # Obrir el detall (o PDF) en una nova pestanya utilitzant el codegen:
    logging.info("Obrint la vista detallada en nova pestanya...")
    new_tab = await open_link_in_new_tab_by_role(page, "link", "Proyectos de I+D", exact=True)

    # A la nova pestanya, obtenir els enllaços PDF
    pdf_links = await get_pdf_links(new_tab)
    if pdf_links:
        pdf_url = pdf_links[0]
        logging.info("Enllaç PDF trobat: " + pdf_url)
        # Forçar la descàrrega del PDF (funció sincrònica)
        download_message = force_download_via_header_intercept(pdf_url, "cdti_forced_download.pdf")
        logging.info(download_message)
    else:
        logging.warning("No s'ha trobat cap enllaç PDF a la nova pestanya.")

    await asyncio.sleep(5000)
    await browser.close()
    logging.info("Navegador tancat.")

async def main():
    async with async_playwright() as playwright:
        await run(playwright)

if __name__ == "__main__":
    asyncio.run(main())
