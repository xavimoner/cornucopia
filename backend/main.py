# backend/main.py
from fastapi import FastAPI, Depends, HTTPException, status, Response, File, UploadFile, Request as FastAPIRequest # Afegit Response, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional, AsyncGenerator, List, Dict 
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os
import traceback
import uuid
from datetime import timedelta
import shutil # Per a esborrar directoris

# Importacions d'ADK
from google.adk.runners import Runner
from google.adk.agents.invocation_context import InvocationContext
from google.adk.sessions import InMemorySessionService, Session 
from google.adk.events import Event
from google.genai.types import Content, Part 

# Importacions 
import base 
import db   
import models 
import agents 
import security 
import ingestion_service # mòdul per a la lògica d'ingesta

load_dotenv()

# --- 1. CREACIÓ DE LA INSTÀNCIA DE FastAPI ---
app = FastAPI(title="Cornucopia API con Agentes ADK", version="1.1") 

# --- 2. MODELS PYDANTIC ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    nom_usuari: Optional[str] = Field(default=None, alias="sub")
    rol: Optional[str] = Field(default=None) 

class UsuariPublic(BaseModel):
    id: int
    nom_usuari: str
    email: Optional[str] = None
    nom_complet: Optional[str] = None
    rol: str
    actiu: Optional[bool] = None
    class Config:
        from_attributes = True

# Model per a la petició de scraping inicial (Etapa 1)
class ScrapeRequest(BaseModel): 
    url_convocatoria: str
    nombre_convocatoria_propuesto: str

# Model per a la resposta de l'scraping inicial (Etapa 1)
class ScrapeResponse(BaseModel):
    message: str
    nombre_convocatoria_usado: str
    # ruta_carpeta_servidor: str 
    archivos_gestionados: List[Dict[str,str]] 
    archivos_confirmados_para_procesar: Optional[List[Dict[str, str]]] = None 

class ChatRequest(BaseModel):
    query: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    respuesta: str
    session_id: str 
    user_id: str    

class ConvocatoriaModel(BaseModel):
    id: int
    organismo: Optional[str] = None
    nombre: Optional[str] = None

    class Config:
        from_attributes = True

class ConvocatoriaCreate(BaseModel):
    organismo: str 
    nombre: str   

class FileUploadResponse(BaseModel):
    message: str
    uploaded_filenames: List[str]
    errors: List[str]

class ProcessDocsRequest(BaseModel):
    nombre_convocatoria: str # El nom de la carpeta/convocatòria a processar
    convocatoria_url_original: str # La URL original per desar a la taula convocatorias
    # Opcional: llista de fitxers confirmats per l'usuari per processar.
    # Si no s'envia, es processen tots els fitxers vàlids de la carpeta.
    archivos_confirmados_para_procesar: Optional[List[Dict[str, str]]] = None 


# --- Variables Globals, Funcions de Startup, Middleware (igual que abans) ---


orchestrator_agent_instance: Optional[agents.OrchestratorAgent] = None
runner_instance: Optional[Runner] = None
global_session_service: Optional[InMemorySessionService] = None
APP_NAME_FOR_ADK: str = "cornucopia_chat_app_v12" 

def create_initial_user_if_not_exists(db_session: Session, username_env_var: str, password_env_var: str, email_env_var: str, fullname_env_var: str, rol_assignat: str ):
    username = os.getenv(username_env_var); password = os.getenv(password_env_var)
    email = os.getenv(email_env_var); fullname = os.getenv(fullname_env_var)
    if not username or not password: print(f"ADVERTENCIA: Falten variables per a {username_env_var}."); return
    if not db_session.query(models.Usuari).filter(models.Usuari.nom_usuari == username).first():
        db_session.add(models.Usuari(nom_usuari=username, hashed_password=security.get_password_hash(password), email=email, nom_complet=fullname, rol=rol_assignat, actiu=True))
        db_session.commit(); print(f"INFO: Usuari '{username}' ({rol_assignat}) creat.")
    else: print(f"INFO: Usuari '{username}' ({rol_assignat}) ja existeix.")

