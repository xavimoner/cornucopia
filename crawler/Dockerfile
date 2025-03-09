FROM python:3.11-slim

WORKDIR /app

# Instal·lar dependències del sistema necessàries
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium-driver \
    libxrender1 libxshmfence1 libxcomposite1 libxcb1 \
    && rm -rf /var/lib/apt/lists/*

# Copiar el fitxer de dependències
COPY requirements.txt requirements.txt

# Actualitzar pip, setuptools i wheel per evitar errors de compatibilitat
RUN pip install --upgrade pip setuptools wheel

# Instal·lar les dependències
RUN pip install --no-cache-dir -r requirements.txt

# Instal·lar els navegadors per Playwright
RUN playwright install --with-deps

# Copiar el codi font de l'aplicació
COPY . .

# Exposar el port
EXPOSE 5001

# Comando d'inici
CMD ["python", "main.py"]
