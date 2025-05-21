# backend/agents/orchestrator_agent/agent.py
import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.genai import types as genai_types
from google.adk.tools import agent_tool

from .. import SqlSearchAgent
from .. import VectorSearchAgent

load_dotenv()

class OrchestratorAgent(LlmAgent):
    def __init__(self):

        adk_model_name = os.getenv("ADK_GEMINI_MODEL_NAME")
        
        if not adk_model_name and os.getenv("ADK_LLM_PROVIDER", "").upper() == "GEMINI":
            raise ValueError("ADK_GEMINI_MODEL_NAME no está definido en las variables de entorno, "
                             "pero ADK_LLM_PROVIDER está configurado para GEMINI.")
            
        sql_agent_instance = SqlSearchAgent()
        vector_agent_instance = VectorSearchAgent()
        
        sql_agent_as_tool = agent_tool.AgentTool(agent=sql_agent_instance)
        vector_agent_as_tool = agent_tool.AgentTool(agent=vector_agent_instance)

        orchestrator_instruction = (
            "Eres un consultor inteligente de subvenciones y ayudas. Tu objetivo es ayudar a los usuarios a encontrar la información que necesitan de la manera más eficiente.\n"
            "Analiza cuidadosamente la consulta del usuario para determinar la mejor estrategia de búsqueda:\n\n"
            "1. Si la consulta busca datos muy específicos, factuales, o requiere filtros precisos sobre características de las convocatorias "
            "(como nombres, organismos, fechas exactas, rangos de presupuesto, identificadores, etc.), "
            "deberías usar la herramienta 'SqlSearchAgent'. \n"
            "   Ejemplos: '¿Cuál es el presupuesto de la ayuda X?', 'Lista las ayudas del organismo Y que finalizan en 2024', "
            "   'Encuentra convocatorias para PYMEs en el sector energético con un mínimo de 100.000 euros'.\n"
            "   Para esta herramienta, intenta formular la pregunta de manera que el agente SQL pueda construir una consulta SQL, "
            "   o si la pregunta ya es muy técnica, indica la posible consulta SQL.\n\n"
            "2. Si la consulta es más general, conceptual, busca entender el contenido de documentos, o explora temas amplios "
            "   (como 'ayudas para inteligencia artificial', 'proyectos europeos de innovación', 'documentación técnica sobre eficiencia energética'), "
            "   deberías usar la herramienta 'VectorSearchAgent'. Esta herramienta buscará en el contenido de los documentos.\n"
            "   Ejemplos: 'Háblame de subvenciones para la transformación digital', '¿Existen ayudas para startups de tecnología verde?', "
            "   'Necesito información sobre los criterios de valoración de proyectos de I+D+i'.\n\n"
            "3. Si la consulta es una pregunta general, un saludo, o no está relacionada con la búsqueda de subvenciones, "
            "   responde de manera natural y conversacional sin usar ninguna herramienta.\n\n"
            "Proceso a seguir:\n"
            "- Primero, decide qué herramienta es la más adecuada (o ninguna).\n"
            "- Si usas una herramienta, formula la entrada para esa herramienta de la manera más efectiva (generalmente, la consulta original del usuario o una versión ligeramente adaptada).\n"
            "- Una vez que la herramienta te devuelva un resultado, preséntalo de forma clara y útil al usuario.\n"
            "- Si el resultado de una herramienta no es satisfactorio o no encuentra nada, informa al usuario e considera si la otra herramienta podría ser útil o si necesitas más información del usuario.\n"
            "Sé claro en tus respuestas y justifica brevemente por qué usas una herramienta si lo haces."
        )

        super().__init__(
            name="OrchestratorAgent",
            model=adk_model_name, 
            instruction=orchestrator_instruction,
            tools=[sql_agent_as_tool, vector_agent_as_tool],
            generate_content_config=genai_types.GenerationConfig(temperature=0.3)
        )