# crawler_rag/crawler_cdti_ID.py

import asyncio
from playwright.async_api import async_playwright
import logging

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
    await page.goto("https://www.cdti.es/")
    await page.wait_for_load_state("networkidle")

    try:
        logging.info("Tancant el popup de cookies...")
        await page.click("text=De acuerdo", timeout=3000)
    except Exception as e:
        logging.warning("Popup de cookies no trobat: " + str(e))

    # Pas 2: Navegació pel menú principal
    logging.info("Clic a 'Ayudas y servicios'...")
    await page.get_by_role("link", name="Ayudas y servicios").click()
    await page.wait_for_timeout(1000)

    logging.info("Clic a 'Buscadores de ayudas'...")
    await page.get_by_role("link", name="Buscadores de ayudas").first.click()
    await page.wait_for_timeout(500)

    # Pas 3: Intentar clicar "Matriz de ayudas" amb fallback a "Ver Matriz"
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

    # Pas 4: Un cop carregada la pàgina, clicar la targeta "Proyectos de I + D"
    try:
        logging.info("Esperant la targeta 'Proyectos de I + D'...")
        await page.wait_for_selector("text=Proyectos de I + D", timeout=5000)
        await page.get_by_text("Proyectos de I + D").click()
        logging.info("Targeta 'Proyectos de I + D' clicada correctament.")
    except Exception as e:
        logging.warning("No s'ha pogut clicar la targeta 'Proyectos de I + D': " + str(e))


    # Aquí tenim el problema!!!!
    # Pas revisat: Després de clicar "Ver Matriz"
    try:
        logging.info("Esperant navegació després de 'Ver Matriz'...")
        await page.wait_for_url("**/matriz-de-ayudas**", timeout=5000)  # O el patró correcte
        logging.info("Pàgina de Matriz carregada correctament")
    except Exception as e:
        logging.error(f"No s'ha carregat la pàgina de Matriz: {str(e)}")
        await page.screenshot(path="debug_matriz_page.png")
        raise

    # Pas revisat: Clicar "Proyectos de I+D" (versió robusta)
    try:
        logging.info("Clicant targeta 'Proyectos de I+D'...")
        await page.wait_for_selector("text=Proyectos de I + D", state="visible", timeout=5000)
        
        # Forçar clic si és necessari
        await page.click("text=Proyectos de I + D", delay=100, force=True)
        logging.info("Targeta clicada")
        
        # Esperar canvi de pàgina
        await page.wait_for_url("**/proyectos-de-id**", timeout=5000)  # Ajusta el patró
    except Exception as e:
        logging.error(f"Error al clicar targeta: {str(e)}")
        await page.screenshot(path="debug_targeta_fail.png")
        raise










    # Pas final: Espera per observar el resultat i tancament del navegador
    await page.wait_for_timeout(5000)
    await browser.close()
    logging.info("Navegador tancat.")

async def main():
    async with async_playwright() as playwright:
        await run(playwright)

if __name__ == "__main__":
    asyncio.run(main())
