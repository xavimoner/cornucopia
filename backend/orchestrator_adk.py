# backend/orchestrator_adk.py

from agents.orchestrator_agent_adk import execute_orchestrator_agent
# Si 'main.py' ja defineix l'aplicació FastAPI i l'endpoint /chat,
# aquest arxiu 'orchestrator_adk.py' només necessita la funció handle_chat.
# Per claredat, el que s'executa a 'main.py' hauria de ser el punt d'entrada de FastAPI.

async def handle_chat(query: str):
    """
    Gestiona una consulta de xat enviant-la a l'agent orquestrador.
    Aquesta funció és un connector entre l'endpoint de FastAPI (main.py)
    i la lògica de l'agent orquestrador.
    """
    return {"respuesta": await execute_orchestrator_agent(query)}
