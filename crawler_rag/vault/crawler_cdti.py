import asyncio
from playwright.async_api import async_playwright
import logging
import json
from datetime import datetime

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

    logging.info("Navegant a https://www.cdti.es/")
    await page.goto("https://www.cdti.es/")
    await page.wait_for_load_state("networkidle")

    try:
        logging.info("Tancant popup de cookies...")
        await page.click("text=De acuerdo", timeout=3000)
    except Exception as e:
        logging.warning("Popup de cookies no trobat: " + str(e))

    logging.info("Navegació: 'Ayudas y servicios' -> 'Buscadores de ayudas'")
    await page.get_by_role("link", name="Ayudas y servicios").click()
    await page.wait_for_timeout(1000)
    await page.get_by_role("link", name="Buscadores de ayudas").first.click()
    await page.wait_for_timeout(500)

    # Intentar clicar "Matriz de ayudas" amb timeout reduït; si falla, fallback a "Ver Matriz"
    try:
        logging.info("Intentant clicar 'Matriz de ayudas'...")
        await page.wait_for_selector("text=Matriz de ayudas", timeout=3000)
        await page.get_by_role("link", name="Matriz de ayudas", exact=True).click()
        logging.info("'Matriz de ayudas' clicat correctament.")
    except Exception as e:
        logging.warning("No s'ha pogut clicar 'Matriz de ayudas': " + str(e))
        logging.info("Fent fallback a 'Ver Matriz'...")
        await page.evaluate("window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });")
        await asyncio.sleep(1)  # Espera breu per completar el scroll
        await page.get_by_role("link", name="Ver Matriz").click()
        logging.info("'Ver Matriz' clicat correctament.")

    # Per observar el resultat
    await page.wait_for_timeout(5000)
    await browser.close()
    logging.info("Navegador tancat.")

async def main():
    async with async_playwright() as playwright:
        await run(playwright)

if __name__ == "__main__":
    asyncio.run(main())
