# backend/structured_extraction_service.py
import os
import traceback
from sqlalchemy.orm import Session
import tiktoken
from dotenv import load_dotenv
from typing import List, Dict, Optional # AFEGIT

import models 
import requests 

load_dotenv()

# === Lògica de extraction_tasks.py ===
TASKS = {
    "organismo": """Del texto a continuación, extrae el nombre del organismo que convoca o gestiona la ayuda.
Devuelve solo el nombre, sin introducciones ni frases explicativas. Si no lo encuentras, responde 'No se menciona'.
Texto: {{TEXT}}""",
    "nombre": """Extrae el nombre completo y oficial de la convocatoria, incluyendo el año si aparece.
Devuelve solo el nombre exacto, sin frases de introducción ni explicaciones. Si no lo encuentras, responde 'No se menciona'.
Texto: {{TEXT}}""",
    "linea": """Indica si la convocatoria está incluida dentro de una línea o programa específico.
Devuelve solo el nombre del programa o 'No se menciona'.
Texto: {{TEXT}}""",
    "fecha_inicio": """Extrae la fecha exacta (formato DD/MM/AAAA) a partir de la cual se pueden presentar solicitudes.
Devuelve solo la fecha o 'No se menciona'.
Texto: {{TEXT}}""",
    "fecha_fin": """Extrae la fecha límite oficial para la presentación de solicitudes (formato DD/MM/AAAA).
Devuelve solo la fecha o 'No se menciona'.
Texto: {{TEXT}}""",
    "objetivo": """Resume el objetivo principal de la convocatoria en una o dos frases concisas.
Evita repeticiones o introducciones. Sé claro y directo. Si no es claro, responde 'No se menciona'.
Texto: {{TEXT}}""",
    "beneficiarios": """¿Quiénes pueden solicitar esta ayuda? Identifica los tipos de entidades o perfiles.
Devuelve una lista de perfiles separados por punto y coma o 'No se menciona'.
Texto: {{TEXT}}""",
    "anio": """Indica el año de publicación o aplicación principal de la convocatoria.
Devuelve solo el número (ej: 2024) o 'No se menciona'.
Texto: {{TEXT}}""",
    "area": """Indica el área temática o sector principal de la convocatoria (ej: I+D, digitalización, sostenibilidad).
Devuelve solo el nombre del área o 'No se menciona'.
Texto: {{TEXT}}""",
    "presupuesto_minimo": """Indica si existe un presupuesto mínimo exigido por proyecto.
Devuelve solo la cifra en euros (ej: 100.000 €) o 'No se especifica'.
Texto: {{TEXT}}""",
    "presupuesto_maximo": """Indica el presupuesto máximo financiable por proyecto.
Devuelve solo la cifra en euros (ej: 1.000.000 €) o 'No se especifica' o 'Sin límite'.
Texto: {{TEXT}}""",
    "duracion_minima": """Extrae la duración mínima de los proyectos si se menciona (ej: 6 meses, 1 año).
Devuelve solo el valor o 'No se menciona'.
Texto: {{TEXT}}""",
    "duracion_maxima": """Extrae la duración máxima permitida para los proyectos (ej: 24 meses, 3 años).
Devuelve solo el valor o 'No se menciona'.
Texto: {{TEXT}}""",
    "intensidad_de_subvencion": """Indica los porcentajes máximos de subvención aplicables y sus condiciones principales.
Devuelve los datos esenciales, o 'No se menciona'.
Texto: {{TEXT}}""",
    "tipo_financiacion": """Indica si la financiación es subvención, préstamo, una combinación, u otro tipo.
Devuelve solo el tipo o 'No se menciona'.
Texto: {{TEXT}}""",
    "region_de_aplicacion": """Indica el ámbito territorial de aplicación (ej: España, Cataluña, Nacional, Euskadi...).
Devuelve solo el nombre de la región o 'No se menciona'.
Texto: {{TEXT}}""",
    "costes_elegibles": """Enumera brevemente los principales costes elegibles.
Devuelve una lista separada por punto y coma o 'No se menciona'.
Texto: {{TEXT}}""",
    "dotacion_presupuestaria": """Indica la dotación total o presupuesto global asignado a la convocatoria.
Devuelve solo la cifra (ej: 10.000.000 €) o 'No se menciona'.
Texto: {{TEXT}}"""
}

