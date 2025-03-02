FROM python:3.11-slim

WORKDIR /app

ENV PYTHONPATH="${PYTHONPATH}:/app/src"
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt --no-cache-dir

COPY . .

CMD ["python", "-u", "src/bot/main.py"]