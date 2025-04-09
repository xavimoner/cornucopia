# /cornucopia/test.py

from openai import OpenAI

# Configura el client OpenAI per a connectar-se al servidor vLLM
client = OpenAI(base_url="http://vllm:5000/v1", api_key="no-api-key-needed")

# Verifica si el model respon correctament
response = client.chat.completions.create(
    model="Qwen/Qwen2.5-3B-Instruct",  # Nom del model que està servint vLLM
    messages=[{"role": "user", "content": "Explain quantum mechanics in simple terms."}],
    max_tokens=50  # Limita la resposta a 50 tokens
)

print(response.choices[0].message.content)