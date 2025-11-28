FROM python:3.10-slim

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip setuptools wheel

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-hf.txt .

RUN pip install --no-cache-dir \
    --prefer-binary \
    --default-timeout=15000 \
    --retries 10 \
    -r requirements-hf.txt

COPY . .

RUN mkdir -p pdf_references chroma_db
RUN chmod +x /app/start.sh

EXPOSE 7860

HEALTHCHECK --interval=60s --timeout=10s --start-period=180s --retries=5 \
    CMD curl -f http://localhost:7860/healthz || exit 1

CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:7860", "main:app"]
