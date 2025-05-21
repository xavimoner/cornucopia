# agents/merge_comparativa_csv.py
import pandas as pd

# Llegeix els dos fitxers
openai_df = pd.read_csv("openai_result.csv")
gemini_df = pd.read_csv("gemini_result.csv")

# Identificador: nom de camp = columnes
fields = list(openai_df.columns)

rows = []
for field in fields:
    if field == "id" or field == "created_at":
        continue
    task_info = f"[{field}]"
    resposta_openai = openai_df[field][0]
    resposta_gemini = gemini_df[field][0]
    rows.append([field, task_info, resposta_openai, resposta_gemini])

# Guarda com a comparativa
df = pd.DataFrame(rows, columns=["Camp", "Task i Prompt", "Resposta OpenAI", "Resposta Gemini"])
df.to_csv("comparativa_resultats.csv", index=False)
print("CSV comparatiu generat: comparativa_resultats.csv")
