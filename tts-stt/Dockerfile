FROM nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    software-properties-common ca-certificates ffmpeg \
 && add-apt-repository ppa:deadsnakes/ppa \
 && apt-get update && apt-get install -y --no-install-recommends \
    python3.11 python3.11-venv python3.11-distutils \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN python3.11 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN python -m pip install --upgrade pip setuptools wheel

COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY stt_tts.py .
CMD ["python", "stt_tts.py"]