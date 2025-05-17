# backend/Dockerfile

FROM ubuntu:22.04

# Definir directori de treball
WORKDIR /app

# Instal·lar dependències del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    libpq-dev \
    gcc \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Crear i activar entorn virtual
RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"

# Actualitzar pip i eines bàsiques
RUN pip install --upgrade pip setuptools wheel --timeout 120 --no-cache-dir

# Instal·lar PyTorch per CPU
RUN pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu torch==2.6.0 --timeout 120

# Instal·lar accelerate (opcional si utilitzes models amb Hugging Face)
RUN pip install --no-cache-dir "accelerate>=0.26.0" --no-deps --timeout 120

# Copiar requirements.txt i instal·lar dependències
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --timeout 120

# Copiar codi font del backend
COPY . .

# Definir variable d'entorn pel PYTHONPATH
ENV PYTHONPATH=/app

# Exposar port FastAPI
EXPOSE 8000

# Comanda per defecte
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

