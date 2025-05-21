# backend/models.py
from sqlalchemy import Column, Integer, Text, TIMESTAMP, String, Boolean, DateTime, func, ForeignKey 
from pgvector.sqlalchemy import VECTOR  
import base 

class Convocatoria(base.Base):
    __tablename__ = "convocatorias"

    id = Column(Integer, primary_key=True, index=True)
    organismo = Column(Text, nullable=True)
    nombre = Column(Text, nullable=True)
    linea = Column(Text, nullable=True)
    fecha_inicio = Column(Text, nullable=True)
    fecha_fin = Column(Text, nullable=True)
    objetivo = Column(Text, nullable=True)
    beneficiarios = Column(Text, nullable=True)
    anio = Column(Text, nullable=True)
    area = Column(Text, nullable=True)
    presupuesto_minimo = Column(Text, nullable=True)
    presupuesto_maximo = Column(Text, nullable=True)
    duracion_minima = Column(Text, nullable=True)
    duracion_maxima = Column(Text, nullable=True)
    intensidad_de_subvencion = Column(Text, nullable=True)
    intensidad_de_prestamo = Column(Text, nullable=True)
    tipo_financiacion = Column(Text, nullable=True)
    forma_y_plazo_de_cobro = Column(Text, nullable=True)
    minimis = Column(Text, nullable=True)
    region_de_aplicacion = Column(Text, nullable=True)
    tipo_de_consorcio = Column(Text, nullable=True)
    costes_elegibles = Column(Text, nullable=True)
    dotacion_presupuestaria = Column(Text, nullable=True)
    numero_potencial_de_ayudas = Column(Text, nullable=True)
    tasa_de_exito = Column(Text, nullable=True)
    link_ficha_tecnica = Column(Text, nullable=True)
    link_orden_de_bases = Column(Text, nullable=True)
    link_convocatoria = Column(Text, nullable=True)
    link_plantilla_memoria = Column(Text, nullable=True)
    criterios_valoracion = Column(Text, nullable=True)
    documentacion_solicitud = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False) 

    def __repr__(self):
        return f"<Convocatoria(id={self.id}, nombre='{self.nombre[:30]}...')>"
    
class Usuari(base.Base):
    __tablename__ = "usuaris"

    id = Column(Integer, primary_key=True, index=True)
    nom_usuari = Column(String(255), unique=True, index=True, nullable=False) 
    hashed_password = Column(String(255), nullable=False) 
    email = Column(String(255), unique=True, index=True, nullable=True) 
    nom_complet = Column(String(255), nullable=True) 
    rol = Column(String(50), default="usuari", nullable=False) 
    actiu = Column(Boolean, default=True)
    data_creacio = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Usuari(id={self.id}, nom_usuari='{self.nom_usuari}', rol='{self.rol}')>"

class Documentos(base.Base): 
    __tablename__ = "documentos"

    id = Column(Integer, primary_key=True, index=True)
   
    convocatoria_id = Column(Integer, ForeignKey("convocatorias.id", ondelete="CASCADE")) 
    fuente = Column(Text, nullable=False)
    url = Column(Text, nullable=True) 
    titulo = Column(Text, nullable=True)
    texto = Column(Text, nullable=True) 
    embedding = Column(VECTOR(1536), nullable=True) 
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False) 

    def __repr__(self):
        return f"<Documentos(id={self.id}, titulo='{self.titulo}', convocatoria_id={self.convocatoria_id})>"