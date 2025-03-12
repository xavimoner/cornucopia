# backend/main.py
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from db import Base, engine, get_db  # Importació absoluta i clara
from models import Proyecto

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Backend funciona!"}

# Crear la base de dades (si no existeix)
Base.metadata.create_all(bind=engine)

# Obtenir un projecte específic per ID
@app.get("/proyectos/{proyecto_id}")
def read_proyecto(proyecto_id: int, db: Session = Depends(get_db)):
    proyecto = db.query(Proyecto).filter(Proyecto.id == proyecto_id).first()
    return proyecto
