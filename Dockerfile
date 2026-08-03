FROM alpine:3.20

RUN apk add --no-cache nmap python3 py3-pip

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r flask>=3.0

COPY app.py .

EXPOSE 5000
CMD ["python3", "app.py"]
