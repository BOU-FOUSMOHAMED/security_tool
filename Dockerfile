FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    nmap \
    libcap2-bin && \
    setcap cap_net_raw,cap_net_admin=eip /usr/bin/nmap && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080


CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:8080", "app:app"]