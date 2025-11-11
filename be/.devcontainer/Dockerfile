FROM python:3.11-slim

WORKDIR /app

COPY ../requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y make git

RUN git config --global user.name "Ang Leng Khai"
RUN git config --global user.email "lengkhai@gmail.com"

COPY ../app/ ./app/
# COPY ../firebase_key.json ./firebase_key.json

# Bind to the PORT environment variable (Render expects binding to 0.0.0.0:$PORT).
# Use shell form so environment variable expansion works at container runtime.
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
