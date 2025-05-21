# backend/ingestion_service.py
import os
import asyncio
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
import pdfplumber
from urllib.parse import urljoin, urlparse
import uuid
from sqlalchemy.orm import Session
import traceback
from typing import List, Dict, Optional 

import models 
from dotenv import load_dotenv

from openai import AzureOpenAI
import tiktoken
import requests

load_dotenv()

# --- Configuració del client Azure OpenAI ---
azure_client_for_embeddings: Optional[AzureOpenAI] = None
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_EMBEDDING_DEPLOYMENT = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")

if all([AZURE_OPENAI_API_KEY, AZURE_OPENAI_API_VERSION, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_EMBEDDING_DEPLOYMENT]):
    try:
        azure_client_for_embeddings = AzureOpenAI(
            api_key=AZURE_OPENAI_API_KEY,
            api_version=AZURE_OPENAI_API_VERSION,
            azure_endpoint=AZURE_OPENAI_ENDPOINT
        )
        print("INFO [IngestionService]: Client Azure OpenAI para embeddings inicializado.") # Espanyol
    except Exception as e:
        print(f"ERROR [IngestionService]: No se pudo inicializar el cliente Azure OpenAI: {e}")
else:
    print("WARN [IngestionService]: Faltan variables de entorno para Azure OpenAI embeddings.")

# --- Funcions utilidad ---
def split_text_if_needed(text: str, model_encoding_name: str = "cl100k_base", max_tokens: int = 8190) -> List[str]:
    if not text or not text.strip(): return []
    try: encoding = tiktoken.get_encoding(model_encoding_name)
    except Exception: 
        encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(text)
    if len(tokens) <= max_tokens: return [text]
    chunks = []; current_chunk_tokens = []; current_length = 0
    for token in tokens:
        current_chunk_tokens.append(token); current_length += 1
        if current_length >= max_tokens:
            chunks.append(encoding.decode(current_chunk_tokens)); current_chunk_tokens = []; current_length = 0
    if current_chunk_tokens: chunks.append(encoding.decode(current_chunk_tokens))
    return chunks

def get_embedding_from_azure(text_to_embed: str) -> Optional[List[float]]:
    if not azure_client_for_embeddings: print("ERROR [IngestionService]: Cliente Azure OpenAI no inicializado."); return None
    if not text_to_embed or not text_to_embed.strip(): print("WARN [IngestionService]: Texto vacío para embedding."); return None
    chunks = split_text_if_needed(text_to_embed); all_chunk_embeddings: List[List[float]] = []
    if not chunks: return None
    try:
        for i, chunk in enumerate(chunks):
            if not chunk.strip(): continue
            response = azure_client_for_embeddings.embeddings.create(input=chunk, model=str(AZURE_OPENAI_EMBEDDING_DEPLOYMENT))
            all_chunk_embeddings.append(response.data[0].embedding)
        if not all_chunk_embeddings: return None
        if len(all_chunk_embeddings) == 1: return all_chunk_embeddings[0]
        else:
            first_len = len(all_chunk_embeddings[0])
            if not all(len(emb) == first_len for emb in all_chunk_embeddings): return None 
            num_vectors = len(all_chunk_embeddings); vector_len = first_len
            avg_embedding = [sum(all_chunk_embeddings[j][i] for j in range(num_vectors)) / num_vectors for i in range(vector_len)]
            return avg_embedding
    except Exception as e: print(f"ERROR [IngestionService] en embedding: {e}"); traceback.print_exc(); return None

def extract_text_from_local_pdf(pdf_path: str) -> Optional[str]:
    full_text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            if not pdf.pages: print(f"WARN [IngestionService]: PDF {pdf_path} vacío o ilegible."); return None
            for i, page in enumerate(pdf.pages):
                text = page.extract_text();
                if text: full_text += text + "\n"
            extracted_content = full_text.strip()
            if not extracted_content: print(f"WARN [IngestionService]: No se extrajo texto de {pdf_path}."); return None
            return extracted_content
    except Exception as e: print(f"ERROR [IngestionService] extrayendo texto de PDF {pdf_path}: {e}"); traceback.print_exc(); return None

