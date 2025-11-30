#!/bin/bash

# Skrypt do uruchomienia aplikacji w trybie deweloperskim
# Automatycznie konfiguruje środowisko i instaluje zależności

set -e  # Zatrzymaj skrypt przy błędzie

VENV_DIR="venv"
PYTHON_CMD="python3"
MAIN_FILE="main.py"
REQUIREMENTS_FILE="requirements.txt"

echo "🔍 Sprawdzanie dostępności Python 3..."
if ! command -v $PYTHON_CMD &> /dev/null; then
    echo "❌ Python 3 nie został znaleziony. Zainstaluj Python 3."
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version)
echo "✅ Znaleziono: $PYTHON_VERSION"

# Sprawdź czy main.py istnieje
if [ ! -f "$MAIN_FILE" ]; then
    echo "❌ Plik $MAIN_FILE nie został znaleziony w bieżącym katalogu."
    exit 1
fi

# Utwórz virtualenv jeśli nie istnieje
if [ ! -d "$VENV_DIR" ]; then
    echo "📦 Tworzenie środowiska wirtualnego..."
    $PYTHON_CMD -m venv $VENV_DIR
    echo "✅ Środowisko wirtualne utworzone"
else
    echo "✅ Środowisko wirtualne już istnieje"
fi

# Aktywuj virtualenv
echo "🔌 Aktywowanie środowiska wirtualnego..."
source $VENV_DIR/bin/activate

# Zaktualizuj pip
echo "⬆️  Aktualizowanie pip..."
pip install --upgrade pip --quiet

# Zainstaluj zależności
if [ -f "$REQUIREMENTS_FILE" ]; then
    echo "📥 Instalowanie zależności z $REQUIREMENTS_FILE..."
    pip install -r $REQUIREMENTS_FILE
    echo "✅ Zależności zainstalowane"
else
    echo "⚠️  Plik $REQUIREMENTS_FILE nie został znaleziony"
    echo "⚠️  Kontynuowanie bez instalacji zależności..."
fi

# Sprawdź czy uvicorn jest zainstalowany
if ! python -m uvicorn --help &> /dev/null; then
    echo "⚠️  Uvicorn nie jest zainstalowany. Instalowanie..."
    pip install uvicorn[standard]
fi

# Uruchom aplikację
echo ""
echo "🚀 Uruchamianie aplikacji FastAPI..."
echo "📍 Aplikacja będzie dostępna pod adresem: http://localhost:8080"
echo "📍 Dokumentacja API: http://localhost:8080/docs"
echo "⏹️  Naciśnij Ctrl+C aby zatrzymać serwer"
echo ""

# Uruchom przez uvicorn (lepsze dla developmentu z auto-reload)
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
