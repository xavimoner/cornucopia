# ./vllm/Dockerfile
# Utilitzar una imatge base compatible amb Python 3.12
FROM python:3.12-slim

# Establir directori de treball
WORKDIR /workspace

# Instal·lar dependències bàsiques
RUN apt-get update && apt-get install -y \
    git gcc-12 g++-12 libnuma-dev libtcmalloc-minimal4 \
    && rm -rf /var/lib/apt/lists/*

# Actualitzar alternatives per usar gcc-12
RUN update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-12 10 \
    --slave /usr/bin/g++ g++ /usr/bin/g++-12

# Instal·lar vLLM des de codi font
RUN git clone https://github.com/vllm-project/vllm.git vllm_source && \
    cd vllm_source && \
    pip install --upgrade pip && \
    pip install "cmake>=3.26" wheel packaging ninja "setuptools-scm>=8" numpy && \
    pip install -v -r requirements/cpu.txt --extra-index-url https://download.pytorch.org/whl/cpu && \
    VLLM_TARGET_DEVICE=cpu python setup.py install

# Configurar Hugging Face cache
RUN mkdir -p /root/.cache/huggingface
VOLUME /root/.cache/huggingface

# Instal·lar transformers i altres paquets de Hugging Face
RUN pip install torch transformers huggingface-hub vllm

# Baixar el model DeepSeek-R1-Distill-Qwen-1.5B
RUN python -c "from transformers import AutoModelForCausalLM, AutoTokenizer; \
    AutoModelForCausalLM.from_pretrained('deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B'); \
    AutoTokenizer.from_pretrained('deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B');"

# Exposar el port del servei
EXPOSE 5000

# Comanda per arrencar vLLM
CMD ["vllm", "serve", "--device", "cpu", "--trust-remote-code", "$VLLM_MODEL"]

