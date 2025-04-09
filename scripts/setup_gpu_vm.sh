#!/bin/bash
# scripts/setup_gpu_vm.sh

# Actualitza paquets i instal·la docker
sudo apt-get update && sudo apt-get install -y \
    docker.io docker-compose git curl

# Instal·la el NVIDIA Container Toolkit per suport GPU
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
    sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker

# Comprova que la GPU està visible
docker run --rm --gpus all nvidia/cuda:12.1.1-base-ubuntu22.04 nvidia-smi

# Clona el projecte Cornucopia (si no ho has fet)
git clone https://github.com/xavimoner/cornucopia.git
cd cornucopia

# Executa el sistema amb GPU (vllm + resta de serveis)
docker compose up --build -d
