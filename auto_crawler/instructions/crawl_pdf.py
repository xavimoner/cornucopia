
# crawler_cdti.py

import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import requests
# from smolagents.agents import CodeAgent

# 1. NAVEGACIÓ
async def run(playwright):
    print("Iniciant navegador...")
    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context(viewport={"width": 1280, "height": 800})
    page = await context.new_page()
    
    
    # Navegar a la pàgina principal de CDTI
    print("Navegant a la pàgina principal de CDTI...")
    await page.goto("https://www.cdti.es/ayudas/proyectos-de-i-d")
    await page.wait_for_load_state("networkidle")
    browser = await playwright.chromium.launch(headless=True)

    # Clicar el link i esperar la nova pàgina que obre el PDF
    async with context.expect_page() as new_page_info:
        await page.get_by_role('link', name='Proyectos de I+D', exact=True).click()


    new_page = await new_page_info.value

    # Un cop tens la nova pàgina, pots obtenir la URL del PDF
    pdf_url = new_page.url
    print("URL del PDF:", pdf_url)

    # Descarregar el PDF amb requests
    response = requests.get(pdf_url)
    with open("document.pdf", "wb") as f:
        f.write(response.content)
    print("PDF descarregat correctament.")


    await page.wait_for_timeout(20000)


    print("Dades guardades correctament a l'Excel.")

    await browser.close()

# Funció principal per a executar el crawler
async def main():
    print("Iniciant crawler...")
    async with async_playwright() as playwright:
        await run(playwright)

if __name__ == "__main__":
    asyncio.run(main())