# agent_extractor.py

from smolagents import HfApiModel

# Crear el modelo de Hugging Face API (sin 'base_url')
model = HfApiModel(model_id="Qwen/Qwen2.5-3B-Instruct")  # Ya no es necesario pasar base_url

# Función para consultar al agente
def query_agent(content, instruction):
    prompt = f"{instruction}\n\nTexto: {content}"
    print("Prompt enviado al modelo:", prompt)

    # Realizar la consulta al modelo de forma síncrona
    response = model([{"role": "user", "content": prompt}])

    # Imprimir la respuesta completa para inspeccionarla
    print("Respuesta completa del modelo:", response)
    '''
    # Verificar la respuesta
    try:
        if isinstance(response, dict) and 'choices' in response:
            # Extract the content directly from the response
            message_content = response['choices'][0]['message']['content']
            return message_content
        else:
            # Si la respuesta no tiene la estructura esperada, devolver el contenido completo
            print("La respuesta no tiene la estructura esperada.")
            return response  # Devolvemos la respuesta tal cual
    except Exception as e:
        print(f"Error al acceder a la respuesta: {e}")
        return f"Error al procesar la respuesta: {e}"'
    '''
