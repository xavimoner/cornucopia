# ollama/Dockerfile

# Utilitzar la imatge oficial d'Ollama
FROM ollama/ollama

# Copiar el fitxer shell per iniciar Ollama
COPY ./run_ollama.sh /tmp/run_ollama.sh

# Establir el directori de treball
WORKDIR /tmp

# Donar permisos d'execució al fitxer shell
RUN chmod +x run_ollama.sh

# Exposar el port de Ollama
EXPOSE 11434

