# backend/agents/orchestrator_agent_adk.py

from google.adk.agents import Agent
from llm_client_adk import get_lite_llm # Assuming get_lite_llm fetches a valid LLM model
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Importa les funcions d'execució dels sub-agents
from agents.sql_agent import execute_sql_agent
from agents.rag_agent import execute_rag_agent

# Definició de l'agent orquestrador
orchestrator_agent = Agent(
    name="AgenteCoordinador",
    model=get_lite_llm(), # Assume this returns a valid LLM instance (e.g., Gemini)
    description="Agente que decide a que subagente enviar la consulta",
    instruction="""
Eres un agente coordinador que debe decidir si una consulta debe ser respondida por el SQLAgent o por el RAGAgent.

- Si la consulta contiene filtros estructurados como fechas, regiones, presupuestos u otros datos específicos, reenvíala al **SQLAgent**.
- Si la consulta es conceptual, general, o requiere una explicación, resumen o interpretación de texto largo, reenvíala al **RAGAgent**.

Responde únicamente con: **SQLAgent** o **RAGAgent**.
""",
)

# Configuració del servei de sessió i del runner per a l'agent orquestrador
session_service = InMemorySessionService()
runner = Runner(
    agent=orchestrator_agent,
    app_name="orchestrator_agent_app",
    session_service=session_service
)

# Identificadors de sessió fixos per simplicitat. En una app real, session_id podria ser dinàmic per usuari.
USER_ID = "user_orchestrator_001" # Es pot canviar per diferenciar usuaris si cal
SESSION_ID = "session_orchestrator_main" # Noms més descriptius per a depuració

async def execute_orchestrator_agent(query: str) -> str:
    """
    Executa l'agent orquestrador per decidir a quin sub-agent s'ha d'enviar la consulta.
    """
    user_message_content = types.Content(role="user", parts=[types.Part(text=query)])

    # Correcció clau: Assegurar-se que la sessió existeix.
    # get_session i create_session de InMemorySessionService prenen només el session_id com a argument posicional.
    session = await session_service.get_session(SESSION_ID)
    if not session:
        session = await session_service.create_session(SESSION_ID)
        # print(f"DEBUG: [Orchestrator] Sesión '{SESSION_ID}' creada.") # Opcional para depuración
    # else:
        # print(f"DEBUG: [Orchestrator] Sesión '{SESSION_ID}' encontrada.") # Opcional para depuración

    try:
        async for event in runner.run_async(
            user_id=USER_ID, # user_id s'utilitza a nivell de runner per a traçabilitat
            session_id=SESSION_ID,
            new_message=user_message_content
        ):
            if event.is_final_response():
                response_from_llm = event.content.parts[0].text.strip()

                if response_from_llm == "SQLAgent":
                    # print("DEBUG: Orchestrator delegando a SQLAgent.") # Opcional para depuración
                    return await execute_sql_agent(query)
                elif response_from_llm == "RAGAgent":
                    # print("DEBUG: Orchestrator delegando a RAGAgent.") # Opcional para depuración
                    return await execute_rag_agent(query)
                else:
                    # print(f"DEBUG: Orchestrator recibió respuesta inesperada del LLM: {response_from_llm}") # Opcional para depuración
                    return f"L'AgenteCoordinador no ha pogut delegar la consulta. Resposta inesperada del model: '{response_from_llm}'."
        # Si no hi ha una final_response, potser hi ha un problema.
        # Això depèn de si el runner.run_async sempre produeix un final_response.
        return "No s'ha obtingut una resposta final de l'AgenteCoordinador."
    except Exception as e:
        # Captura qualsevol excepció durant l'execució del runner
        # print(f"ERROR: [Orchestrator] Falló la ejecución del runner: {e}") # Opcional para depuración
        return f"S'ha produït un error intern a l'AgenteCoordinador: {str(e)}"