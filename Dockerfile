FROM python:3.11-slim

WORKDIR /app

# Kopiuj pliki wymagane
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiuj pliki aplikacji
COPY main.py .
COPY index.html .
# badania.csv jest wczytywany z Google Cloud Storage bucket "hipokrates"
# COPY badania.csv .  # Opcjonalnie dla lokalnego fallback

# Uruchom aplikację
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]

