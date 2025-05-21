 #  backend/tasks/sql_task.py

from sqlalchemy.orm import Session
from db import get_db
from models import Proyecto
from fastapi import Depends

class SQLTask:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    async def run(self, query: str) -> str:
        query = query.lower()

        if "quants" in query or "nombre" in query or "total" in query:
            count = self.db.query(Proyecto).count()
            return f"Hi ha un total de {count} projectes registrats."

        if "pressupost mitjà" in query:
            pressupostos = self.db.query(Proyecto.presupuesto_maximo).all()
            valors = [float(p[0].replace('.', '').replace(',', '.')) for p in pressupostos if p[0]]
            mitjana = sum(valors) / len(valors) if valors else 0
            return f"El pressupost mitjà màxim és de {mitjana:,.2f} €."

        return "No he pogut entendre la teva consulta. Torna-la a formular amb més detall."
