# scripts/test_gemini_curl.py

import os
import requests
import json

# Obtenim la clau API des de les variables d'entorn
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    print("No s'ha trobat la variable d'entorn GEMINI_API_KEY.")
    exit(1)

# Endpoint del model Gemini
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

# Prompt de prova
prompt = "Explica breument com funciona la intel·ligència artificial."

# Cos de la petició
payload = {
    "contents": [{
        "parts": [{"text": prompt}]
    }]
}

# Capçaleres
headers = {"Content-Type": "application/json"}

# Crida a l'API
response = requests.post(f"{GEMINI_URL}?key={API_KEY}", headers=headers, json=payload)

# Tractament de la resposta
if response.status_code == 200:
    data = response.json()
    try:
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        print("Resposta de Gemini:")
        print(text)
    except Exception as e:
        print("Error interpretant la resposta de Gemini:", str(e))
        print(json.dumps(data, indent=2))
else:
    print(f"Error {response.status_code}: {response.text}")
