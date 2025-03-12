# backend/main.py
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from db import Base, engine, get_db  # Importació absoluta i clara
from models import Proyecto
from pydantic import BaseModel

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

# Crear un projecte nou a la base de dades
class ProyectoCreate(BaseModel):
    organismo: str
    nombre: str
    linea: str
    fecha_inicio: str
    fecha_fin: str
    anio: int
    area: str
    presupuesto_minimo: str
    presupuesto_maximo: str
    duracion_minima: str
    duracion_maxima: str
    tipo_financiacion: str
    forma_y_plazo_de_cobro: str
    minimis: str

@app.post("/proyectos/", status_code=201)
def create_proyecto(proyecto: ProyectoCreate, db: Session = Depends(get_db)):
    db_proyecto = Proyecto(
        organismo=proyecto.organismo,
        nombre=proyecto.nombre,
        linea=proyecto.linea,
        fecha_inicio=proyecto.fecha_inicio,
        fecha_fin=proyecto.fecha_fin,
        anio=proyecto.anio,
        area=proyecto.area,
        presupuesto_minimo=proyecto.presupuesto_minimo,
        presupuesto_maximo=proyecto.presupuesto_maximo,
        duracion_minima=proyecto.duracion_minima,
        duracion_maxima=proyecto.duracion_maxima,
        tipo_financiacion=proyecto.tipo_financiacion,
        forma_y_plazo_de_cobro=proyecto.forma_y_plazo_de_cobro,
        minimis=proyecto.minimis
    )
    db.add(db_proyecto)
    db.commit()
    db.refresh(db_proyecto)
    return db_proyecto