# === Lògica de llm_client.py (adaptada per a extracció) ===
GEMINI_API_KEY_FOR_EXTRACTION = os.getenv("GEMINI_API_KEY") 
ADK_GEMINI_MODEL_NAME_FOR_EXTRACTION = os.getenv("ADK_GEMINI_MODEL_NAME") # No"models/"
GEMINI_API_URL_BASE_V1BETA = "https://generativelanguage.googleapis.com/v1beta/"

def ask_llm_for_extraction(prompt: str) -> str:
    if not GEMINI_API_KEY_FOR_EXTRACTION or not ADK_GEMINI_MODEL_NAME_FOR_EXTRACTION:
        print("ERROR [ExtractionService]: GEMINI_API_KEY o ADK_GEMINI_MODEL_NAME no configurades per a extracció.")
        return "[Error Configuración LLM para Extracción]"

    # nom del model per a l'API de Gemini SÍ necessita el prefix "models/"
    model_name_for_api = ADK_GEMINI_MODEL_NAME_FOR_EXTRACTION
    if not model_name_for_api.startswith("models/"):
        model_name_for_api = f"models/{ADK_GEMINI_MODEL_NAME_FOR_EXTRACTION}"
        
    # Construïm la URL completa correctament
    gemini_url_full = f"{GEMINI_API_URL_BASE_V1BETA}{model_name_for_api}:generateContent"

    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": { 
            "temperature": 0.05, # Baixa temperatura per a extracció
            "topK": 1
            # "maxOutputTokens": 256 
        }
    }
    try:
        print(f"INFO [ExtractionService]: Enviant prompt a Gemini API URL: {gemini_url_full} per extracció del camp...")
        response = requests.post(f"{gemini_url_full}?key={GEMINI_API_KEY_FOR_EXTRACTION}", headers=headers, json=payload, timeout=120)
        response.raise_for_status() # Excepció per a errors HTTP 4xx/5xx
        
        response_json = response.json()
        # print(f"DEBUG [ExtractionService]: Raw Gemini Response: {response_json}") 
        
        candidates = response_json.get("candidates")
        if candidates and isinstance(candidates, list) and len(candidates) > 0:
            content = candidates[0].get("content")
            if content and isinstance(content, dict) and "parts" in content:
                parts = content.get("parts")
                if parts and isinstance(parts, list) and len(parts) > 0:
                    text_response = parts[0].get("text")
                    if text_response:
                        return text_response.strip()
        
        print(f"WARN [ExtractionService]: Resposta inesperada o buida de Gemini: {response.text[:500]}...")
        return "[Error Gemini] Formato de respuesta inesperado"

    except requests.exceptions.Timeout:
        print(f"ERROR [ExtractionService]: Timeout cridant a Gemini API.")
        return "[Error Gemini] Timeout"
    except requests.exceptions.HTTPError as e: # Captura errors HTTP
        print(f"ERROR [ExtractionService]: HTTPError cridant a Gemini API ({e.response.status_code}): {e.response.text[:500]}")
        return f"[Error Gemini] HTTP {e.response.status_code}"
    except requests.exceptions.RequestException as e:
        print(f"ERROR [ExtractionService]: Error de xarxa cridant a Gemini API: {e}")
        return f"[Error Gemini] Red: {e}"
    except Exception as e:
        print(f"ERROR [ExtractionService]: Error inesperat cridant a Gemini: {e}")
        traceback.print_exc()
        return f"[Error Gemini] Inesperado: {str(e)}"

# === Lògica principal d'extracció ===
def get_full_text_for_extraction(db_session: Session, convocatoria_id: int) -> Optional[str]:
    print(f"INFO [ExtractionService]: Obtenint text complet per a la convocatòria ID {convocatoria_id}...")
    documentos_db = db_session.query(models.Documentos.texto).filter(models.Documentos.convocatoria_id == convocatoria_id).all()
    textos_validos = [doc.texto for doc in documentos_db if doc.texto and doc.texto.strip()]
    if not textos_validos:
        print(f"WARN [ExtractionService]: No s'ha trobat text per a la convocatòria {convocatoria_id}")
        return None
    print(f"INFO [ExtractionService]: {len(textos_validos)} fragments de documents trobats per a la convocatòria {convocatoria_id}")
    return "\n\n".join(textos_validos).strip()

