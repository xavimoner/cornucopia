# crawler_rag/eagents/xtraction_tasks.py

# Diccionari amb tots els prompts, field, descripció per cada camp.

# crawler_rag/agents/extraction_tasks.py

"""
Conté les instruccions (prompts) per a cada camp a extreure d’una convocatòria.
Cada entrada defineix:
- field: nom del camp a la base de dades
- description: descripció breu de què s'ha d'extreure
- prompt: instrucció que s'enviarà al LLM
"""

EXTRACTION_TASKS = [
    {
        "field": "objetivo",
        "description": "Objectiu principal de la convocatòria",
        "prompt": """Eres un agente de extracción de información. Tu tarea consiste en identificar el objetivo principal de la convocatoria.

Busca frases que indiquen finalidades como:
- fomentar la innovación
- impulsar actividades de I+D
- mejorar la competitividad
- apoyar el desarrollo tecnológico
- facilitar la transferencia de tecnología

Devuelve solo el párrafo exacto que lo exprese, sin resúmenes ni explicaciones."""
    },
    {
        "field": "beneficiarios",
        "description": "Quién puede solicitar la ayuda",
        "prompt": """Eres un agente de extracción de información. Tu tarea consiste en identificar qué tipo de entidades pueden ser beneficiarias de esta convocatoria.

Busca frases que mencionen:
- pymes, empresas, organismos de investigación
- consorcios, universidades, autónomos
- sectores o condiciones específicas

Devuelve únicamente el párrafo literal donde se mencione esta información."""
    },
    {
        "field": "linea",
        "description": "Línea o tipo de proyecto financiado",
        "prompt": """Eres un agente de extracción de información. Tu tarea consiste en identificar la línea o tipología del proyecto de la convocatoria.

Busca si se trata de:
- proyectos individuales
- proyectos cooperativos
- proyectos en consorcio
- proyectos colaborativos

Devuelve solo el párrafo literal donde se indique esta clasificación."""
    }
]
