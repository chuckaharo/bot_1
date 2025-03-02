FROM python:3.11-slim

WORKDIR /app

ENV PYTHONPATH="${PYTHONPATH}:/app/src"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-u", "src/bot/main.py"]