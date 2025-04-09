# extractor/extractor.py

from smolagents import VLLMModel

# Diccionario de instrucciones para cada campo
instrucciones = {
    "presupuesto_minimo": "Buscar el presupuesto mínimo, ya sea directo o financiable, expresar si es financiable y la cantidad.",
    "nombre": "Buscar el nombre del proyecto o convocatoria.",
    "fecha_inicio": "Buscar la fecha de inicio de la convocatoria o del proyecto.",
    "fecha_fin": "Buscar la fecha de fin de la convocatoria o del proyecto.",
    "beneficiarios": "Buscar a qué tipo de beneficiarios está dirigida la convocatoria.",
    "area": "Buscar el área o ámbito al que pertenece el proyecto o convocatoria.",
    "intensidad_de_subvención": "Buscar el porcentaje de subvención o la ayuda máxima que puede recibir cada beneficiario.",
    "tipo_financiacion": "Identificar si la financiación es en forma de subvención, préstamo, o ambas.",
    "criterios_valoración": "Buscar los criterios de valoración para la evaluación del proyecto o convocatoria.",
    "documentacion_solicitud": "Identificar la documentación necesaria para presentar la solicitud."
}

# Crear el modelo vLLM
model = VLLMModel(model_id="Qwen/Qwen2.5-3B-Instruct")

# Función para procesar el contenido con el modelo
async def process_data(content: str, title_variable_map: dict):
    # Crear el mensaje para el modelo, incluyendo las instrucciones y el contenido
    messages = [
        {
            "role": "user",
            "content": f"Extrae los siguientes datos de la siguiente convocatoria de subvención:\n{str(instrucciones)}\n\n{content}"
        }
    ]
    
    # Realizar la consulta
    response = model(messages, stop_sequences=["END"])

    # Mostrar la respuesta
    print("Variables extraídas:", response)
    return response
