# agents/navivgation_tools.py

import os
os.environ["PWDEBUG"] = "1"
from smolagents import tool
from playwright.sync_api import sync_playwright, Page
from urllib.parse import urljoin
import requests
import logging
import re



# ────────────────────────────────────────────────────────────────────────────────
# Configuració de logging
# ────────────────────────────────────────────────────────────────────────────────
logging.basicConfig(
    filename="navigation.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ────────────────────────────────────────────────────────────────────────────────
# Inicialització del navegador
# ────────────────────────────────────────────────────────────────────────────────
playwright = sync_playwright().start()
browser = playwright.chromium.launch(headless=False)
context = browser.new_context()
page: Page = context.new_page()


# ────────────────────────────────────────────────────────────────────────────────
# Navegació i clics
# ────────────────────────────────────────────────────────────────────────────────

@tool
def go_to_url(url: str) -> str:
    """
    Navigates to the specified URL and waits for the page to fully load.
    
    Args:
        url: The URL to navigate to.

    Returns:
        A confirmation message indicating the navigation was successful.
    """
    page.goto(url)
    page.wait_for_load_state("networkidle")
    msg = f"Navigated to {url}"
    logging.info(msg)
    return msg


@tool
def click_by_text(text: str, timeout: int = 10000) -> str:
    """
    Clicks the first element matching the provided visible text.
    
    Args:
        text: Visible text of the element to click.
        timeout: Timeout in milliseconds.

    Returns:
        Result of the click operation.
    """
    try:
        locator = page.locator(f"text={text}").first
        locator.wait_for(state="attached", timeout=timeout)
        page.evaluate("(e) => e.scrollIntoView({behavior: 'smooth', block: 'center'})", locator.element_handle())
        locator.wait_for(state="visible", timeout=timeout)
        locator.click()
        msg = f"Clicked element with text: {text}"
        logging.info(msg)
        return msg
    except Exception as e:
        msg = f"Error clicking on element with text '{text}': {str(e)}"
        logging.error(msg)
        return msg


@tool
def click_by_role(role: str, name: str) -> str:
    """
    Clicks an element by ARIA role and accessible name.

    Args:
        role: ARIA role (e.g. 'link', 'button').
        name: Accessible name of the element.

    Returns:
        Confirmation message.
    """
    locator = page.get_by_role(role=role, name=name, exact=exact)
    locator.click()
    return f"Clicked {role} with name '{name}'"


@tool
def wait_for(milliseconds: int) -> str:
    """
    Waits for a specified number of milliseconds.

    Args:
        milliseconds: Time to wait.

    Returns:
        Confirmation message.
    """
    page.wait_for_timeout(milliseconds)
    msg = f"Waited {milliseconds}ms"
    logging.info(msg)
    return msg


@tool
def scroll_down(pixels: int = 1000) -> str:
    """
    Scrolls down the page by the specified number of pixels.

    Args:
        pixels: Number of pixels to scroll down.

    Returns:
        Confirmation message.
    """
    page.evaluate(f"window.scrollBy(0, {pixels})")
    msg = f"Scrolled down {pixels} pixels"
    logging.info(msg)
    return msg


@tool
def element_exists(text: str) -> str:
    """
    Checks if an element with the given text exists on the page.

    Args:
        text: Text to search for.

    Returns:
        Message indicating whether the element exists.
    """
    element = page.locator(f"text={text}")
    exists = element.count() > 0
    msg = f"Element with text '{text}' exists: {exists}"
    logging.info(msg)
    return msg


@tool
def screenshot_page(filename: str = "screenshot.png") -> str:
    """
    Takes a screenshot of the current page.

    Args:
        filename: Name of the file to save the screenshot.

    Returns:
        Confirmation message.
    """
    page.screenshot(path=filename, full_page=True)
    msg = f"Screenshot saved as {filename}"
    logging.info(msg)
    return msg


@tool
def switch_to_new_page() -> str:
    """
    Switches to the most recently opened page or popup.

    Returns:
        Message indicating the result.
    """
    global page
    pages = context.pages
    if len(pages) > 1:
        page = pages[-1]
        msg = f"Switched to new page: {page.url}"
        logging.info(msg)
        return msg
    else:
        msg = "No new popup page detected."
        logging.warning(msg)
        return msg


@tool
def get_current_page() -> Page:
    """
    Returns the current active Playwright page object.
    """
    global page
    return page

# ────────────────────────────────────────────────────────────────────────────────
# Interacció amb menús i clics robustos
# ────────────────────────────────────────────────────────────────────────────────
@tool
def sequential_hover_and_click(label: str, path: list[str], wait: int = 1000) -> str:
    """
    Sequentially hovers over a menu and submenu and clicks the final target item.

    Args:
        label: ARIA label of the parent menu container (e.g., "Main navigation")
        path: List of link names to hover through. The last one will be clicked.
        wait: Milliseconds to wait between hover actions.

    Returns:
        A success or failure message.
    """
    try:
        container = page.get_by_label(label)
        for link_name in path[:-1]:
            container.get_by_role("link", name=link_name, exact=True).hover()
            page.wait_for_timeout(wait)
        container.get_by_role("link", name=path[-1], exact=True).click()
        return f"Hovered through {path[:-1]} and clicked '{path[-1]}'"
    except Exception as e:
        return f"Error in sequential_hover_and_click({path}): {e}"




@tool
def hover_by_text(text: str) -> str:
    """
    Hovers over an element by its visible text.

    Args:
        text: Text of the element.

    Returns:
        Confirmation message.
    """
    element = page.locator(f"text={text}")
    element.hover()
    return f"Hovered over element with text: {text}"


@tool
def click_menu_item(menu_text: str, submenu_text: str, timeout: int = 10000) -> str:
    """
    Clicks a submenu item by hovering over a parent menu.

    Args:
        menu_text: Main menu text.
        submenu_text: Submenu item text.
        timeout: Wait timeout.

    Returns:
        Confirmation message.
    """
    try:
        menu = page.locator(f"text={menu_text}").first
        menu.wait_for(state="visible", timeout=timeout)
        menu.hover()
        submenu = page.locator(f"text={submenu_text}").first
        submenu.wait_for(state="visible", timeout=timeout)
        submenu.click()
        msg = f"Clicked submenu item '{submenu_text}' under menu '{menu_text}'"
        logging.info(msg)
        return msg
    except Exception as e:
        msg = f"Failed to click submenu '{submenu_text}' under '{menu_text}': {str(e)}"
        logging.error(msg)
        return msg


@tool
def try_click_multiple_texts(texts: list[str], timeout: int = 5000) -> str:
    """
    Tries clicking elements by multiple alternative visible texts.

    Args:
        texts: List of possible texts.
        timeout: Timeout per attempt.

    Returns:
        Result of the first successful click or a warning message.
    """
    for text in texts:
        try:
            locator = page.locator(f"text={text}").first
            locator.wait_for(state="visible", timeout=timeout)
            locator.click()
            msg = f"Clicked element with text: {text}"
            logging.info(msg)
            return msg
        except:
            continue
    msg = f"Could not click any of the provided texts: {texts}"
    logging.warning(msg)
    return msg


@tool
def robust_click_link(name: str, timeout: int = 10000) -> str:
    """
    Attempts to click a link using multiple strategies.

    Args:
        name: Visible text or label of the link.
        timeout: Timeout value.

    Returns:
        Result of the most successful strategy.
    """
    try:
        result = click_by_role("link", name)
        return f"(role) {result}"
    except Exception as role_error:
        logging.warning(f"click_by_role failed for '{name}': {str(role_error)}")
    try:
        result = click_by_text(name, timeout=timeout)
        return f"(text) {result}"
    except Exception as text_error:
        logging.error(f"click_by_text also failed for '{name}': {str(text_error)}")
        return f"Failed to click link '{name}' using both strategies."

@tool
def try_click_multiple_by_role(role: str, names: list[str], timeout: int = 7000) -> str:
    """
    Tries to click an element by ARIA role and a list of possible names.

    Args:
        role: ARIA role (e.g., 'link', 'button', etc.).
        names: List of possible accessible names.
        timeout: Time to wait for each element in milliseconds.

    Returns:
        A message indicating success or failure.
    """
    from agents.navigation_tools import page  # assegura't que 'page' sigui accessible

    for name in names:
        try:
            locator = page.get_by_role(role=role, name=name, exact=True)
            locator.wait_for(state="visible", timeout=timeout)
            locator.click()
            return f"Clicked {role} with name: {name}"
        except Exception as e:
            continue
    return f"Could not click any {role} with names: {names}"

@tool
def hover_and_click_submenu(menu_text: str, submenu_text: str, timeout: int = 10000) -> str:
    """
    Hovers over a parent menu item and clicks a submenu item.

    Args:
        menu_text: The visible text of the parent menu (e.g., 'Ayudas y servicios').
        submenu_text: The visible text of the submenu to click (e.g., 'Buscadores de ayudas').
        timeout: Maximum time in milliseconds to wait for the elements.

    Returns:
        A confirmation message indicating success or failure.
    """
    try:
        menu = page.locator(f"text={menu_text}").first
        menu.wait_for(state="visible", timeout=timeout)
        menu.hover()
        submenu = page.locator(f"text={submenu_text}").first
        submenu.wait_for(state="visible", timeout=timeout)
        submenu.click()
        msg = f"Clicked submenu item '{submenu_text}' under menu '{menu_text}'"
        logging.info(msg)
        return msg
    except Exception as e:
        msg = f"Failed to click submenu '{submenu_text}' under '{menu_text}': {str(e)}"
        logging.error(msg)
        return msg


# ────────────────────────────────────────────────────────────────────────────────
# PDF Tools
# ────────────────────────────────────────────────────────────────────────────────

@tool
def get_pdf_links() -> list:
    """
    Returns a list of PDF URLs found in anchor elements on the page.

    Returns:
        A list of full PDF links.
    """
    links = page.eval_on_selector_all("a", "els => els.map(el => el.getAttribute('href'))")
    pdf_links = [link for link in links if link and ".pdf" in link.lower()]
    absolute_links = [urljoin(page.url, link) for link in pdf_links]
    logging.info("Found %d PDF link(s)", len(absolute_links))
    return absolute_links


@tool
def force_download_via_header_intercept(pdf_url: str = "", filename: str = "cdti_forced_download.pdf") -> str:
    """
    Forces a PDF to download by launching a new Playwright context with a route that modifies headers.

    Args:
        pdf_url: Full URL to the PDF.
        filename: Filename to save.

    Returns:
        Success/failure message.
    """
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
            return f"PDF forcibly downloaded as {filename} from {pdf_url}"
    except Exception as e:
        return f"Error during forced PDF download: {e}"


@tool
def get_visible_links() -> list:
    """
    Returns a list of visible link texts on the page.

    Returns:
        List of link texts.
    """
    elements = page.locator("a:visible")
    texts = elements.all_inner_texts()
    return texts


@tool
def extract_text_from_pdf(filename: str = "cdti_proyectos.pdf") -> str:
    """
    Extracts text from a downloaded PDF and saves it to pdf_text.txt.

    Args:
        filename: Name of the PDF file.

    Returns:
        Status message.
    """
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(filename)
        text = "\n".join(page.get_text() for page in doc)
        with open("pdf_text.txt", "w", encoding="utf-8") as f:
            f.write(text)
        return f"Text extracted from {filename}"
    except Exception as e:
        return f"Failed to extract text from PDF: {e}"


@tool
def open_link_in_new_tab_by_role(name: str) -> str:
    """
    Clicks a link by its ARIA role and name, and waits for the new tab to load.

    Args:
        name (str): The visible name of the link (e.g., 'Proyectos de I+D')

    Returns:
        str: Message confirming the new tab URL or error if it failed.
    """
    try:
        global page
        # Espera la nova pestanya *abans* de clicar
        with context.expect_page() as new_page_info:
            page.get_by_role('link', name=name, exact=True).click()
        page = new_page_info.value
        page.wait_for_load_state("networkidle")
        msg = f"Opened new tab with URL: {page.url}"
        logging.info(msg)
        return msg
    except Exception as e:
        msg = f"Failed to open new tab for link '{name}': {str(e)}"
        logging.error(msg)
        return msg




@tool
def get_href_by_text(link_text: str) -> str:
    """
    Gets the href of the first visible anchor with the given text.

    Args:
        link_text: Visible link text.

    Returns:
        The href URL or an error message.
    """
    try:
        locator = page.locator(f'a:visible', has_text=link_text).first
        href = locator.get_attribute("href")
        if href:
            logging.info(f"Found href for '{link_text}': {href}")
            return href
        else:
            return f"No href found for link with text: {link_text}"
    except Exception as e:
        return f"Error retrieving href: {str(e)}"



@tool
def force_pdf_download_from_tab(pdf_url: str = "", filename: str = "forced_cdti_download.pdf") -> str:
    """
    Forces download of a PDF opened in a browser tab by intercepting the request and changing headers.

    Args:
        pdf_url: The full URL of the PDF currently opened in the browser tab.
        filename: The desired filename to save the downloaded PDF as.

    Returns:
        A message confirming the PDF was downloaded, or an error message if it failed.
    """
    from playwright.sync_api import sync_playwright
    import time

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(accept_downloads=True)
            page = context.new_page()

            def intercept_pdf(route, request):
                if request.url.endswith(".pdf"):
                    response = context.request.get(request.url)
                    route.fulfill(
                        status=response.status,
                        headers={**response.headers, "Content-Disposition": "attachment"},
                        body=response.body()
                    )
                else:
                    route.continue_()

            page.route("**/*", intercept_pdf)

            page.goto(pdf_url)

            download_path = None

            def handle_download(download):
                nonlocal download_path
                download_path = download.path()
                download.save_as(filename)

            page.on("download", handle_download)

            page.wait_for_timeout(7000)
            browser.close()

            return f"PDF downloaded with forced headers as '{filename}'." if download_path else "❌ Failed to download PDF with forced route."

    except Exception as e:
        return f"Exception during forced PDF download: {e}"

@tool
def download_pdf_playwright(link_text: str, filename: str = "downloaded.pdf") -> str:
    """
    Tries to click a visible link by text and waits for the PDF download using Playwright's download manager.

    Args:
        link_text: Visible text of the link to click.
        filename: Name of the file to save the PDF as.

    Returns:
        Status message.
    """
    try:
        with page.expect_download() as download_info:
            page.locator(f'a:visible', has_text=link_text).first.click()
        download = download_info.value
        download.save_as(filename)
        logging.info(f"PDF downloaded as '{filename}' via Playwright.")
        return f"PDF downloaded as '{filename}' via Playwright."
    except Exception as e:
        msg = f"Failed to download PDF using Playwright: {e}"
        logging.error(msg)
        return msg



# ────────────────────────────────────────────────────────────────────────────────
# Copiar webs, documents i pdf
# ────────────────────────────────────────────────────────────────────────────────

@tool
def get_page_text() -> str:
    """
    Extracts the full visible text from the current webpage and saves it to 'webpage_text.txt'.

    Returns:
        A confirmation message.
    """
    try:
        text = page.inner_text("body")  # extreu només el text visible
        with open("webpage_text.txt", "w", encoding="utf-8") as f:
            f.write(text)
        logging.info("Saved visible page text as 'webpage_text.txt'")
        return "Saved visible page text."
    except Exception as e:
        logging.error(f"Failed to extract visible text: {e}")
        return f"Error extracting text: {e}"


@tool
def process_opened_pdf_tab(pdf_url: str, filename: str = "cdti_proyectos.pdf") -> str:
    """
    Handles opened PDF in a new tab: downloads it if possible, or extracts text directly if not.

    Args:
        pdf_url: URL of the opened PDF tab.
        filename: Desired name to save the downloaded PDF file.

    Returns:
        Status message about what was successfully done.
    """
    import requests
    import fitz  # PyMuPDF
    import os

    try:
        # Try to download PDF
        r = requests.get(pdf_url)
        if r.ok and b'%PDF' in r.content[:1024]:
            with open(filename, 'wb') as f:
                f.write(r.content)
            # Try to extract text from downloaded PDF
            try:
                doc = fitz.open(filename)
                text = "\n".join(page.get_text() for page in doc)
                with open("pdf_text.txt", "w", encoding="utf-8") as f:
                    f.write(text)
                return f"PDF downloaded and text extracted from {filename}"
            except Exception as e:
                return f"PDF downloaded but failed to extract text: {e}"
        else:
            return "PDF could not be downloaded or is invalid."
    except Exception as e:
        return f"Failed to fetch or process PDF from tab: {e}"

@tool
def get_current_tab_url() -> str:
    """
    Returns the current tab's URL. Useful to retrieve PDF URL before processing it.
    """
    return page.url


@tool
def extract_pdf_text_from_tab() -> str:
    """
    Extracts visible text from a PDF opened in the current browser tab and returns it as plain text.
    Assumes the PDF is rendered using the browser's PDF viewer (e.g., Chrome, Firefox).
    
    Returns:
        Extracted text content as a string.
    """
    page: Page = get_current_page()
    return page.content()


@tool
def inspect_extracted_texts() -> str:
    """
    Mostra un resum del text extret del PDF i de la pàgina web, incloent comprovacions bàsiques.

    Retorna:
        Un missatge amb el resultat de la inspecció.
    """
    result = []
    
    # PDF LOCAL
    try:
        with open("pdf_text.txt", "r", encoding="utf-8") as f:
            pdf_text = f.read()
        result.append("PDF TEXT (pdf_text.txt):")
        result.append(pdf_text[:1000] + "\n...")  # primeres línies
        if "CDTI" in pdf_text or "Proyectos de I+D" in pdf_text:
            result.append("El contingut del PDF sembla correcte.\n")
        elif "robots" in pdf_text or "Incapsula" in pdf_text:
            result.append("Contingut web o bloqueig detectat al PDF.\n")
        else:
            result.append("El PDF s'ha descarregat però pot no ser vàlid.\n")
    except FileNotFoundError:
        result.append("No s'ha trobat pdf_text.txt.")
    
    # TEXT DE LA WEB
    try:
        with open("webpage_text.txt", "r", encoding="utf-8") as f:
            web_text = f.read()
        result.append("🌐 WEB TEXT (webpage_text.txt):")
        result.append(web_text[:1000] + "\n...")  # primeres línies
        if "Proyectos de I + D" in web_text or "Ficha del instrumento" in web_text:
            result.append("El text de la pàgina web sembla correcte.\n")
        else:
            result.append("No s'ha trobat informació rellevant a la pàgina web.\n")
    except FileNotFoundError:
        result.append("No s'ha trobat webpage_text.txt.")

    return "\n".join(result)

@tool
def experimental_download_from_current_tab(filename: str = "downloaded_pdf.pdf") -> str:
    """
    Tries to download content from the current tab using its URL (PDF or other).
    This is useful if the PDF is rendered in-browser but the URL is accessible.

    Args:
        filename: The name to save the downloaded file as.

    Returns:
        A message indicating success or failure.
    """
    import requests
    from agents.navigation_tools import get_current_tab_url

    try:
        url = get_current_tab_url()
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; ExperimentalBot/1.0)"
        }
        response = requests.get(url, headers=headers)
        if response.ok and b"%PDF" in response.content[:1024]:
            with open(filename, "wb") as f:
                f.write(response.content)
            return f"File downloaded from {url} and saved as {filename}"
        else:
            return f"The content at {url} doesn't appear to be a valid PDF."
    except Exception as e:
        return f"Download failed from current tab: {e}"
