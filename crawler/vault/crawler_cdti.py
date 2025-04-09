# crawler/crawler_cdti.py

import asyncio
from playwright.async_api import async_playwright
from crawler.agent_extractor import query_agent  # Importamos el archivo agent.py para consultar al agente
import requests
from datetime import datetime

# Función para navegar y extraer contenido
async def run(playwright):
    print("Iniciando navegador...")
    browser = await playwright.chromium.launch(headless=True)  # Cambiar a headless=False si quieres ver el navegador
    context = await browser.new_context(viewport={"width": 1280, "height": 800})
    page = await context.new_page()

    # Navegar a la página principal de CDTI
    print("Navegando a la página principal de CDTI...")
    await page.goto("https://www.cdti.es/")
    await page.wait_for_load_state("networkidle")

    # Cerrar el popup de cookies
    try:
        print("Cerrando el popup de cookies...")
        await page.click("text=De acuerdo", timeout=3000)
    except Exception:
        print("No se encontró el popup con el botón 'De acuerdo', continuamos...")

    # Navegar a la página deseada: "Ver Matriz"
    print("Faz clic a 'Ayudas y servicios'...")
    await page.get_by_role("link", name="Ayudas y servicios").click()
    await page.wait_for_timeout(1000)

    print("Faz clic a 'Buscadores de ayudas'...")
    await page.get_by_role("link", name="Buscadores de ayudas").first.click()
    await page.wait_for_timeout(500)

    print("Faz clic a 'Ver Matriz'...")
    await page.get_by_role('link', name='Ver Matriz').click()
    await page.wait_for_load_state("networkidle")

    print("Haciendo scroll hacia abajo...")
    # Realizar scroll para asegurarse de que los elementos carguen completamente
    await page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
    await page.wait_for_timeout(1000)

    print("Esperando a que el enlace 'Proyectos de I + D' sea visible...")
    project_link_locator = page.locator("text=Proyectos de I + D")
    await project_link_locator.wait_for(state='visible', timeout=10000)  # Espera hasta 10 segundos

    # Hacer clic en el enlace "Proyectos de I + D"
    await project_link_locator.click()

    # Extraer contenido de la página
    print("Extrayendo contenido de la página...")
    content = await page.inner_text("body")

    # Descargar el PDF asociado
    print("Descarregando el PDF asociado...")
    try:
        pdf_link_locator = await page.locator("a[href='/sites/default/files/2025-03/proyectos_de_id.pdf']")
        await pdf_link_locator.wait_for(state="visible", timeout=10000)  # Esperar hasta 10 segundos

        pdf_url = await pdf_link_locator.get_attribute('href')
        if pdf_url:
            if not pdf_url.startswith("http"):
                pdf_url = "https://www.cdti.es" + pdf_url
            r = requests.get(pdf_url)
            if r.status_code == 200:
                with open("convocatoria.pdf", "wb") as pdf_file:
                    pdf_file.write(r.content)
                print("PDF descargado correctamente.")
            else:
                print("Error al descargar el PDF:", r.status_code)
        else:
            print("No se encontró el enlace al PDF.")
    except Exception as e:
        print("Error al obtener el enlace del PDF:", e)

    # Guardar los metadatos
    metadata = {
        "url": page.url,
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tipo_documento": "html",  # Consideramos el documento HTML si no hay PDF
        "contenido_texto": content
    }
    '''
    print(f"Metadatos: {metadata}")

    # Consulta al agente para extraer la información de la página web y el PDF
    fields_to_extract = [
        {"field": "organismo", "instruction": "Buscar el organismo que ofrece la subvención."},
        {"field": "nombre", "instruction": "Buscar el nombre de la convocatoria."},
        {"field": "presupuesto_minimo", "instruction": "Buscar el presupuesto mínimo financiable."},
        # Añadir más campos según sea necesario
    ]

    results = {}
    for field in fields_to_extract:
        results[field["field"]] = await query_agent(content, field["instruction"])

    print("Resultados extraídos por el agente:", results)
    await browser.close()
    '''
# Ejecutar el script
async def main():
    async with async_playwright() as playwright:
        await run(playwright)

if __name__ == "__main__":
    asyncio.run(main())