def truncate_to_max_tokens(text: str, max_tokens: int, model_name_for_tiktoken: str = "gpt-4") -> str: # Usar un model comú per a tiktoken
    try:
        encoding = tiktoken.encoding_for_model(model_name_for_tiktoken)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(text)
    if len(tokens) <= max_tokens:
        return text
    truncated_tokens = tokens[:max_tokens]
    print(f"INFO [ExtractionService]: Text truncat de {len(tokens)} a {len(truncated_tokens)} tokens.")
    return encoding.decode(truncated_tokens)

def perform_structured_extraction(db_session: Session, convocatoria_id: int) -> bool:
    print(f"INFO [ExtractionService]: Iniciant extracció estructurada per a la convocatòria ID {convocatoria_id}.")
    full_text = get_full_text_for_extraction(db_session, convocatoria_id)
    if not full_text:
        print(f"WARN [ExtractionService]: Sense text per a la convocatòria {convocatoria_id}. No es pot fer l'extracció.")
        return False

    max_text_tokens_for_extraction = int(int(os.getenv("GEMINI_MAX_TOKENS", "30000")) * 0.70) # Ajustat a un valor una mica menor

    extracted_data = {}
    all_extractions_successful = True

    for field, prompt_template in TASKS.items():
        print(f"INFO [ExtractionService]: Extraient camp '{field}' per a convocatòria ID {convocatoria_id}...")
        text_for_prompt = truncate_to_max_tokens(full_text, max_text_tokens_for_extraction)
        prompt = prompt_template.replace("{{TEXT}}", text_for_prompt)
        
        response_llm = ask_llm_for_extraction(prompt)
        print(f"DEBUG [ExtractionService]: Resposta de l'LLM per al camp '{field}': '{response_llm[:100].strip()}'...")
        
        if response_llm.startswith("[Error Gemini]") or \
           "no se menciona" in response_llm.lower() or \
           "no se especifica" in response_llm.lower() or \
           "no es claro" in response_llm.lower() or \
           not response_llm.strip() or \
           len(response_llm.strip()) > 500 : # Filtre  respostes massa llargues o genèriques
            print(f"WARN [ExtractionService]: El camp '{field}' no s'ha pogut extreure de forma vàlida o no es menciona: '{response_llm[:100]}...'")
        else:
            extracted_data[field] = response_llm.strip()

    if not extracted_data:
        print(f"WARN [ExtractionService]: No s'ha extret cap dada estructurada vàlida per a la convocatòria ID {convocatoria_id}.")
        return True # èxit si no hi ha hagut errors, tot i que no s'extregui res

    try:
        convocatoria_to_update = db_session.query(models.Convocatoria).filter(models.Convocatoria.id == convocatoria_id).first()
        if not convocatoria_to_update:
            print(f"ERROR [ExtractionService]: No s'ha trobat la convocatòria amb ID {convocatoria_id} per actualitzar.")
            return False

        changes_made_count = 0
        for field, value in extracted_data.items():
            if hasattr(convocatoria_to_update, field):
                current_value_db = getattr(convocatoria_to_update, field)
                # Evitem actualitzar si el valor extret és el placeholder i ja hi ha alguna cdada a DB
                if value == "[Extracció Pendent]" and current_value_db and current_value_db != "[Extracció Pendent]":
                    continue
                if str(current_value_db or "").strip() != value.strip():
                    setattr(convocatoria_to_update, field, value)
                    changes_made_count +=1
                    print(f"INFO [ExtractionService]: Camp '{field}' actualitzat a '{value[:50]}...' per a convocatòria ID {convocatoria_id}.")
            else:
                print(f"WARN [ExtractionService]: El camp '{field}' extret no existeix al model SQLAlchemy Convocatoria.")
        
        if changes_made_count > 0:
            db_session.commit()
            print(f"INFO [ExtractionService]: {changes_made_count} camps actualitzats a la BD per a la convocatòria ID {convocatoria_id}.")
        else:
            print(f"INFO [ExtractionService]: No s'han requerit actualitzacions a la BD per a la convocatòria ID {convocatoria_id}.")
        return True
    except Exception as e:
        print(f"ERROR [ExtractionService]: Error desant dades extretes a SQL per a convocatòria ID {convocatoria_id}: {e}")
        traceback.print_exc()
        db_session.rollback()
        return False