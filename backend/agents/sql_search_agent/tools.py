# backend/agents/sql_search_agent/tools.py
import psycopg2
import os
from google.adk.tools import FunctionTool
from pydantic import BaseModel, Field, ValidationError
from dotenv import load_dotenv
import traceback # logging 

load_dotenv() 

class SqlQueryParams(BaseModel):

    query: str = Field(description="La consulta SQL SELECT completa a ejecutar contra la tabla 'convocatorias'.")

class SqlSearchTool(FunctionTool):
    def __init__(self):
        self.name = "execute_sql_on_convocatorias" 
        self.description = (
            "Ejecuta una consulta SQL SELECT de solo lectura en la tabla 'convocatorias' "
            "y devuelve los resultados. Úsese para obtener datos específicos y fácticos. "
            "El argumento esperado es 'query' conteniendo la sentencia SQL completa."
        ) # Descripció actualitzada per a l'LLM
        
        super().__init__(
            func=self._run_query
            # FunctionTool utilitza els type hints
            # i la introspecció de la funció _run_query i el seu model Pydantic.
        )
        
        self.db_url = os.getenv("DATABASE_URL")
        if not self.db_url:
            raise ValueError("DATABASE_URL no está configurada en las variables de entorno o no se ha cargado.")
        if not isinstance(self.db_url, str) or len(self.db_url.strip()) == 0:
            raise ValueError("DATABASE_URL está vacía o no es una cadena de texto válida.")

    # Funció espera diccionari (args provinents de l'LLM) i converteix a SqlQueryParams
    def _run_query(self, args: dict) -> str: 
        try:
            # Validar i convertir diccionari d'args a model Pydantic
            # L'LLM genera {'query': 'SELECT ...'}
            params = SqlQueryParams(**args)
        except ValidationError as e:
            error_msg = f"Error en los parámetros proporcionados a la herramienta de búsqueda SQL: {e}. Se esperaba un argumento 'query' con la consulta SQL."
            print(f"ERROR de validación de parámetros en SqlSearchTool: {error_msg}")
            return error_msg

        # consulta SQL que l'agent ha formulat i eina q executarà
        print(f"INFO [SqlSearchTool]: Consulta SQL recibida para ejecutar: {params.query}")

        if not params.query.strip().upper().startswith("SELECT"):
            return "Error: Solo se permiten consultas SELECT."

        try:
            with psycopg2.connect(self.db_url) as conn:
                with conn.cursor() as cur:
                    cur.execute(params.query) 
                    
                    if cur.description: # consulta retorna columnes (és un SELECT amb resultats)?
                        rows = cur.fetchall()
                        if not rows:
                            return "No se encontraron resultados para la consulta."
                        
                        colnames = [desc[0] for desc in cur.description]
                        results = [dict(zip(colnames, row)) for row in rows]
                        
                        results_str = str(results) 
                        max_len = 3500 
                        if len(results_str) > max_len:
                            results_str = results_str[:max_len] + "... (resultados truncados)"
                        return f"Resultados de la consulta: {results_str}"
                    else:

                        return "La consulta se ejecutó, pero no produjo filas de resultados o no era un SELECT estándar."

        except psycopg2.Error as e:
            error_message = f"Error de base de datos: {e.pgcode} - {e.pgerror}. "
            if hasattr(e, 'diag') and e.diag.message_detail:
                error_message += f"Detalle: {e.diag.message_detail}"
            else:
                error_message += "No hay detalles adicionales disponibles."
            print(f"ERROR en SqlSearchTool (DB): {error_message}") 
            return error_message 
        except Exception as e:
            print(f"ERROR inesperado en SqlSearchTool: {str(e)}") 
            traceback.print_exc() # errors 
            return f"Ocurrió un error inesperado al ejecutar la consulta SQL: {str(e)}"