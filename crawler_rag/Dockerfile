# crawler_rag/Dockerfile
FROM ubuntu:22.04

WORKDIR /app

# Instal·lem dependències bàsiques i pip3
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-venv \
    chromium-driver \
    libxrender1 libxshmfence1 libxcomposite1 libxcb1 \
    git \
    software-properties-common \
    && add-apt-repository universe \
    && apt-get update \
    # && apt-get install -y numactl-dev \
    && rm -rf /var/lib/apt/lists/*

# Crear un entorn virtual
RUN python3 -m venv /venv

# Asegurarem que utilitzem pip3 del nostre entorn virtual
ENV PATH="/venv/bin:$PATH"

# Copiem el fitxer de dependències
COPY requirements.txt requirements.txt

# Actualitzem pip3, setuptools i wheel
RUN pip install --upgrade pip setuptools wheel

# Instal·lem les dependències de Python
RUN pip install --no-cache-dir -r requirements.txt
# RUN pip install smolagents[vllm]
# RUN pip install 'accelerate>=0.26.0'  # Afegir aquesta línia

# Instal·lem Playwright
RUN playwright install --with-deps

# Copiem el codi font
COPY . .

# Exposem el port
EXPOSE 5001

CMD ["python", "main.py"]