# --- ETAPA 1: Scraping i descàrrega de fitxers ---
async def scrape_and_download_initial_files( # Nom de funció actualitzat
    convocatoria_url: str, 
    nombre_convocatoria_propuesto: str 
) -> Dict:
    results_log: List[str] = [] 
    errors_log: List[str] = []  
    archivos_gestionados: List[Dict[str, str]] = [] 
    page_text_content: Optional[str] = None
    
    shared_documents_path_in_container = "/app/shared_documents_output" 
    convocatoria_folder_name = "".join(c if c.isalnum() or c in (' ') else '_' for c in nombre_convocatoria_propuesto).strip().replace(" ", "_")
    convocatoria_save_path_on_server = os.path.join(shared_documents_path_in_container, convocatoria_folder_name)
    
    # Comprovació d'existència  carpeta
    if os.path.exists(convocatoria_save_path_on_server) and os.listdir(convocatoria_save_path_on_server):
        msg = (f"CONFLICTO DE DIRECTORIO: El directorio '{convocatoria_folder_name}' para la convocatoria '{nombre_convocatoria_propuesto}' "
               f"ya existe en '{shared_documents_path_in_container}' y contiene archivos. "
               "No se volverá a descargar. Si desea procesar estos archivos o añadir nuevos, "
               "proceda con el siguiente paso. Si es una convocatoria totalmente nueva, "
               "use un nombre diferente o vacíe la carpeta '{convocatoria_folder_name}' manualmente en el servidor.")
        print(f"WARN [ScrapeService]: {msg}")
        return {
            "message": msg, "status_code_internal": 409, "conflicto_directorio": True, 
            "nombre_convocatoria_usado": nombre_convocatoria_propuesto, 
            "ruta_carpeta_servidor": convocatoria_save_path_on_server,
            "archivos_gestionados": [{"tipo": "info", "nombre_original": f"Directorio existente con {len(os.listdir(convocatoria_save_path_on_server))} archivos."}],
            "log_proceso": results_log, "errores_encontrados": [msg]
        }
    
    try:
        os.makedirs(convocatoria_save_path_on_server, exist_ok=True)
        results_log.append(f"Directorio de trabajo creado/confirmado: {convocatoria_save_path_on_server}")
    except OSError as e:
        msg = f"No se pudo crear directorio {convocatoria_save_path_on_server}: {e}"; print(f"ERROR CRITICO [ScrapeService]: {msg}"); errors_log.append(msg)
        return {"message": "Error crítico creando directorio.", "archivos_gestionados": [], "errores_encontrados": errors_log, "status_code_internal": 500, "log_proceso": results_log}

    async with async_playwright() as p:
        browser = None
        try:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(ignore_https_errors=True) 
            page = await context.new_page()
            await page.goto(convocatoria_url, wait_until="networkidle", timeout=90000)
            results_log.append(f"Acceso a URL principal: {convocatoria_url}")
            
            temp_page_text_content = await page.evaluate("() => document.body.innerText")
            page_text_content_scraped = temp_page_text_content.strip() if temp_page_text_content else None # Guardem el text per a la BD

            if page_text_content_scraped:
                results_log.append(f"Texto de la web extraído (longitud: {len(page_text_content_scraped)}).")
                web_text_filename = f"_{convocatoria_folder_name}_web_content.txt"
                web_text_filepath_on_server = os.path.join(convocatoria_save_path_on_server, web_text_filename)
                try:
                    with open(web_text_filepath_on_server, "w", encoding="utf-8") as f: f.write(page_text_content_scraped)
                    results_log.append(f"Texto web guardado como: {web_text_filename}")
                    archivos_gestionados.append({
                        "tipo": "web_content_file", "nombre_original": web_text_filename, 
                        "ruta_guardada_relativa_carpeta": web_text_filename, 
                        "url_origen": convocatoria_url
                    })
                except Exception as e_write: errors_log.append(f"No se pudo guardar texto web: {e_write}")
            else: results_log.append(f"Advertencia: No se extrajo texto de {convocatoria_url}")

            pdf_elements = await page.query_selector_all("a[href$='.pdf'], a[href$='.PDF']")
            found_pdf_urls = [urljoin(page.url, await el.get_attribute("href")) for el in pdf_elements if await el.get_attribute("href")]
            pdf_urls_on_page = sorted(list(set(found_pdf_urls)))
            results_log.append(f"Se encontraron {len(pdf_urls_on_page)} enlaces PDF.")
            
            if pdf_urls_on_page:
                http_session = requests.Session() 
                for pdf_url_loop_var in pdf_urls_on_page:
                    pdf_filename_raw = os.path.basename(urlparse(pdf_url_loop_var).path) or f"doc_{uuid.uuid4().hex[:6]}.pdf"
                    pdf_filename_cleaned = "".join(c if c.isalnum() or c in ('.', '_', '-') else '_' for c in pdf_filename_raw)
                    pdf_save_path_on_server_file = os.path.join(convocatoria_save_path_on_server, pdf_filename_cleaned)
                    try:
                        pdf_response = http_session.get(pdf_url_loop_var, stream=True, timeout=90, verify=False)
                        pdf_response.raise_for_status()
                        with open(pdf_save_path_on_server_file, 'wb') as f:
                            for chunk in pdf_response.iter_content(chunk_size=8192): f.write(chunk)
                        archivos_gestionados.append({
                            "tipo": "pdf", "nombre_original": pdf_filename_cleaned, 
                            "ruta_guardada_relativa_carpeta": pdf_filename_cleaned, 
                            "url_origen": pdf_url_loop_var
                        })
                        results_log.append(f"PDF DESCARGADO: {pdf_filename_cleaned}")
                    except Exception as e_pdf: msg = f"Error descargando PDF {pdf_url_loop_var}: {e_pdf}"; errors_log.append(msg)
        except Exception as e_scrape: msg = f"Error durante scraping: {e_scrape}"; traceback.print_exc(); errors_log.append(msg)
        finally:
            if browser and browser.is_connected(): await browser.close()

    message_parts = [f"Scraping y descarga preliminar para '{nombre_convocatoria_propuesto}' completado."]
    if page_text_content: message_parts.append("Se obtuvo el texto de la página web.")
    else: message_parts.append("No se pudo obtener el texto de la página web.")
    
    num_pdfs_descargados = len([f for f in archivos_gestionados if f["tipo"] == "pdf"])
    message_parts.append(f"Se encontraron {len(pdf_urls_on_page) if 'pdf_urls_on_page' in locals() else 0} enlaces PDF, de los cuales se descargaron {num_pdfs_descargados}.")

    status_code_internal = 200
    if errors_log: 
        message_parts.append(f"Se encontraron {len(errors_log)} errores durante el proceso.")
        status_code_internal = 207 
    
    return {
        "message": " ".join(message_parts), # Missatge resum per al frontend
        "nombre_convocatoria_usado": nombre_convocatoria_propuesto,
        "ruta_carpeta_servidor": convocatoria_save_path_on_server, 
        "archivos_gestionados": archivos_gestionados, 
        "log_proceso": results_log, # Log tècnic més detallat
        "errores_encontrados": errors_log,
        "status_code_internal": status_code_internal,
        "conflicto_directorio": False 
    }

