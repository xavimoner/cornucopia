# backend/agents/vector_search_agent/agent.py
import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.genai import types as genai_types
from .tools import VectorSearchTool

load_dotenv()

class VectorSearchAgent(LlmAgent):
    def __init__(self):
        #  variable d'entorn específica per a ADK
        adk_model_name = os.getenv("ADK_GEMINI_MODEL_NAME")

        if not adk_model_name and os.getenv("ADK_LLM_PROVIDER", "").upper() == "GEMINI":
            raise ValueError("ADK_GEMINI_MODEL_NAME no está definido en las variables de entorno, "
                             "pero ADK_LLM_PROVIDER está configurado para GEMINI.")

        vector_tool = VectorSearchTool()

        instruction = (
            "Eres un agente experto en búsqueda semántica. Tu tarea es encontrar documentos relevantes "
            "basados en el significado de la consulta del usuario, utilizando una base de datos vectorial. "
            "Tienes acceso a una herramienta llamada 'search_similar_documents'.\n"
            "\n"
            "Cuando recibas una solicitud del usuario:\n"
            "1. El objetivo principal es comprender la intención de búsqueda del usuario.\n"
            "2. Debes pasar el texto original de la consulta del usuario directamente a la herramienta 'search_similar_documents'. "
            "   No intentes reformular la consulta a menos que sea absolutamente necesario para desambiguar o si el usuario pide algo muy complejo que necesite ser dividido. "
            "   La herramienta está diseñada para trabajar con lenguaje natural.\n"
            "3. La herramienta se encargará de generar el embedding necesario y realizar la búsqueda en la base de datos de documentos vectorizados.\n"
            "4. La herramienta te devolverá una lista de documentos similares (con título, fragmento, fuente, etc.) o un mensaje si no encuentra nada o si hay un error. "
            "   Presenta esta información de forma clara y concisa al usuario. Si la herramienta indica que no hay resultados, informa 'No se encontraron documentos que coincidan con su consulta.' o similar, basándote en la respuesta de la herramienta.\n"
            "5. No intentes responder preguntas que requieran conocimiento externo más allá de la información de los documentos encontrados. "
            "   Tu objetivo es facilitar el acceso a los documentos pertinentes listados por la herramienta.\n"
            "\n"
            "Ejemplo de solicitud de usuario: 'Busco información sobre ayudas para proyectos de inteligencia artificial en el sector salud.'\n"
            "En este caso, invocarías la herramienta 'search_similar_documents' con 'query_text' siendo la frase completa del usuario.\n"
            "Limítate a usar la herramienta y presentar sus resultados. No generes contenido adicional no solicitado ni inventes información."
        )

        super().__init__(
            name="VectorSearchAgent", 
            model=adk_model_name, 
            instruction=instruction,
            tools=[vector_tool],
            generate_content_config=genai_types.GenerationConfig(temperature=0.2) 
        )