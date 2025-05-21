# crawler_rag/Dockerfile
FROM ubuntu:22.04

WORKDIR /app

RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-venv \
    cron \
    netcat-openbsd \
    chromium-driver libxrender1 libxshmfence1 libxcomposite1 libxcb1 git software-properties-common \
    && add-apt-repository --yes universe \
    && apt-get update \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install --with-deps

# Copia tot, incloent scripts/ i agents/
COPY . . 

RUN mkdir -p /app/logs # Crea el directori de logs
RUN chmod -R 777 /app/logs # Dóna permisos amplis als logs (considera permisos més restrictius si cal)

# Dóna permisos d'execució als scripts de shell
RUN chmod +x /app/scripts/entrypoint.sh
RUN chmod +x /app/scripts/run_pending_extraction.sh

# Configura cron
COPY scripts/extraction_crontab /etc/cron.d/cornucopia-extraction-cron 
RUN chmod 0644 /etc/cron.d/cornucopia-extraction-cron
# RUN crontab /etc/cron.d/cornucopia-extraction-cron # Normalment no és necessari, cron llegeix de /etc/cron.d

EXPOSE 5001 

ENTRYPOINT ["/app/scripts/entrypoint.sh"]
CMD ["python", "main.py"]