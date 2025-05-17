# backend/llm_client_adk.py

import os
# The tutorial uses google.adk.models.lite_llm.LiteLlm directly [cite: 1]
from google.adk.models.lite_llm import LiteLlm 

# Ensure the correct base client is imported for direct Gemini usage if LiteLlm has issues
# from google.adk.models.gemini import Gemini  # Not used in your current setup, but good to know

def get_lite_llm():
    provider = os.getenv("LLM_PROVIDER", "OPENAI").upper()

    if provider == "GEMINI":
        gemini_model_name = os.getenv("GEMINI_MODEL")
        if not gemini_model_name:
            raise ValueError("La variable d'entorn GEMINI_MODEL no està definida. Si uses Gemini, és necessària.")
        
        # Correction: Ensure model name is in the format expected by LiteLlm for Gemini.
        # LiteLlm often expects "gemini/gemini-1.5-flash" or just "gemini-1.5-flash" 
        # not "models/gemini-1.5-flash-preview-04-17" directly from Google's GenAI package.
        # It's best to check LiteLlm's specific documentation for the exact format.
        # For robustness, let's remove "models/" if it exists.
        if gemini_model_name.startswith("models/"):
            gemini_model_name = gemini_model_name.replace("models/", "")
        
        return LiteLlm(f"gemini/{gemini_model_name}") # LiteLlm might expect provider prefix
    
    elif provider == "DEEPSEEK":
        deepseek_model_name = os.getenv("DEEPSEEK_MODEL")
        if not deepseek_model_name:
            raise ValueError("La variable d'entorn DEEPSEEK_MODEL no està definida. Si uses DeepSeek, és necessària.")
        # LiteLlm for DeepSeek usually expects "deepseek/deepseek-chat"
        return LiteLlm(f"deepseek/{deepseek_model_name}")
    
    elif provider == "OPENAI":
        openai_model_name = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT") or os.getenv("OPENAI_MODEL")
        if not openai_model_name:
            raise ValueError("La variable d'entorn AZURE_OPENAI_CHAT_DEPLOYMENT (o OPENAI_MODEL) no està definida. Si uses OpenAI, és necessària.")
        # LiteLlm for OpenAI/Azure OpenAI usually expects "openai/gpt-4o" or specific deployment name
        # If AZURE_OPENAI_CHAT_DEPLOYMENT is a direct deployment name, it might be just that.
        # For robustnes, let's assume it should follow the `provider/model_name` format.
        return LiteLlm(f"openai/{openai_model_name}") # Or just LiteLlm(openai_model_name) depending on deployment config
    
    else:
        raise ValueError(f"Model LLM_PROVIDER '{provider}' no reconegut.")