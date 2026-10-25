FROM python:3.13-slim-bookworm

WORKDIR /app

COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

CMD ["fastapi", "dev", "app/main.py", "--host", "0.0.0.0", "--port", "5000"]
