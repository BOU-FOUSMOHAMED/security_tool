# FROM alpine:3.20

# RUN apk add --no-cache nmap python3 py3-pip

# WORKDIR /app
# COPY requirements.txt .
# RUN pip install --no-cache-dir "flask>=3.0"

# COPY app.py .

# EXPOSE 5000
# CMD ["python3", "app.py"]
FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y nmap && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]