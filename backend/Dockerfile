# backend/Dockerfile
FROM ubuntu:22.04

ENV PYTHON_VERSION=3.10
ENV VENV_PATH=/opt/backend-venv
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive
ENV PIP_NO_CACHE_DIR=on
ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV PYTHONUNBUFFERED=1

# configuració d'OpenSSL abans d'apt-get update
# arxiu de config:  backend/config/openssl_custom.cnf
COPY ./config/openssl_custom.cnf /etc/ssl/openssl_custom.cnf 

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python${PYTHON_VERSION} \
    python${PYTHON_VERSION}-venv \
    python3-pip \
    python3-dev \
    libpq-dev \
    gcc \
    curl \
    netcat-openbsd \
    postgresql-client \
    libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 libgbm1 \
    libasound2 libpangocairo-1.0-0 libx11-6 libx11-xcb1 libxcb1 \
    libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 \
    libxi6 libxrandr2 libxrender1 libxss1 libxtst6 libglib2.0-0 \
    libfontconfig1 libfreetype6 \
    && \
    # Modifica la configuració global d'OpenSSL + directiva .include
    echo "" >> /etc/ssl/openssl.cnf && \ 

    echo ".include /etc/ssl/openssl_custom.cnf" >> /etc/ssl/openssl.cnf && \
    rm -rf /var/lib/apt/lists/*
RUN python${PYTHON_VERSION} -m venv ${VENV_PATH}
ENV PATH="${VENV_PATH}/bin:$PATH"
RUN pip install --upgrade pip setuptools wheel

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt --timeout 120

RUN playwright install --with-deps chromium

COPY . .
ENV PYTHONPATH=/app

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]