@app.on_event("startup")
async def startup_event():
    print("INFO: Iniciant startup de l'aplicació FastAPI...")
    if hasattr(base.Base, 'metadata'): base.Base.metadata.create_all(bind=db.engine); print("INFO: BD verificada/creada.")
    db_s = db.SessionLocal()
    try:
        create_initial_user_if_not_exists(db_s, "INITIAL_ADMIN_USERNAME", "INITIAL_ADMIN_PASSWORD", "INITIAL_ADMIN_EMAIL", "INITIAL_ADMIN_NOM_COMPLET", "administrador")
        create_initial_user_if_not_exists(db_s, "INITIAL_USER_USERNAME", "INITIAL_USER_PASSWORD", "INITIAL_USER_EMAIL", "INITIAL_USER_NOM_COMPLET", "usuario")
    finally: db_s.close()
    global orchestrator_agent_instance, runner_instance, global_session_service, APP_NAME_FOR_ADK
    global_session_service = InMemorySessionService()
    try:
        orchestrator_agent_instance = agents.OrchestratorAgent(); print("INFO: OrchestratorAgent OK.")
        runner_instance = Runner(agent=orchestrator_agent_instance, app_name=APP_NAME_FOR_ADK, session_service=global_session_service); print(f"INFO: Runner OK per a app: {APP_NAME_FOR_ADK}.")
    except Exception as e: print(f"ERROR CRITICO ADK: {e}"); traceback.print_exc()


app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:3000")], # AFEGEIX localhost:8000 si cal, però el navegador ho pot permetre
    allow_credentials=True, 
    allow_methods=["*"], 
    allow_headers=["*"],
)

# --- ENDPOINTS D'AUTENTICACIÓ I USUARIS ---
@app.post("/token", response_model=Token, tags=["Autenticación"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db_session: Session = Depends(db.get_db)):
    print(f"INFO: Intent de login per a l'usuari: {form_data.username}")
    usuari_db = db_session.query(models.Usuari).filter(models.Usuari.nom_usuari == form_data.username).first()
    if not usuari_db or not security.verify_password(form_data.password, usuari_db.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Nombre de usuario o contraseña incorrectos", headers={"WWW-Authenticate": "Bearer"})
    if not usuari_db.actiu:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario inactivo")
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    token_data_to_encode = {"sub": usuari_db.nom_usuari, "rol": usuari_db.rol}
    access_token = security.create_access_token(data=token_data_to_encode, expires_delta=access_token_expires)
    print(f"INFO: Token generat per a: {form_data.username} amb rol: {usuari_db.rol}")
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=UsuariPublic, tags=["Usuarios"])
async def read_users_me(current_user: models.Usuari = Depends(security.get_current_active_user)):
    return current_user

# --- ENDPOINTS D'ADMINISTRACIÓ PER A LA INGESTA ---

@app.post("/admin/scrape-initial-files", response_model=ScrapeResponse, tags=["Administración"])
async def scrape_initial_files_endpoint(
    scrape_request: ScrapeRequest,
    db_session: Session = Depends(db.get_db), 
    current_admin: models.Usuari = Depends(security.get_current_admin_user)
):
    print(f"INFO [ScrapeEndpoint]: Petició rebuda de '{current_admin.nom_usuari}' per URL: {scrape_request.url_convocatoria}, Nom Proposat: {scrape_request.nombre_convocatoria_propuesto}")

    # PAS 1: Comprovar conflictes de BD (nom o URL)
    conflicto_db_detectado = False
    mensajes_conflicto_db = []
    existing_by_name = db_session.query(models.Convocatoria.id, models.Convocatoria.nombre, models.Convocatoria.link_convocatoria)\
        .filter(models.Convocatoria.nombre == scrape_request.nombre_convocatoria_propuesto).first()
    if existing_by_name:
        conflicto_db_detectado = True
        mensajes_conflicto_db.append(f"Ya existe una convocatoria en la BD con el nombre '{scrape_request.nombre_convocatoria_propuesto}' (ID: {existing_by_name.id}, URL: {existing_by_name.link_convocatoria}).")
    
    existing_by_url = db_session.query(models.Convocatoria.id, models.Convocatoria.nombre, models.Convocatoria.link_convocatoria)\
        .filter(models.Convocatoria.link_convocatoria == scrape_request.url_convocatoria).first()
    if existing_by_url:
        if not (existing_by_name and existing_by_name.id == existing_by_url.id): # Evitar duplicar si nom i URL són de la mateixa entrada
            conflicto_db_detectado = True
            mensajes_conflicto_db.append(f"La URL '{scrape_request.url_convocatoria}' ya está asociada a la convocatoria '{existing_by_url.nombre}' (ID: {existing_by_url.id}) en la BD.")

    if conflicto_db_detectado:
        full_conflict_message = "\n".join(mensajes_conflicto_db) + \
                                "\n\nPor favor, use un nombre de convocatoria diferente o verifique la URL. " + \
                                "La opción de actualizar una convocatoria existente se puede implementar en el futuro."
        print(f"WARN [ScrapeEndpoint]: Conflicto de BD detectado: {full_conflict_message}")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=full_conflict_message)
        
    # PAS 2: Si no hi ha conflictes de BD, procedir amb scraping i descàrrega
    print(f"INFO [ScrapeEndpoint]: Sin conflictos de BD. Llamando a ingestion_service.scrape_and_download_initial_files...")
    try:
        result_scraping = await ingestion_service.scrape_and_download_initial_files(
            convocatoria_url=scrape_request.url_convocatoria,
            nombre_convocatoria_propuesto=scrape_request.nombre_convocatoria_propuesto
        )
        
        status_code_internal = result_scraping.get("status_code_internal", 500)
        
        if status_code_internal == 409 and result_scraping.get("conflicto_directorio"):
            # Conflicte de directori detectat per ingestion_service
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=result_scraping.get("message"))
        elif status_code_internal >= 400 and status_code_internal != 409: # Altres errors durant scraping/descàrrega
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=result_scraping.get("message","Error durante scraping/descarga."))
        
        # Si tot va bé (status_code_internal és 200 o 207), retornem el resultat
        return ScrapeResponse(**result_scraping) # Desempaquetem el diccionari al model de resposta
        
    except HTTPException as http_exc:
        raise http_exc # Repropaguem excepcions HTTP 
    except Exception as e:
        print(f"ERROR CRITICO en /admin/scrape-initial-files: {e}"); traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error crítico en el scraping: {str(e)}")

