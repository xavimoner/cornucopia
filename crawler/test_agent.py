# test_agent.py

from agent_extractor import query_agent  # Importamos la función query_agent desde agent_extractor.py

# Texto de prueba corto para enviar al agente
sample_text = """
La subvención está destinada a fomentar la investigación en energías renovables. El proyecto debe tener una duración mínima de 1 año y máxima de 5 años. El presupuesto mínimo financiable será de 175.000 €, con una intensidad de subvención del 50%. Los beneficiarios de la subvención son empresas que operen en el sector de la energía.
"""

# Instrucción que le pasa al agente para buscar información
instruction = "Buscar el presupuesto mínimo financiable y la intensidad de la subvención."

# Función para probar el agente
def test_agent():
    try:
        # Realizar la consulta al agente
        result = query_agent(sample_text, instruction)
        print("Resultado de la consulta:", result)
    except Exception as e:
        print(f"Error al consultar al agente: {e}")

# Ejecutar la función test_agent
if __name__ == "__main__":
    test_agent()
