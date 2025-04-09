import asyncio
from playwright.async_api import async_playwright
import logging

# Configuració del logging
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

    logging.info("Navegant a https://www.cdti.es/")
    await page.goto("https://www.cdti.es/")
    await page.wait_for_load_state("networkidle")

    try:
        logging.info("Tancant el popup de cookies...")
        await page.click("text=De acuerdo", timeout=3000)
    except Exception as e:
        logging.warning("Popup de cookies no trobat: " + str(e))

    # Navegació per menú: "Ayudas y servicios" → "Buscadores de ayudas"
    logging.info("Clic a 'Ayudas y servicios'...")
    await page.get_by_role("link", name="Ayudas y servicios").click()
    await page.wait_for_timeout(1000)

    logging.info("Clic a 'Buscadores de ayudas'...")
    await page.get_by_role("link", name="Buscadores de ayudas").first.click()
    await page.wait_for_timeout(500)

    # Intentem clicar "Matriz de ayudas"
    try:
        logging.info("Intentant clicar 'Matriz de ayudas'...")
        # Esperem que aparegui el selector abans de clicar
        await page.wait_for_selector("text=Matriz de ayudas", timeout=5000)
        await page.get_by_role("link", name="Matriz de ayudas", exact=True).click()
        logging.info("'Matriz de ayudas' clicat correctament.")
    except Exception as e:
        logging.warning("No s'ha pogut clicar 'Matriz de ayudas': " + str(e))
        logging.info("Fent fallback a 'Ver Matriz'...")
        # Scroll suau per assegurar que "Ver Matriz" és visible
        await page.evaluate("window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });")
        await page.wait_for_timeout(2000)
        await page.get_by_role("link", name="Ver Matriz").click()
        logging.info("'Ver Matriz' clicat correctament.")

    # Espera per observar el resultat (pots ajustar el temps segons necessiti)
    await page.wait_for_timeout(5000)
    await browser.close()
    logging.info("Navegador tancat.")

async def main():
    async with async_playwright() as playwright:
        await run(playwright)

if __name__ == "__main__":
    asyncio.run(main())