@app.post("/admin/upload-additional-file/{nombre_convocatoria}", 
          response_model=FileUploadResponse, 
          tags=["Administración"]) 
async def upload_additional_file_endpoint( 
    nombre_convocatoria: str,
    files: List[UploadFile] = File(...), # Esperem  LLISTA de fitxers
    current_admin: models.Usuari = Depends(security.get_current_admin_user)
):
    print(f"INFO [UploadFile Endpoint]: Petición recibida para subir archivos  a: {nombre_convocatoria}")
    print(f"INFO [UploadFile Endpoint]: Nombre de arvhivos: {len(files)}")

    shared_documents_path_in_container = "/app/shared_documents_output"
    convocatoria_folder_name = "".join(c if c.isalnum() or c in (' ') else '_' for c in nombre_convocatoria).strip().replace(" ", "_")
    convocatoria_save_path = os.path.join(shared_documents_path_in_container, convocatoria_folder_name)

    if not os.path.isdir(convocatoria_save_path):
        try:
            os.makedirs(convocatoria_save_path, exist_ok=True)
            print(f"WARN [UploadFile Endpoint]: El directorio {convocatoria_save_path} no existia, se ha creado.")
        except OSError as e:
            raise HTTPException(status_code=500, detail=f"No se pudo crear el directorio de destino: {e}")

    uploaded_filenames = []
    errors_upload = []

    for file_upload_object in files:
        try:
            safe_filename = "".join(c if c.isalnum() or c in ('.', '_', '-') else '_' for c in file_upload_object.filename)
            file_location = os.path.join(convocatoria_save_path, safe_filename)
            
            print(f"INFO [UploadFile Endpoint]: Intentando guardar archvo '{safe_filename}' a '{file_location}'")
            with open(file_location, "wb+") as file_object_disk:
                shutil.copyfileobj(file_upload_object.file, file_object_disk)
            
            uploaded_filenames.append(safe_filename)
            print(f"INFO [UploadFile Endpoint]: Fitxer '{safe_filename}' desat correctament.")
        except Exception as e:
            errors_upload.append(f"No se pudo guardar el archivo '{file_upload_object.filename}': {str(e)}")
            print(f"ERROR [UploadFile Endpoint]: No se pudo guardar '{file_upload_object.filename}': {e}")
        finally:
            await file_upload_object.close() 

    if errors_upload:
        return FileUploadResponse(
            message=f"Subida de archivos completada con {len(errors_upload)} errores.", # Espanyol
            uploaded_filenames=uploaded_filenames,
            errors=errors_upload
        )
    return FileUploadResponse(
        message=f"{len(uploaded_filenames)} archivos subidos correctamente a la carpeta '{convocatoria_folder_name}'.", # Espanyol
        uploaded_filenames=uploaded_filenames,
        errors=[]
    )
