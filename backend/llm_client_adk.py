# backend/llm_client_adk.py

import os
from google.adk.models.lite_llm import LiteLlm # Eina ADK per a LiteLLM

# Nota: La importació de google.adk.models.gemini.Gemini no s'utilitza actualment.

def get_lite_llm():
    """
    Obtenir instància LiteLlm segons proveïdor a .env.
    """
    provider = os.getenv("LLM_PROVIDER", "OPENAI").upper() # Proveïdor LLM per defecte: OPENAI

    if provider == "GEMINI":
        gemini_model_name = os.getenv("GEMINI_MODEL") # Nom model Gemini (ex: gemini-1.5-flash-latest)
        if not gemini_model_name:
            raise ValueError("Variable d'entorn GEMINI_MODEL no definida. Necessària per a Gemini.")
        
        # Assegurar format nom model per LiteLlm (generalment "gemini/nom-model")
        # LiteLlm pot esperar el prefix del proveïdor.
        # Eliminem "models/" si l'usuari l'ha inclòs per error.
        if gemini_model_name.startswith("models/"):
            gemini_model_name = gemini_model_name.replace("models/", "")
        
        model_string_for_litellm = f"gemini/{gemini_model_name}"
        print(f"INFO [LLM_Client_ADK]: Configurant LiteLlm per a Gemini amb model: {model_string_for_litellm}")
        return LiteLlm(model_string_for_litellm)
    
    elif provider == "DEEPSEEK":
        deepseek_model_name = os.getenv("DEEPSEEK_MODEL") # Nom model DeepSeek (ex: deepseek-chat)
        if not deepseek_model_name:
            raise ValueError("Variable d'entorn DEEPSEEK_MODEL no definida. Necessària per a DeepSeek.")
        
        model_string_for_litellm = f"deepseek/{deepseek_model_name}"
        print(f"INFO [LLM_Client_ADK]: Configurant LiteLlm per a DeepSeek amb model: {model_string_for_litellm}")
        return LiteLlm(model_string_for_litellm)
    
    elif provider == "OPENAI": # Per a Azure OpenAI o OpenAI directe via LiteLLM
        # Prioritza el nom del desplegament d'Azure si està definit
        openai_model_name = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT") or os.getenv("OPENAI_MODEL")
        if not openai_model_name:
            raise ValueError("Variables d'entorn AZURE_OPENAI_CHAT_DEPLOYMENT o OPENAI_MODEL no definides. Necessàries per a OpenAI.")
        
        # Recordar! Azure, LiteLlm sovintespera "azure/nom"
        # OpenAI directe, "openai/gpt-4o" .
        # Si AZURE_OPENAI_CHAT_DEPLOYMENT ja conté el prefix "azure/", LiteLlm podria gestionar-ho.
        
        
        model_string_for_litellm = openai_model_name # Intentem primer amb el nom directe
        if os.getenv("AZURE_OPENAI_ENDPOINT"): # Si hi ha endpoint d'Azure, és probable que sigui Azure
             model_string_for_litellm = f"azure/{openai_model_name}" # Format comú per a Azure amb LiteLlm
        else: # Si no, podria ser OpenAI directe
             model_string_for_litellm = f"openai/{openai_model_name}"

        print(f"INFO [LLM_Client_ADK]: Configurant LiteLlm per a OpenAI/Azure amb model string: {model_string_for_litellm}")
        return LiteLlm(model_string_for_litellm)
    
    else:
        raise ValueError(f"Proveedor LLM_PROVIDER '{provider}' no reconocido o no soportado.")