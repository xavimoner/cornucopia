# backend/agents/sql_agent.py

from google.adk.agents import Agent
from llm_client_adk import get_lite_llm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

sql_agent = Agent(
    name="SQLAgent",
    model=get_lite_llm(),
    description="Agent especialitzat en consultes SQL per a subvencions.",
    instruction="""
Ets un agent que respon a preguntes sobre subvencions utilitzant dades estructurades.
Només has de contestar si la pregunta pot ser resolta amb una consulta SQL.
Respon sempre amb l'string literal de la consulta SQL o amb la dada si ja tens accés directe.
""",
)

session_service = InMemorySessionService() # Instància separada de session_service
runner = Runner(
    agent=sql_agent,
    app_name="sql_agent_app",
    session_service=session_service
)

USER_ID = "user_sql_001" # ID d'usuari propi per a SQLAgent
SESSION_ID = "session_sql_main" # ID de sessió propi per a SQLAgent

async def execute_sql_agent(query: str):
    user_message_content = types.Content(role="user", parts=[types.Part(text=query)])

    # MODIFICACIÓ CLAU: Assegurar-se que la sessió existeix per a SQLAgent
    session = await session_service.get_session(SESSION_ID)
    if not session:
        session = await session_service.create_session(SESSION_ID)
        # print(f"DEBUG: [SQLAgent] Sesión '{SESSION_ID}' creada.") # Opcional para depuración
    # else:
        # print(f"DEBUG: [SQLAgent] Sesión '{SESSION_ID}' encontrada.") # Opcional para depuración

    try:
        async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=user_message_content):
            if event.is_final_response():
                return event.content.parts[0].text
        # Si no hi ha una final_response
        return "No s'ha obtingut una resposta final del SQLAgent."
    except Exception as e:
        # print(f"ERROR: [SQLAgent] Falló la ejecución del runner: {e}") # Opcional para depuración
        return f"S'ha produït un error intern al SQLAgent: {str(e)}"