# --- ETAPA 2: Funció processar fitxers de la carpeta i inserir a BD ---
def process_folder_files_for_db( # Canviat nom per claredat respecte a l'anterior process_downloaded_files_and_embed
    db_session: Session,
    nombre_convocatoria: str, 
    convocatoria_url_original: str, 
    ruta_carpeta_convocatoria_on_server: str # ruta completa a carpeta  convocatòria al servidor
) -> Dict:
    results_log = []
    errors_log = []
    documentos_procesados_bd = 0
    convocatoria_id_db: Optional[int] = None
    
    print(f"INFO [ProcessService]: Iniciando procesamiento de archivos en carpeta: {ruta_carpeta_convocatoria_on_server} para convocatoria '{nombre_convocatoria}'")

    if not os.path.isdir(ruta_carpeta_convocatoria_on_server):
        msg = f"El directorio '{ruta_carpeta_convocatoria_on_server}' no existe."
        print(f"ERROR [ProcessService]: {msg}"); errors_log.append(msg)
        return {"message": msg, "detalles_procesamiento_bd": results_log, "errores_procesamiento_bd": errors_log, "status_code_internal": 404}

    try:
        # 1. taula convocatorias
        db_conv = db_session.query(models.Convocatoria).filter(models.Convocatoria.nombre == nombre_convocatoria).first()
        if db_conv:
            convocatoria_id_db = db_conv.id
            results_log.append(f"Usando convocatoria existente en BD: '{nombre_convocatoria}' (ID: {convocatoria_id_db})")
            if db_conv.link_convocatoria != convocatoria_url_original: 
                db_conv.link_convocatoria = convocatoria_url_original; db_session.commit()
        else:
            new_db_conv = models.Convocatoria(nombre=nombre_convocatoria, organismo="[Extracción Pendiente]", link_convocatoria=convocatoria_url_original)
            db_session.add(new_db_conv); db_session.commit(); db_session.refresh(new_db_conv); convocatoria_id_db = new_db_conv.id
            results_log.append(f"Nueva convocatoria '{nombre_convocatoria}' creada en BD con ID: {convocatoria_id_db}.")
        if convocatoria_id_db is None: raise ValueError("ID de convocatoria no válido.")

        # 2. Llegir farxius carpeta, extreure text, generar embeddings i inserir a  foler documentos
        for filename in os.listdir(ruta_carpeta_convocatoria_on_server):
            file_path_on_server = os.path.join(ruta_carpeta_convocatoria_on_server, filename)
            if not os.path.isfile(file_path_on_server): continue # Ignora subdirectoris

            text_content: Optional[str] = None
            fuente_db = "desconocido"
            url_origen_doc = None # Intentarem obtenir si  PDF descarregat amb info prèvia

            if filename.endswith("_web_content.txt"):
                try:
                    with open(file_path_on_server, "r", encoding="utf-8") as f_txt: text_content = f_txt.read()
                    fuente_db = "web_principal"
                    url_origen_doc = convocatoria_url_original # La URL de la qual es va extreure
                except Exception as e: errors_log.append(f"Error leyendo {filename}: {e}")
            elif filename.lower().endswith(".pdf"):
                text_content = extract_text_from_local_pdf(file_path_on_server)
                fuente_db = "pdf_adjunt"
                # Per a l'URL d'origen del PDF
                
            elif filename.lower().endswith((".txt", ".md")):
                try:
                    with open(file_path_on_server, "r", encoding="utf-8") as f_txt: text_content = f_txt.read()
                    fuente_db = "fichero_texto_adjunto"
                except Exception as e: errors_log.append(f"Error leyendo {filename}: {e}")
            # TODO: pendent afegir lectors per a .doc, .docx amb python-docx 

            if text_content and text_content.strip():
                print(f"INFO [ProcessService]: Procesando embedding para: {filename}")
                embedding = get_embedding_from_azure(text_content)
                if embedding:
                    doc_titulo_db = filename if fuente_db != "web_principal" else f"Contenido web - {nombre_convocatoria}"
                    # Comprovar si ja existeix per actualitzar
                    doc_existent = db_session.query(models.Documentos).filter_by(convocatoria_id=convocatoria_id_db, titulo=doc_titulo_db, fuente=fuente_db).first()
                    if doc_existent:
                        doc_existent.texto = text_content; doc_existent.embedding = embedding
                        if url_origen_doc: doc_existent.url = url_origen_doc 
                        results_log.append(f"Documento '{doc_titulo_db}' actualizado en BD.")
                    else:
                        db_session.add(models.Documentos(convocatoria_id=convocatoria_id_db, fuente=fuente_db, url=url_origen_doc, titulo=doc_titulo_db, texto=text_content, embedding=embedding))
                        results_log.append(f"Documento '{doc_titulo_db}' insertado en BD.")
                    db_session.commit()
                    documentos_procesados_bd +=1
                else: errors_log.append(f"Fallo embedding para {filename}")
            elif text_content is None and (filename.lower().endswith(".pdf") or filename.endswith("_web_content.txt")): 
                # Si era PDF o el fitxer web i no es va poder extreure text
                errors_log.append(f"No se pudo extraer texto de {filename}.")
        
        results_log.append(f"Total de {documentos_procesados_bd} documentos insertados/actualizados en la BD desde la carpeta.")
        message = f"Procesamiento de {documentos_procesados_bd} documentos para '{nombre_convocatoria}' finalizado."
        if errors_log: message += f" Se produjeron {len(errors_log)} errores durante el procesamiento de archivos."
        
        return {"message": message, "detalles_procesamiento_bd": results_log, "errores_procesamiento_bd": errors_log, "status_code_internal": 200 if not errors_log else 207}

    except Exception as e_main_process:
        msg = f"Error crítico procesando archivos para '{nombre_convocatoria}': {e_main_process}"
        print(f"ERROR [ProcessService]: {msg}"); traceback.print_exc(); errors_log.append(msg)
        if db_session.is_active : db_session.rollback()
        return {"message": msg, "detalles_procesamiento_bd": results_log, "errores_procesamiento_bd": errors_log, "status_code_internal": 500}