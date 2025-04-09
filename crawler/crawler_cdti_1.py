# crawler_rag/crawler_cdti_id.py
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=300)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://www.cdti.es")
    page.wait_for_load_state("networkidle")
    page.click("text=De acuerdo")

    # Hover sobre el menú principal
    main_menu = page.get_by_label("Main navigation")

    # Hover sobre "Ayudas y servicios"
    ayudas = main_menu.get_by_role("link", name="Ayudas y servicios", exact=True)
    ayudas.hover()
    page.wait_for_timeout(3000)

    # Hover sobre "Buscadores de ayudas"
    buscadores = main_menu.get_by_role("link", name="Buscadores de ayudas", exact=True)
    buscadores.hover()
    page.wait_for_timeout(3000)

    # Click a "Matriz de ayudas"
    matriz = main_menu.get_by_role("link", name="Matriz de ayudas", exact=True)
    matriz.click()


    print("Haciendo scroll hacia abajo...")
    # Realizar scroll para asegurarse de que los elementos carguen completamente
    page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
    page.wait_for_timeout(1000)

    print("Esperando a que el enlace 'Proyectos de I + D' sea visible...")
    project_link_locator = page.locator("text=Proyectos de I + D")
    project_link_locator.wait_for(state='visible', timeout=10000)  # Espera hasta 10 segundos

    page.wait_for_timeout(5000)

