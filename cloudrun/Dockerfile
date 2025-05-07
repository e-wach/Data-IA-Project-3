FROM python:3.10-slim

WORKDIR /app

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Puerto de Cloud Run
ENV PORT 8080
EXPOSE 8080

# Comando de inicio
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "teams_games:app"]