@app.post("/admin/process-documents-for-db", response_model=Dict, tags=["Administración"], status_code=status.HTTP_202_ACCEPTED)
async def process_documents_for_db_endpoint(
    process_request: ProcessDocsRequest,
    db_session: Session = Depends(db.get_db),
    current_admin: models.Usuari = Depends(security.get_current_admin_user)
):
    print(f"INFO: [ProcessDocs Endpoint] Petición de '{current_admin.nom_usuari}' para  procesar BD de: {process_request.nombre_convocatoria}")
    
    shared_documents_path_in_container = "/app/shared_documents_output"
    convocatoria_folder_name = "".join(c if c.isalnum() or c in (' ') else '_' for c in process_request.nombre_convocatoria).strip().replace(" ", "_")
    ruta_carpeta_convocatoria_on_server = os.path.join(shared_documents_path_in_container, convocatoria_folder_name)

    if not os.path.isdir(ruta_carpeta_convocatoria_on_server):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"La carpeta '{convocatoria_folder_name}' no existeix al servidor per processar.")

    try:
        result_processing = ingestion_service.process_folder_files_for_db(
            db_session=db_session,
            nombre_convocatoria=process_request.nombre_convocatoria,
            convocatoria_url_original=process_request.convocatoria_url_original,
            ruta_carpeta_convocatoria_on_server=ruta_carpeta_convocatoria_on_server
        )
        
        status_code_internal = result_processing.get("status_code_internal", 500)
        if status_code_internal >= 400: # Si el servei indica un error
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=result_processing.get("message"))
        
        return result_processing

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        print(f"ERROR CRITICO en /admin/process-documents-for-db: {e}"); traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error crítico: {str(e)}")

@app.delete("/admin/cancel-ingest/{nombre_convocatoria}", response_model=Dict, tags=["Administración"])
async def cancel_ingest_endpoint(
    nombre_convocatoria: str,
    current_admin: models.Usuari = Depends(security.get_current_admin_user)
):
    print(f"INFO: [CancelIngest Endpoint] Petición de '{current_admin.nom_usuari}' para cancelar ingesta de: {nombre_convocatoria}")
    shared_documents_path_in_container = "/app/shared_documents_output"
    convocatoria_folder_name = "".join(c if c.isalnum() or c in (' ') else '_' for c in nombre_convocatoria).strip().replace(" ", "_")
    convocatoria_save_path = os.path.join(shared_documents_path_in_container, convocatoria_folder_name)

    if os.path.isdir(convocatoria_save_path):
        try:
            shutil.rmtree(convocatoria_save_path) # Esborra la carpeta i tot el seu contingut
            print(f"INFO [CancelIngest Endpoint]: Directori '{convocatoria_save_path}' esborrat correctament.")
            return {"message": f"Ingesta cancel·lada i directori '{convocatoria_folder_name}' esborrat."}
        except Exception as e:
            print(f"ERROR [CancelIngest Endpoint]: No s'ha pogut esborrar el directori '{convocatoria_save_path}': {e}")
            raise HTTPException(status_code=500, detail=f"Error esborrant directori: {e}")
    else:
        print(f"WARN [CancelIngest Endpoint]: El directori '{convocatoria_save_path}' no existia.")
        return {"message": f"El directori '{convocatoria_folder_name}' no existia. No s'ha esborrat res."}

