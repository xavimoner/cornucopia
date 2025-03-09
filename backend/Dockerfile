# ./backend/Dockerfile

# Utilitzar una imatge de Python optimitzada
FROM python:3.11-slim

WORKDIR /app

# Instal·lar dependències del sistema necessàries
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar el fitxer de dependències
COPY requirements.txt requirements.txt

# Actualitzar pip, setuptools i wheel per evitar errors de compatibilitat
RUN pip install --upgrade pip setuptools wheel

# Instal·lar Torch abans que la resta de dependències, indicant el repositori CPU
RUN pip install --no-cache-dir torch==2.1.2 --index-url https://download.pytorch.org/whl/cpu

# Instal·lar la resta de dependències
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el codi font
COPY . .

# Exposar el port del backend
EXPOSE 8000

# Comando d'inici del servidor FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
