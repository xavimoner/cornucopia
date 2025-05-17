# backend/agents/rag_agent.py
from google.adk.agents import Agent
from llm_client_adk import get_lite_llm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

rag_agent = Agent(
    name="RAGAgent",
    model=get_lite_llm(),
    description="Agent per a consultes obertes utilitzant RAG.",
    instruction="""
Ets un agent que llegeix informació rellevant de textos llargs relacionats amb subvencions.
Quan reps una pregunta oberta, contextual o conceptual, utilitza el context per generar una resposta útil i clara.
""",
)

session_service = InMemorySessionService() # Instància separada de session_service
runner = Runner(
    agent=rag_agent,
    app_name="rag_agent_app",
    session_service=session_service
)

USER_ID = "user_rag_001" # ID d'usuari propi per a RAGAgent
SESSION_ID = "session_rag_main" # ID de sessió propi per a RAGAgent

async def execute_rag_agent(query: str):
    user_message_content = types.Content(role="user", parts=[types.Part(text=query)])

    # MODIFICACIÓ CLAU: Assegurar-se que la sessió existeix per a RAGAgent
    session = await session_service.get_session(SESSION_ID)
    if not session:
        session = await session_service.create_session(SESSION_ID)
        # print(f"DEBUG: [RAGAgent] Sesión '{SESSION_ID}' creada.") # Opcional para depuración
    # else:
        # print(f"DEBUG: [RAGAgent] Sesión '{SESSION_ID}' encontrada.") # Opcional para depuración
    
    try:
        async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=user_message_content):
            if event.is_final_response():
                return event.content.parts[0].text
        # Si no hi ha una final_response
        return "No s'ha obtingut una resposta final del RAGAgent."
    except Exception as e:
        # print(f"ERROR: [RAGAgent] Falló la ejecución del runner: {e}") # Opcional para depuración
        return f"S'ha produït un error intern al RAGAgent: {str(e)}"