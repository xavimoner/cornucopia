# crawler_rag/agents/unified_extraction_agent_crono.py
import os
import sys
import psycopg2
import tiktoken
from dotenv import load_dotenv
import argparse # arguments de línia de comandes
from datetime import datetime #  x logging
import traceback # logs d'error 
from typing import List, Dict, Optional


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from extraction_tasks import TASKS
    from llm_client import ask_llm, get_model_info # Utilitzem la funció genèrica ask_llm
except ImportError as e:
    print(f"ERROR CRÍTIC [UEA_CRONO]: No s'han pogut importar mòduls necessaris des de 'agents': {e}")
    print(f"           sys.path actual: {sys.path}")
    print(f"           Directori actual: {os.getcwd()}")
    sys.exit(1)

# Carrega variables d'entorn .env a arrel del projecte (/app/.env)
dotenv_path = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path=dotenv_path)
    # print(f"INFO [UEA_CRONO]: Variables d'entorn carregades des de {dotenv_path}")
else:
    print(f"WARN [UEA_CRONO]: El fitxer .env no s'ha trobat a {dotenv_path}. S'utilitzaran les variables d'entorn del sistema si existeixen.")

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("ERROR CRÍTIC [UEA_CRONO]: La variable d'entorn DATABASE_URL no està configurada.")
    sys.exit(1)

LOG_DIR = "logs" # Relatiu a /app
os.makedirs(os.path.join(os.path.dirname(__file__), '..', LOG_DIR), exist_ok=True) # Assegura que /app/logs existeixi
LOG_FILE_UEA = os.path.join(os.path.dirname(__file__), '..', LOG_DIR, "unified_extraction_agent_crono.log")


