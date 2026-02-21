FROM --platform=linux/amd64 python:3.11-slim

WORKDIR /app

# Kopiuj pliki wymagane
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiuj pliki aplikacji
COPY main.py .
COPY index.html .
# Logo w static_files – aplikacja serwuje pliki statyczne z tego folderu
COPY decent-code-1024x0.png static_files/
# badania.csv jest wczytywany z Google Cloud Storage bucket "hipokrates"
# COPY badania.csv .  # Opcjonalnie dla lokalnego fallback

# Uruchom aplikację
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]

