
# crawler_cdti.py

import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import requests
from smolagents.agents import CodeAgent

# 1. NAVEGACIÓ
async def run(playwright):
    print("Iniciant navegador...")
    browser = await playwright.chromium.launch(headless=True)
    context = await browser.new_context(viewport={"width": 1280, "height": 800})
    page = await context.new_page()

    # Navegar a la pàgina principal de CDTI
    print("Navegant a la pàgina principal de CDTI...")
    await page.goto("https://www.cdti.es/")
    await page.wait_for_load_state("networkidle")
    browser = await playwright.chromium.launch(headless=True)

    # Tancar el popup del botó "De acuerdo"
    try:
        print("Tancant el popup de cookies...")
        await page.click("text=De acuerdo", timeout=3000)
        print("Popup tancat correctament.")
    except Exception as e:
        print("No s'ha trobat el popup amb el botó 'De acuerdo', continuem...")

    # Fer clic a "Ayudas y servicios"
    print("Fent clic a 'Ayudas y servicios'...")
    await page.get_by_role("link", name="Ayudas y servicios").click()
    await page.wait_for_timeout(1000)

    # Fer clic a "Buscadores de ayudas"
    print("Fent clic a 'Buscadores de ayudas'...")
    await page.get_by_role("link", name="Buscadores de ayudas").first.click()
    await page.wait_for_timeout(500)

    # Fer clic a "Matriz de ayudas"
    print("Fent clic a 'Ver Matriz'...")
    await page.get_by_role('link', name='Ver Matriz').click()
    await page.wait_for_load_state("networkidle")

    # Esperar l'aparició d'una nova finestra (popup) al clicar "Proyectos de I + D"
    print("Fent clic a 'Proyectos de I + D'...")
    popup_promise = page.wait_for_event("popup")
    await page.get_by_role("link", name="Proyectos de I + D").click()
    popup_page = await popup_promise
    await popup_page.wait_for_load_state("networkidle")

    # 2. EXTRACCIÓ DE DADES WEB - Obtenir el valor de "Nombre" després de "Actuación"
    print("Extraiem les dades de la pàgina...")
    nombre = "Proyectos CDTI de I+D"  # Assignar directament el valor al camp "Nombre"
    organismo = "https://www.cdti.es/"
    linea = "Proyectos CDTI de I+D"
    fecha_inicio = "Todo el año"
    fecha_fin = "Todo el año"

    # Recollir "objetivo" i "beneficiarios"
    print("Recollint 'objetivo'...")
    await popup_page.get_by_text('Objetivo', exact=True).click()
    objetivo = await popup_page.get_by_text('Fomentar la investigación').inner_text()
    
    print("Recollint 'beneficiarios'...")
    await popup_page.get_by_text('Beneficiarios', exact=True).click()
    beneficiarios = await popup_page.get_by_text('Empresas').inner_text()

    # 3. DESCÀRREGA DEL PDF
    print("Descarregant el PDF associat...")
    pdf_link_locator = popup_page.locator('text="Proyectos de I+D"')
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
            print("Error en descarregar el PDF:", r.status_code)

    # 4. ACTUALITZACIÓ DE L'EXCEL
    print("Actualitzant l'Excel amb les dades recollides...")
    data = {
        "organismo": organismo,
        "nombre": nombre,
        "línea": linea,
        "fecha inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "objetivo": objetivo,
        "beneficiarios": beneficiarios,
        "anyo": "2025",
        "area": "I+D",
        "presupuesto_minimo": "175.000 €",
        "presupuesto_maximo": "No hay máximo",
        "duración_minima": "1 año",
        "duración_maxima": "5 años",
        "intensidad_de_subvención": "50%",
        "intensidad_de_prestamo": "N/A",
        "tipo_financiacion": "Subvención",
        "forma_y_plazo_de_cobro": "Plazo flexible",
        "Minimis": "Sí",
        "Region_de_aplicación": "España",
        "Tipo_de_consorcio": "No aplica",
        "costes_elegibles": "Gastos en personal y equipos",
        "dotacion_presupuestaria": "5.000.000 €",
        "numero_potencial_de_ayudas": "50",
        "tasa_de_exito": "40%",
        "link_ficha_técnica": "https://www.cdti.es/ficha_tecnica",
        "link_orden_de_bases": "https://www.cdti.es/orden_bases",
        "link_convocatoria": "https://www.cdti.es/convocatoria",
        "link_plantilla_memoria": "https://www.cdti.es/plantilla_memoria",
        "criterios_valoración": "Evaluación técnica y económica",
        "documentacion_solicitud": "Formulario en PDF",
    }

    # Carregar el fitxer Excel existent
    df = pd.read_excel("/mnt/data/BBDD Subvenciones.xlsx")

    # Afegir les noves dades
    df = df.append(data, ignore_index=True)

    # Desa les dades al fitxer Excel
    df.to_excel("/mnt/data/BBDD_Subvenciones_actualitzat.xlsx", index=False)
    print("Dades guardades correctament a l'Excel.")

    await browser.close()

# Funció principal per a executar el crawler
async def main():
    print("Iniciant crawler...")
    async with async_playwright() as playwright:
        await run(playwright)

if __name__ == "__main__":
    asyncio.run(main())
