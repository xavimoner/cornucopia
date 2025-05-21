# instructions/cdti.py

"""
Instruccions per a navegar a la web del CDTI i descarregar el PDF de "Proyectos de I + D".
Aquest fitxer fa ús dels agents definits a auto_crawler/agents/navigation_tools.py.
"""

from agents.navigation_tools import (
    go_to_url,
    click_by_text,
    click_by_role,
    wait_for,
    get_pdf_links,
    download_pdf,
)

def execute_cdti_navigation():
    results = []

    # 1. Anar a la pàgina principal
    results.append(go_to_url("https://www.cdti.es/"))

    # 2. Acceptar les cookies (si apareixen)
    try:
        results.append(click_by_text("De acuerdo"))
    except Exception as e:
        results.append(f"Cookie popup not found: {str(e)}")

    # 3. Entrar a "Ayudas y servicios"
    results.append(click_by_role("link", "Ayudas y servicios"))
    results.append(wait_for(1000))

    # 4. Entrar a "Buscadores de ayudas"
    results.append(click_by_role("link", "Buscadores de ayudas"))
    results.append(wait_for(1000))

    # 5. Fer clic a "Ver Matriz"
    results.append(click_by_role("link", "Ver Matriz"))
    results.append(wait_for(1000))

    # 6. Fer clic a "Proyectos de I + D"
    results.append(click_by_role("link", "Proyectos de I + D"))
    results.append(wait_for(1500))

    # 7. Obtenir enllaços a PDFs i filtrar el correcte
    pdfs = get_pdf_links()
    filtered = [url for url in pdfs if "Proyectos" in url]

    if filtered:
        results.append(download_pdf(filtered[0], "cdti_proyectos.pdf"))
    else:
        results.append("No PDF found with 'Proyectos' in URL.")

    return results
