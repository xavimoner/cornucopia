# backend/main.py

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from dotenv import load_dotenv
import os

from db import Base, engine, get_db
from models import Proyecto
from orchestrator_adk import handle_chat

# Carregar variables d'entorn
load_dotenv()

# Crear app FastAPI
app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # restringit a ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicialitzar BD
Base.metadata.create_all(bind=engine)

# ─────────────────────────────────────────────────────────────
# MODELS Pydantic
# ─────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    query: str

class ProyectoCreate(BaseModel):
    organismo: str
    nombre: str
    linea: Optional[str] = None
    fecha_inicio: Optional[str] = None
    fecha_fin: Optional[str] = None
    anio: Optional[int] = None
    area: Optional[str] = None
    presupuesto_minimo: Optional[str] = None
    presupuesto_maximo: Optional[str] = None
    duracion_minima: Optional[str] = None
    duracion_maxima: Optional[str] = None
    tipo_financiacion: Optional[str] = None
    forma_y_plazo_de_cobro: Optional[str] = None
    minimis: Optional[str] = None

# ─────────────────────────────────────────────────────────────
# ENDPOINTS
# ─────────────────────────────────────────────────────────────

@app.get("/proyectos/{proyecto_id}")
def read_proyecto(proyecto_id: int, db: Session = Depends(get_db)):
    proyecto = db.query(Proyecto).filter(Proyecto.id == proyecto_id).first()
    if not proyecto:
        raise HTTPException(status_code=404, detail="Projecte no trobat")
    return proyecto

@app.post("/proyectos/", status_code=201)
def create_proyecto(proyecto: ProyectoCreate, db: Session = Depends(get_db)):
    db_proyecto = Proyecto(**proyecto.dict())
    db.add(db_proyecto)
    db.commit()
    db.refresh(db_proyecto)
    return db_proyecto

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    return await handle_chat(request.query)

@app.get("/model")
def get_active_model():
    llm_provider = os.getenv("LLM_PROVIDER", "NO DEFINIT").upper()
    if llm_provider == "OPENAI":
        model = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT")
    elif llm_provider == "GEMINI":
        model = os.getenv("GEMINI_MODEL")
    elif llm_provider == "DEEPSEEK":
        model = os.getenv("DEEPSEEK_MODEL")
    else:
        model = "NO DEFINIT"
    return {
        "llm_provider": llm_provider,
        "model": model
    }


@app.get("/ping")
def ping():
    return {"status": "ok"}

@app.post("/prova_cors")
def prova_cors():
    return {"rebut": {"ok": True}}


