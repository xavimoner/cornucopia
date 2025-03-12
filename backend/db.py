# backend/db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base  # Importació clara de base.py

# Configura la connexió a la base de dades
SQLALCHEMY_DATABASE_URL = "postgresql://admin:adminpass@db:5432/cornucopia"

# Crear el motor de la base de dades
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"host": "db"})

# Crear una sessió de la base de dades
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    # Crear una nova sessió per cada petició
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



