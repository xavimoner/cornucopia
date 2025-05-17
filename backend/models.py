# backend/models.py
from sqlalchemy import Column, Integer, String, Date
from base import Base  # Importació clara de base.py

class Proyecto(Base):
    __tablename__ = "proyectos"

    id = Column(Integer, primary_key=True, index=True)
    organismo = Column(String, index=True)
    nombre = Column(String)
    linea = Column(String)
    fecha_inicio = Column(Date)
    fecha_fin = Column(Date)
    anio = Column(Integer)
    area = Column(String)
    presupuesto_minimo = Column(String)
    presupuesto_maximo = Column(String)
    duracion_minima = Column(String)
    duracion_maxima = Column(String)
    tipo_financiacion = Column(String)
    forma_y_plazo_de_cobro = Column(String)
    minimis = Column(String)


