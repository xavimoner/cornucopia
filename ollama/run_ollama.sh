#!/bin/bash
# ollama/run_ollama.sh
# Mostrar missatge per indicar que Ollama s'està iniciant
echo "Starting Ollama server..."

# Iniciar el servidor Ollama en segon pla
ollama serve &

# Executar un model específic
ollama run Qwen/Qwen2.5-7B-Instruct-1M

# Esperar que Ollama estigui actiu
echo "Waiting for Ollama server to be active..."
while [ "$(ollama list | grep 'NAME')" == "" ]; do
  sleep 1
done

echo "Ollama server is up and running!"
