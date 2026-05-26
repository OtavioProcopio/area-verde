FROM mcr.microsoft.com/devcontainers/python:3.11

RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    vim \
    inetutils-ping \
    telnet \
    curl \
    gcc \
    python3-dev && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip

COPY app/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt || echo "Requirements not found yet"
