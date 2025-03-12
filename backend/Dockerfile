# ./backend/Dockerfile


FROM python:3.11-slim

WORKDIR /app


RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc \
    netcat-openbsd  # Canviar 'netcat' per 'netcat-openbsd' \
    && rm -rf /var/lib/apt/lists/*

# Instalar les dependències necessàries per a la compilació de psycopg2
RUN apt-get update && apt-get install -y \
libpq-dev \
gcc \
python3-dev \
&& rm -rf /var/lib/apt/lists/*



COPY requirements.txt requirements.txt


RUN pip install --upgrade pip setuptools wheel


# RUN pip install --no-cache-dir torch==2.1.2 --index-url https://download.pytorch.org/whl/cpu


RUN pip install --no-cache-dir -r requirements.txt


COPY . .

ENV PYTHONPATH=/app


EXPOSE 8000


CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
