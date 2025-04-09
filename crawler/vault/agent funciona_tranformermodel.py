# /cornucopia/test.py

from smolagents import TransformersModel, tools, 

# Crear el model TransformerModel especificant la URL correcta del servidor vLLM
try:
    print("Intentant carregar el model...")
    model = TransformersModel(model_id="Qwen/Qwen2.5-3B-Instruct", 
                      device="cpu", 
                      base_url="http://vllm:5000/v1",
                      platform="cpu")  # Afegir la configuració explícita de la plataforma
    print("Model carregat correctament.")
    
    # Realitzar una sol·licitud de prova
    response = model([{"role": "user", "content": "Explain quantum mechanics in simple terms."}])
    print("Resposta del model:", response)
except Exception as e:
    print(f"Error carregant el model: {e}")
