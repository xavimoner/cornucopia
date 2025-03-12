FROM python:3.11-slim

WORKDIR /app

# dependències
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium-driver \
    libxrender1 libxshmfence1 libxcomposite1 libxcb1 \
    && rm -rf /var/lib/apt/lists/*

# Copiar el fitxer de dependències
COPY requirements.txt requirements.txt

# Actualitzar pip, setuptools i wheel per evitar errors de compatibilitat
RUN pip install --upgrade pip setuptools wheel

# dependències
RUN pip install --no-cache-dir -r requirements.txt

#  navegadors per Playwright
RUN playwright install --with-deps


COPY . .


EXPOSE 5001


CMD ["python", "main.py"]
