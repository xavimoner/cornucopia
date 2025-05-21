# backend/agents/vector_search_agent/tools.py
import psycopg2
import os
from openai import AzureOpenAI
from google.adk.tools import FunctionTool
from pydantic import BaseModel, Field, ValidationError 
from dotenv import load_dotenv
import traceback

load_dotenv()

class VectorSearchParams(BaseModel):
    query_text: str = Field(description="El texto de la consulta del usuario para buscar documentos semánticamente similares.")
    top_k: int = Field(default=5, description="Número de documentos similares a recuperar (entre 1 y 5).")

class VectorSearchTool(FunctionTool):
    def __init__(self):
        self.name = "search_similar_documents" 
        self.description = "Busca documentos (fichas técnicas, memorias, etc.) que sean semánticamente similares al texto de la consulta. Utiliza embeddings vectoriales y pgvector. Es ideal para consultas en lenguaje natural sobre el contenido de los documentos."
        
        super().__init__(
            func=self._run_vector_search
            
        )
        
        self.db_url = os.getenv("DATABASE_URL")
        
        self.azure_openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.azure_openai_embedding_deployment = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
        self.azure_openai_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")

        if not all([self.azure_openai_api_key, self.azure_openai_endpoint, self.azure_openai_embedding_deployment]):
            missing_vars = [
                var for var, val in {
                    "AZURE_OPENAI_API_KEY": self.azure_openai_api_key,
                    "AZURE_OPENAI_ENDPOINT": self.azure_openai_endpoint,
                    "AZURE_OPENAI_EMBEDDING_DEPLOYMENT": self.azure_openai_embedding_deployment
                }.items() if not val
            ]
            raise ValueError(f"Faltan variables de entorno de Azure OpenAI para embeddings: {', '.join(missing_vars)}")
        try:
            self.azure_client = AzureOpenAI(
                api_key=self.azure_openai_api_key,
                azure_endpoint=self.azure_openai_endpoint,
                api_version=self.azure_openai_api_version
            )
        except Exception as e:
            raise RuntimeError(f"Error al inicializar el cliente de AzureOpenAI para embeddings: {e}")

    def _get_embedding_azure(self, text: str) -> list[float]:

        if not text or not text.strip():
            raise ValueError("El texto para generar el embedding no puede estar vacío.")
        try:
            response = self.azure_client.embeddings.create(
                input=text,
                model=self.azure_openai_embedding_deployment
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"ERROR al generar embedding con Azure OpenAI: {e}")
            raise RuntimeError(f"Fallo al generar embedding: {e}")

    #run_async de FunctionTool passa arguments diccionari a 'args'
    # funció embolcallada _run_vector_search rep aquest diccionari.
    
    def _run_vector_search(self, params_dict: dict) -> str:
        try:
            params = VectorSearchParams(**params_dict)
        except ValidationError as e:
            print(f"ERROR de validación de parámetros en VectorSearchTool: {e}")
            return f"Error en los parámetros proporcionados a la herramienta de búsqueda vectorial: {e}"

        if not (1 <= params.top_k <= 5):
            print(f"ADVERTENCIA: top_k ({params.top_k}) fuera del rango permitido (1-5). Usando valor por defecto 3.")
            params.top_k = 3

        try:
            query_embedding = self._get_embedding_azure(params.query_text)

            # Format correcte per a pgvector: '[f1,f2,f3,...]'
            embedding_str_for_pgvector = "[" + ",".join(map(str, query_embedding)) + "]"

            with psycopg2.connect(self.db_url) as conn:
                with conn.cursor() as cur:
                    sql_query = f"""
                        SELECT
                            id, texto, titulo, fuente, url, convocatoria_id,
                            embedding <=> %s::vector AS cosine_distance 
                        FROM documentos
                        ORDER BY cosine_distance ASC
                        LIMIT %s;
                    """
                    cur.execute(sql_query, (embedding_str_for_pgvector, params.top_k)) # Utilitzem la nova cadena
                    rows = cur.fetchall()

                    if not rows:
                        return "No se encontraron documentos semánticamente similares para su consulta."

                    colnames = [desc[0] for desc in cur.description]
                    results = [dict(zip(colnames, row)) for row in rows]

                    formatted_results = []
                    for i, res in enumerate(results):
                        distance_score = res.get('cosine_distance', 2.0) 
                        text_fragment = res.get('texto', '')
                        max_fragment_len = 250 
                        if len(text_fragment) > max_fragment_len:
                            text_fragment = text_fragment[:max_fragment_len] + "..."
                        formatted_results.append(
                            f"Documento {i+1} (Distancia: {distance_score:.4f}):\n"
                            f"  Título: {res.get('titulo', 'N/A')}\n"
                            f"  ID Documento: {res.get('id', 'N/A')}\n"
                            f"  Fuente: {res.get('fuente', 'N/A')}\n"
                            f"  URL: {res.get('url', 'N/A')}\n"
                            f"  Fragmento: \"{text_fragment}\""
                        )
                    return f"Se encontraron {len(results)} documentos relevantes:\n\n" + "\n\n".join(formatted_results)
        
        
        except psycopg2.Error as e:
            error_message = f"Error de base de datos durante la búsqueda vectorial: {e.pgcode} - {e.pgerror}. "
            if hasattr(e, 'diag') and e.diag.message_detail: # HINT or DETAIL might be in diag.message_detail
                error_message += f"Detalle: {e.diag.message_detail}"
            else: # Fallback si no detall específic
                error_message += "No hay detalles adicionales disponibles."

            # Info específica sobre l'error de "operator does not exist"
            if "operator does not exist" in str(e) and "vector <=> vector" in str(e): # Comprovació més específica
                 error_message += " Pista: Verifique que la extensión pgvector esté correctamente instalada y activada en la base de datos actual, y que los tipos de datos sean correctos."
            elif "Vector contents must start with" in str(e):
                 error_message += " Pista: El formato del vector enviado a la base de datos es incorrecto. Debe ser '[f1,f2,...]'."


            print(f"ERROR en VectorSearchTool (DB): {error_message}")
            return error_message
        except ValueError as ve: 
            print(f"ERROR de validación en VectorSearchTool: {str(ve)}")
            return f"Error de validación: {str(ve)}"
        except RuntimeError as re: 
             print(f"ERROR en tiempo de ejecución en VectorSearchTool (probablemente embedding): {str(re)}")
             return f"Error al procesar la consulta para búsqueda semántica: {str(re)}"
        except Exception as e:
            print(f"ERROR inesperado en VectorSearchTool: {str(e)}")
            traceback.print_exc()
            return f"Ocurrió un error inesperado durante la búsqueda vectorial: Error genérico."