def log(msg_type: str, msg: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_msg = f"[{timestamp}] [{msg_type.upper()}] [UEA_CRONO] {msg}"
    print(full_msg)
    try:
        with open(LOG_FILE_UEA, "a", encoding="utf-8") as f:
            f.write(full_msg + "\n")
    except Exception as e:
        print(f"ERROR [UEA_CRONO]: No s'ha pogut escriure al log {LOG_FILE_UEA}: {e}")

def get_full_text(convocatoria_id: int) -> Optional[str]:
    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute("SELECT texto FROM documentos WHERE convocatoria_id = %s", (convocatoria_id,))
        textos = [row[0] for row in cursor.fetchall() if row[0] and row[0].strip()]
        if not textos:
            log("warn", f"No s'ha trobat text vàlid per a la convocatòria ID {convocatoria_id}")
            return None
        log("info", f"{len(textos)} documents de text trobats per a la convocatòria ID {convocatoria_id}")
        return "\n\n".join(textos).strip()
    except psycopg2.Error as e:
        log("error", f"Error de base de dades a get_full_text per ID {convocatoria_id}: {e}")
        return None
    except Exception as e:
        log("error", f"Error inesperat a get_full_text per ID {convocatoria_id}: {e}")
        traceback.print_exc()
        return None
    finally:
        if conn:
            conn.close()

def truncate_to_max_tokens(text: str, max_tokens: int, model_name_for_tiktoken: str = "gemini-pro") -> str: # Model per a tiktoken, troceja
    try:
        encoding = tiktoken.encoding_for_model(model_name_for_tiktoken)
    except KeyError:
        log("warn", f"Encoding per a '{model_name_for_tiktoken}' no trobat, utilitzant 'cl100k_base'.")
        encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(text)
    if len(tokens) <= max_tokens:
        return text
    truncated_tokens = tokens[:max_tokens]
    log("info", f"Text truncat de {len(tokens)} a {len(truncated_tokens)} tokens.")
    return encoding.decode(truncated_tokens)

def run_extraction(convocatoria_id: int) -> List[Dict[str, str]]:
    full_text = get_full_text(convocatoria_id)
    if not full_text:
        log("warn", f"No hi ha text per processar per a la convocatòria ID {convocatoria_id} a run_extraction.")
        return []

    results = []
    # Prenem configuració del model actiu per al límit de tokens
    active_model_info = get_model_info() # Funció de llm_client.py
    # límit de tokens conservador per al text, per deixar màrge al prompt
    # Prenem el GEMINI_MAX_TOKENS del llm_client com a referència, ???
    context_window_for_llm = active_model_info.get("max_tokens", 30000) # Default si no es troba
    max_text_tokens_for_llm = int(context_window_for_llm * 0.70) 
    log("info", f"Usant max_text_tokens_for_llm = {max_text_tokens_for_llm} per a ID {convocatoria_id} (basat en {active_model_info.get('name')})")

    for field, prompt_template in TASKS.items():
        log("info", f"→ Processant camp: '{field}' per a convocatòria ID: {convocatoria_id}")
        text_for_prompt = truncate_to_max_tokens(full_text, max_text_tokens_for_llm)
        prompt_with_text = prompt_template.replace("{{TEXT}}", text_for_prompt)
        
        llm_response_text = "[LLM Error] No s'ha pogut obtenir resposta." # Default
        try:
            llm_response_text = ask_llm(prompt_with_text) # funció genèrica de llm_client
        except Exception as e:
            log("error", f"Excepció cridant a ask_llm per al camp '{field}', ID {convocatoria_id}: {e}")
            llm_response_text = f"[LLM Exception] {str(e)}"

        results.append({
            "camp": field,
            "LLM_Response": llm_response_text # nom de la clau que utilitza save_to_sql
        })
        # log("debug", f"Resposta LLM per '{field}': {llm_response_text[:100]}...") # massa text
    return results

def save_to_sql(results: List[Dict[str, str]], convocatoria_id: int):
    if not results:
        log("info", f"No hay resultados de extracción para guardar en SQL para la convocatoria ID {convocatoria_id}.")
        return

    invalid_responses_substrings = [
        "por favor proporciona", "proporciona el texto", "please provide", 
        "please input", "envíame el texto", "no se ha proporcionado el texto", 
        "no se ha detectado texto", "no se menciona", "no se especifica",
        "no es claro", "texto proporcionado no es suficiente", "información no disponible"
    ]

    data_to_update_in_db = {} # Dades correctes extretes del LLM
    for r_item in results:
        field_name = r_item["camp"]
        extracted_value = r_item.get("LLM_Response", "").strip()
        
        if not extracted_value or \
           any(invalid_sub.lower() in extracted_value.lower() for invalid_sub in invalid_responses_substrings) or \
           len(extracted_value) > 700: # Límit de longitud 
            log("debug", f"Campo '{field_name}' para ID {convocatoria_id}: respuesta LLM inválida/descartada ('{extracted_value[:50]}...').")
            continue
        data_to_update_in_db[field_name] = extracted_value

    if not data_to_update_in_db:
        log("info", f"Ningún dato nuevo válido para actualizar en BD para la convocatoria ID {convocatoria_id} después de filtrar respuestas.")
        return

    conn = None
    cursor = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        # 1. Verificar que la convocatòria existeix
        cursor.execute("SELECT id FROM convocatorias WHERE id = %s", (convocatoria_id,))
        if cursor.fetchone() is None:
            log("error", f"No se encontró la convocatoria con ID {convocatoria_id} para actualizar.")
            return

        # 2.  valores actualesactuals BD

        fields_to_check_in_db = list(data_to_update_in_db.keys())
        
        if not fields_to_check_in_db:
            log("warn", f"No hay campos válidos para consultar/actualizar para ID {convocatoria_id}.")
            return

        # Construir la parte SELECT de la consulta de forma segura
        # No puc fer servir  %s x noms columna de columna no es posible directamente con psycopg2 para SELECT.¿¿¿
        # Construïm llista camps.  Accedim a l'índex
        select_cols_str = ", ".join([f'"{field}"' for field in fields_to_check_in_db]) # Usar comillas dobles por si acaso
        
        query_for_current_values = f"SELECT {select_cols_str} FROM convocatorias WHERE id = %s"
        log("debug", f"Ejecutando SELECT para valores actuales: {query_for_current_values} con ID: {convocatoria_id}")
        cursor.execute(query_for_current_values, (convocatoria_id,))
        current_db_values_row = cursor.fetchone()

        if not current_db_values_row:
            log("error", f"No se pudieron obtener los valores actuales para la convocatoria ID {convocatoria_id} (fetchone retornó None).")
            return

        # Map valors 
        current_data_map = {}
        if cursor.description: # cursor.description conté noms columnes retornadas
            for i, desc_col in enumerate(cursor.description):
                current_data_map[desc_col[0]] = current_db_values_row[i]
        else:
            log("error", f"cursor.description está vacío después del SELECT para ID {convocatoria_id}. No se pueden mapear campos.")
            return
        
        set_clauses_for_update = []
        values_for_sql_update = []

        for field, new_value in data_to_update_in_db.items():
            current_value_from_db = current_data_map.get(field) # valor actual del mapa?
            
            # Lógica per triar si actualitzar
            update_this_field = False
            if str(current_value_from_db or "").strip() != new_value.strip():
                # Si valor un placeholder i valor nou no  actualitzem
                if str(current_value_from_db or "").strip() == "[Extracción Pendiente]" and new_value.strip() != "[Extracció Pendiente]":
                    update_this_field = True
                # Si  valor  NO  placeholder,i és diferent, actualitzem.
                elif str(current_value_from_db or "").strip() != "[Extracción Pendiente]":
                    update_this_field = True
                # No actualitzem si si valor = placeholder y el el nou és el mateix placeholder.
            
            if update_this_field:
                set_clauses_for_update.append(f'"{field}" = %s') # cometes noms columna
                values_for_sql_update.append(new_value)
                log("debug", f"Campo '{field}' para ID {convocatoria_id} cambiará de '{str(current_value_from_db or '')[:50]}' a '{new_value[:50]}'")

        if not set_clauses_for_update:
            log("info", f"No se requieren cambios en la BD para la convocatoria ID {convocatoria_id} (datos extraídos iguales o no mejores).")
            return

        update_query_sql_final = f"UPDATE convocatorias SET {', '.join(set_clauses_for_update)} WHERE id = %s"
        values_for_sql_update.append(convocatoria_id)
        
        log("debug", f"Ejecutando UPDATE: {update_query_sql_final} con {len(values_for_sql_update)-1} valores para ID {convocatoria_id}")
        cursor.execute(update_query_sql_final, values_for_sql_update)
        conn.commit()
        log("info", f"Se han actualizado {len(set_clauses_for_update)} campos para la convocatoria ID {convocatoria_id}.")

    except psycopg2.Error as e_sql:
        log("error", f"Error de base de datos en save_to_sql para ID {convocatoria_id}: {e_sql}")
        if conn: conn.rollback()
    except Exception as e_general:
        log("error", f"Error general en save_to_sql para ID {convocatoria_id}: {e_general}")
        traceback.print_exc()
        if conn: conn.rollback()
    finally:
        if cursor: cursor.close()
        if conn: conn.close()
    if not results:
        log("info", f"No hi ha resultats d'extracció per guardar a SQL per a la convocatòria ID {convocatoria_id}.")
        return

    invalid_responses_substrings = [
        "por favor proporciona", "proporciona el texto", "please provide", 
        "please input", "envíame el texto", "no se ha proporcionado el texto", 
        "no se ha detectado texto", "no se menciona", "no se especifica",
        "no es claro", "texto proporcionado no es suficiente", "información no disponible"
    ] 

    data_to_update_in_db = {}
    for r_item in results:
        field_name = r_item["camp"]
        extracted_value = r_item.get("LLM_Response", "").strip()
        
        # Validació  resposta de l'LLM
        if not extracted_value: # Si està buit
            log("debug", f"Camp '{field_name}' per ID {convocatoria_id}: resposta LLM buida.")
            continue
        if any(invalid_sub.lower() in extracted_value.lower() for invalid_sub in invalid_responses_substrings):
            log("debug", f"Camp '{field_name}' per ID {convocatoria_id}: resposta LLM considerada invàlida ('{extracted_value[:50]}...').")
            continue
        if len(extracted_value) > 700: # Evita valors llargs
            log("debug", f"Camp '{field_name}' per ID {convocatoria_id}: resposta LLM massa llarga ({len(extracted_value)} caràcters), es descarta.")
            continue
            
        data_to_update_in_db[field_name] = extracted_value

    if not data_to_update_in_db:
        log("info", f"Cap dada nova vàlida per actualitzar a la BD per a la convocatòria ID {convocatoria_id} després de filtrar respostes.")
        return

    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        # valors  BD per comparar i actualitzar només si hi ha canvis
        #  SELECT consulta amb camps a  actualitzar
        fields_in_db_to_check = [f'"{f}"' for f in data_to_update_in_db.keys()] # Cometes dobles per a noms de columna
        
        # Comprovem  si convocatòria existeix
        cursor.execute("SELECT EXISTS (SELECT 1 FROM convocatorias WHERE id = %s)", (convocatoria_id,))
        if not cursor.fetchone()[0]:
            log("error", f"No s'ha trobat la convocatòria amb ID {convocatoria_id} per actualitzar a save_to_sql.")
            return

        # Construïm la consulta SELECT només amb  camps on tenim dades per actualitzar
        select_query_for_comparison = f"SELECT {', '.join(fields_in_db_to_check)} FROM convocatorias WHERE id = %s"
        cursor.execute(select_query_for_comparison, (convocatoria_id,))
        current_db_values_row = cursor.fetchone()
        
        if not current_db_values_row: # 22n chcek, no hauria de passar si l'anterior va bé
            log("error", f"No s'han pogut obtenir els valors actuals per a la convocatòria ID {convocatoria_id} tot i existir.")
            return

        current_db_values_map = {fields_to_select[i]: current_db_values_row[i] for i, fields_to_select in enumerate(data_to_update_in_db.keys())}
        
        set_clauses_for_update = []
        values_for_sql_update = []

        for field, new_value in data_to_update_in_db.items():
            current_value_from_db = current_db_values_map.get(field)
            # Actualitzem si nou valor, o si  antic era un placeholder i el nou és diferent
            if str(current_value_from_db or "").strip() != new_value.strip() and \
               not (str(current_value_from_db or "").strip() != "" and "[Extracción Pendiente]" not in str(current_value_from_db or "") and new_value == "[Extracció Pendent]"): # Evitem sobreescriure un valor bo amb un placeholder
                set_clauses_for_update.append(f'"{field}" = %s') # Cometes dobles x noms  columna
                values_for_sql_update.append(new_value)
                log("debug", f"Camp '{field}' per ID {convocatoria_id} canviarà de '{str(current_value_from_db or '')[:50]}' a '{new_value[:50]}'")

        if not set_clauses_for_update:
            log("info", f"No s'han requerit canvis a la BD per a la convocatòria ID {convocatoria_id} (dades extretes iguals o no millors).")
            return

        update_query_sql_final = f"UPDATE convocatorias SET {', '.join(set_clauses_for_update)} WHERE id = %s"
        values_for_sql_update.append(convocatoria_id)
        
        cursor.execute(update_query_sql_final, values_for_sql_update)
        conn.commit()
        log("info", f"S'han actualitzat {len(set_clauses_for_update)} camps per a la convocatòria ID {convocatoria_id}.")

    except psycopg2.Error as e_sql:
        log("error", f"Error de base de dades a save_to_sql per ID {convocatoria_id}: {e_sql}")
        if conn: conn.rollback()
    except Exception as e_general:
        log("error", f"Error general a save_to_sql per ID {convocatoria_id}: {e_general}")
        traceback.print_exc()
        if conn: conn.rollback()
    finally:
        if conn:
            if cursor: cursor.close()
            conn.close()

def get_pending_convocatoria_ids(db_connection) -> List[int]:
    ids = []
    try:
        with db_connection.cursor() as cursor:
            # Cerca convocatòries on 'organismo' o 'objetivo' siguin NULL o  placeholder.
            # Pendent afegir més camps.!!!!
            query = """
                SELECT id FROM convocatorias 
                WHERE organismo IS NULL OR organismo = '[Extracció Pendent]' 
                   OR objetivo IS NULL OR objetivo = '[Extracció Pendent]'
                ORDER BY id
            """
            cursor.execute(query)
            ids = [row[0] for row in cursor.fetchall()]
    except psycopg2.Error as e:
        log("error", f"Error de BD obtenint IDs pendents: {e}")
    return ids

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extreu dades estructurades per a convocatòries.")
    parser.add_argument("convocatoria_id", nargs='?', type=int, help="ID de la convocatòria específica a processar.")
    parser.add_argument("--process-pending", action="store_true", help="Processa totes les convocatòries pendents d'extracció.")
    
    args = parser.parse_args()

    if args.process_pending:
        log("info", "Iniciant processament d'extracció per a TOTES les convocatòries pendents.")
        db_conn_main = None
        try:
            db_conn_main = psycopg2.connect(DATABASE_URL)
            pending_ids = get_pending_convocatoria_ids(db_conn_main)
            if not pending_ids:
                log("info", "No s'han trobat convocatòries pendents d'extracció.")
            else:
                log("info", f"S'han trobat {len(pending_ids)} convocatòries pendents per processar: {pending_ids}")
                for conv_id_loop in pending_ids:
                    log("info", f"--- Processant extracció per a convocatòria ID: {conv_id_loop} ---")
                    # Cada crida a run_extraction i save_to_sql obre i tanca connexió pròpia
                    results_extraction_loop = run_extraction(conv_id_loop)
                    save_to_sql(results_extraction_loop, conv_id_loop)
        except psycopg2.Error as e_db_main:
            log("error", f"Error de connexió a la BD principal per processar pendents: {e_db_main}")
        except Exception as e_main_loop:
            log("error", f"ERROR CRÍTIC processant convocatòries pendents: {e_main_loop}")
            traceback.print_exc()
        finally:
            if db_conn_main:
                db_conn_main.close()
        log("info", "Processament de convocatòries pendents finalitzat.")

    elif args.convocatoria_id:
        convocatoria_id_arg = args.convocatoria_id
        log("info", f"--- Iniciant processament d'extracció per a convocatòria ID: {convocatoria_id_arg} ---")
        results = run_extraction(convocatoria_id_arg)
        save_to_sql(results, convocatoria_id_arg)
        log("info", f"--- Processament per a convocatòria ID: {convocatoria_id_arg} finalitzat ---")
    else:
        print("Ús: python agents/unified_extraction_agent_crono.py <convocatoria_id>")
        print("   o: python agents/unified_extraction_agent_crono.py --process-pending")
        sys.exit(1)