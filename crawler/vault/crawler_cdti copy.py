# crawler/crawler_cdti.py

import asyncio
from playwright.async_api import async_playwright
from crawler.agent_extractor import query_agent  # Consulta al teu agent per extreure camps específics
import requests
from datetime import datetime

async def run(playwright):
    print("Iniciant navegador...")
    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context(viewport={"width": 1280, "height": 800})
    page = await context.new_page()

    # Navegar a la pàgina principal de CDTI
    print("Navegant a la pàgina principal de CDTI...")
    await page.goto("https://www.cdti.es/")
    await page.wait_for_load_state("networkidle")

    # Tancar el popup de cookies
    try:
        print("Tancant el popup de cookies...")
        await page.click("text=De acuerdo", timeout=3000)
    except Exception as e:
        print("No s'ha trobat el popup 'De acuerdo':", e)

    # Navegació pel menú principal amb hover i clics
    try:
        print("Obtenint el menú principal...")
        main_menu = page.get_by_label("Main navigation")
        
        print("Hover sobre 'Ayudas y servicios'...")
        ayudas = main_menu.get_by_role("link", name="Ayudas y servicios", exact=True)
        await ayudas.hover()
        await page.wait_for_timeout(3000)
        
        print("Hover sobre 'Buscadores de ayudas'...")
        buscadores = main_menu.get_by_role("link", name="Buscadores de ayudas", exact=True)
        await buscadores.hover()
        await page.wait_for_timeout(3000)
        
        print("Clic en 'Matriz de ayudas'...")
        matriz = main_menu.get_by_role("link", name="Matriz de ayudas", exact=True)
        await matriz.click()
        await page.wait_for_timeout(5000)
    except Exception as e:
        print("Error en la navegació del menú:", e)

    # Continuar la navegació: scroll i clicar l'enllaç "Proyectos de I + D"
    print("Fent scroll cap avall...")
    await page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
    await page.wait_for_timeout(1000)

    print("Esperant que el enllaç 'Proyectos de I + D' sigui visible...")
    project_link_locator = page.locator("text=Proyectos de I + D")
    await project_link_locator.wait_for(state='visible', timeout=10000)
    await project_link_locator.click()

    # Extraure el contingut de la pàgina
    print("Extrayent contingut de la pàgina...")
    content = await page.inner_text("body")

    # Descarregar el PDF associat
    print("Descarregant el PDF associat...")
    try:
        pdf_link_locator = await page.locator("a[href='/sites/default/files/2025-03/proyectos_de_id.pdf']")
        await pdf_link_locator.wait_for(state="visible", timeout=10000)
        pdf_url = await pdf_link_locator.get_attribute('href')
        if pdf_url:
            if not pdf_url.startswith("http"):
                pdf_url = "https://www.cdti.es" + pdf_url
            r = requests.get(pdf_url)
            if r.status_code == 200:
                with open("convocatoria.pdf", "wb") as pdf_file:
                    pdf_file.write(r.content)
                print("PDF descarregat correctament.")
            else:
                print("Error al descarregar el PDF:", r.status_code)
        else:
            print("No s'ha trobat l'enllaç al PDF.")
    except Exception as e:
        print("Error en obtenir l'enllaç del PDF:", e)

    # Guardar metadades
    metadata = {
        "url": page.url,
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tipo_documento": "html",  # Es considera el document HTML en absència de PDF
        "contenido_texto": content
    }
    print("Metadades:", metadata)

    # Consulta al teu agent per extreure informació específica
    fields_to_extract = [
        {"field": "organismo", "instruction": "Buscar el organismo que ofrece la subvención."},
        {"field": "nombre", "instruction": "Buscar el nombre de la convocatoria."},
        {"field": "presupuesto_minimo", "instruction": "Buscar el presupuesto mínimo financiable."},
        # Afegeix més camps si cal
    ]

    results = {}
    for field in fields_to_extract:
        results[field["field"]] = await query_agent(content, field["instruction"])

    print("Resultats extraïts pel agent:", results)
    await browser.close()

async def main():
    async with async_playwright() as playwright:
        await run(playwright)

if __name__ == "__main__":
    asyncio.run(main())