# --- Endpoints Públics (Xat, Model, Convocatòries Públiques) ---
@app.post("/chat", response_model=ChatResponse, tags=["Chatbot"])
async def chat_with_agent_endpoint(request: ChatRequest, current_user: models.Usuari = Depends(security.get_current_active_user)):

    if orchestrator_agent_instance is None or runner_instance is None: raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Servicio de agente no disponible.")
    if not request.query or not request.query.strip(): raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La consulta no puede estar vacía.")
    user_id_for_session = current_user.nom_usuari 
    session_id_to_use = request.session_id or f"session_{current_user.nom_usuari}_{uuid.uuid4().hex[:8]}"
    current_session_obj: Optional[Session] = None
    try:
        current_session_obj = global_session_service.get_session(app_name=APP_NAME_FOR_ADK, user_id=user_id_for_session, session_id=session_id_to_use)
        if current_session_obj is None: current_session_obj = global_session_service.create_session(app_name=APP_NAME_FOR_ADK, user_id=user_id_for_session, session_id=session_id_to_use)
    except KeyError: current_session_obj = global_session_service.create_session(app_name=APP_NAME_FOR_ADK, user_id=user_id_for_session, session_id=session_id_to_use)
    except Exception as e: print(f"ERROR CRITICO gestió sessió: {e}"); traceback.print_exc(); raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error gestió sessió.")
    if not isinstance(current_session_obj, Session): raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Fallo intern sessió.")
    try:
        input_message = Content(role="user", parts=[Part(text=request.query)]); final_agent_text_response = ""
        event_generator: AsyncGenerator[Event, None] = runner_instance.run_async(user_id=current_session_obj.user_id, session_id=current_session_obj.id, new_message=input_message)
        async for event in event_generator:
            current_event_text = "";
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text: current_event_text += part.text
            current_event_text = current_event_text.strip()
            if current_event_text and event.author == orchestrator_agent_instance.name: final_agent_text_response = current_event_text
        if not final_agent_text_response: final_agent_text_response = "El agente no proporcionó una respuesta de texto final."
        return ChatResponse(respuesta=final_agent_text_response, session_id=current_session_obj.id, user_id=current_session_obj.user_id)
    except Exception as e: print(f"ERROR: Excepción en /chat: {e}"); traceback.print_exc(); raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error interno ({type(e).__name__}).")

@app.get("/model", tags=["Información"]) 
def get_active_model_endpoint():
    llm_provider = os.getenv("LLM_PROVIDER", "NO DEFINIDO").upper()
    model_name = "NO DEFINIDO"
    if llm_provider == "AZURE_OPENAI": model_name = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT", "NO DEFINIDO")
    elif llm_provider == "GEMINI": model_name = os.getenv("ADK_GEMINI_MODEL_NAME", os.getenv("GEMINI_MODEL", "NO DEFINIDO"))
    elif llm_provider == "DEEPSEEK": model_name = os.getenv("DEEPSEEK_MODEL", "NO DEFINIDO")
    display_provider = llm_provider
    if llm_provider == "AZURE_OPENAI": display_provider = "OPENAI" 
    return {"llm_provider": display_provider, "model": model_name}

@app.get("/convocatorias/{convocatoria_id}", response_model=ConvocatoriaModel, tags=["Convocatorias (CRUD Ejemplo)"]) 
def read_convocatoria_endpoint(convocatoria_id: int, db_session: Session = Depends(db.get_db)):
    db_convocatoria = db_session.query(models.Convocatoria).filter(models.Convocatoria.id == convocatoria_id).first()
    if db_convocatoria is None: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Convocatoria no encontrada")
    return db_convocatoria

@app.post("/convocatorias/", response_model=ConvocatoriaModel, status_code=status.HTTP_201_CREATED, tags=["Convocatorias (CRUD Ejemplo)"]) 
def create_convocatoria_endpoint(convocatoria: ConvocatoriaCreate, db_session: Session = Depends(db.get_db)):
    db_convocatoria = models.Convocatoria(**convocatoria.model_dump(exclude_unset=True))
    db_session.add(db_convocatoria); db_session.commit(); db_session.refresh(db_convocatoria)
    return db_convocatoria
    
@app.get("/ping", tags=["Utilidades"]) 
def ping_endpoint():
    return {"status": "ok"}