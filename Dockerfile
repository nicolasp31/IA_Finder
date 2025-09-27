# ------------- Dockerfile -------------
# Imagen base con Python (Debian slim)
FROM python:3.11-slim

# Evitar preguntas interactivas durante apt
ENV DEBIAN_FRONTEND=noninteractive

# 1) Actualizar e instalar exiftool y utilidades mínimas
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libimage-exiftool-perl \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 2) Crear carpeta de la app
WORKDIR /app

# 3) Copiar requirements e instalarlas
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4) Copiar el código
COPY . .

# 5) (Opcional) crear un usuario no-root y cambiar permisos
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# 6) Comando por defecto (ajusta si tu entrypoint es otro)
CMD ["python", "IA_Finder.py"]
# --------------------------------------
