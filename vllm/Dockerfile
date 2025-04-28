# vllm/Dockerfile
FROM nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04

WORKDIR /workspace

RUN apt-get update && apt-get install -y \
    git gcc g++ libnuma-dev libtcmalloc-minimal4 \
    python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

ENV VLLM_CACHE_DIR=/root/.cache/huggingface

RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"

RUN pip install --upgrade pip && \
    pip install torch --index-url https://download.pytorch.org/whl/cu121 && \
    pip install "cmake>=3.26" wheel packaging ninja "setuptools-scm>=8" numpy

RUN git clone https://github.com/vllm-project/vllm.git vllm_source && \
    cd vllm_source && \
    pip install -r requirements.txt && \
    VLLM_TARGET_DEVICE=cuda python setup.py install

RUN pip install vllm transformers huggingface-hub

EXPOSE 5000

CMD ["vllm", "serve", "--device", "cuda", "--model", "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B", "--trust-remote-code", "--port", "5000", "--max-model-len", "4096", "--dtype", "float16"]
