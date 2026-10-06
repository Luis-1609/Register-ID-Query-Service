FROM python:3.11-slim-bookworm

# Evitar prompts interactivos
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar dependencias del sistema necesarias para Playwright
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Instalar librerías de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Instalar navegadores de Playwright con sus dependencias del sistema operativo
RUN playwright install --with-deps chromium

# Copiar el código del proyecto
COPY . .

# Exponer puerto 8080 opcional para callback OAuth inicial
EXPOSE 8080

# Ejecutar el servicio de scheduler en bucle para monitorear Google Sheets
CMD ["python", "scheduler_service.py"]
