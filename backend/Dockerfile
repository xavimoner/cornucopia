# backend/Dockerfile

FROM ubuntu:22.04

# Configurar el directori de treball
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

# Crear entorn virtual i configurar el PATH
RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"

# Assegurar-se que `pip` està actualitzat
RUN pip install --upgrade pip setuptools wheel --timeout 120 --no-cache-dir

# 🔹 Instal·lar `torch` **només per CPU** abans de `requirements.txt`
RUN pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu torch==2.6.0 --timeout 120

# 🔹 Configurar `accelerate` per CPU abans d’instal·lar-lo
# RUN python -c "from accelerate.utils import write_basic_config; write_basic_config(mixed_precision='fp16', compute_environment='LOCAL_MACHINE', use_cpu=True)"

# 🔹 Instal·lar `accelerate` després de configurar-lo
RUN pip install --no-cache-dir "accelerate>=0.26.0" --no-deps --timeout 120

# 🔹 Copiar i instal·lar `requirements.txt` (sense `torch` ni `accelerate`)
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt --timeout 120

# Copiar el codi font
COPY . .

# Definir la variable d'entorn per al PYTHONPATH
ENV PYTHONPATH=/app

# Exposar el port 8000 per a la connexió de l'API
EXPOSE 8000

# Comanda per iniciar l'aplicació
CMD ["/venv/bin/uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
