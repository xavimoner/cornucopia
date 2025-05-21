# backend/db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import base 

SQLALCHEMY_DATABASE_URL = "postgresql://admin:adminpass@db:5432/cornucopia"


engine = create_engine(SQLALCHEMY_DATABASE_URL) # No cal connect_args={"host": "db"} si la URL ja té el host 'db'

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db_session = SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()


