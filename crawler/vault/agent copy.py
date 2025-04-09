# agent.py

from smolagents import TransformersModel

# Crear el modelo Transformers
model = TransformersModel(model_id="Qwen/Qwen2.5-3B-Instruct", device="cpu", base_url="http://vllm:5000/v1")

# Función para consultar al agente
async def query_agent(content, instruction):
    prompt = f"{instruction}\n\nTexto: {content}"
    
    # Realizar la consulta al modelo
    response = await model([{"role": "user", "content": prompt}])

    # Imprimir la respuesta completa para inspeccionarla
    print("Respuesta completa del modelo:", response)
    
    # Verificar la estructura de la respuesta y ajustarla según sea necesario
    try:
        if isinstance(response, dict) and 'choices' in response:
            return response['choices'][0]['message']['content']
        else:
            print("La respuesta no tiene la estructura esperada.")
            return "Error: no se encontró la clave 'choices' en la respuesta."
    except Exception as e:
        return f"Error al acceder a la respuesta: {e}"



