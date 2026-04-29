FROM python:3.12-slim

WORKDIR /app

# Installer system-afhængigheder
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc curl \
    && rm -rf /var/lib/apt/lists/*

# Installer Python-afhængigheder
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiér kode
COPY . .

EXPOSE 8000

# Produktion: gunicorn (startup.txt bruges af Azure App Service)
# Lokal dev: docker-compose overskriver med uvicorn --reload
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", \
     "backend.main:app", "--bind", "0.0.0.0:8000", "--timeout", "120"]
