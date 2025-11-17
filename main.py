from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, validator
import csv
import os
import io
from typing import List, Dict, Optional

app = FastAPI()

# CORS middleware dla lokalnego developmentu
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """Obsługa błędów walidacji z bardziej czytelnymi komunikatami"""
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error.get("loc", []))
        msg = error.get("msg", "Błąd walidacji")
        errors.append(f"{field}: {msg}")
    return JSONResponse(
        status_code=422,
        content={"detail": "; ".join(errors)}
    )

# Konfiguracja Google Cloud Storage
BUCKET_NAME = "hipokrates"
CSV_FILE_NAME = "badania.csv"
CSV_FILE = "badania.csv"  # Dla lokalnego fallback

def get_storage_client():
    """Zwraca klienta Google Cloud Storage lub None jeśli nie jest dostępny"""
    try:
        from google.cloud import storage
        return storage.Client()
    except Exception:
        return None

def parse_price(price_str: str) -> float:
    """Konwertuje cenę z formatu '2,00' na float"""
    if not price_str or price_str.strip() == "":
        return 0.0
    # Zamień przecinek na kropkę i usuń białe znaki
    price_str = price_str.strip().replace(",", ".")
    try:
        return float(price_str)
    except ValueError:
        return 0.0

def load_badania() -> List[Dict]:
    """Wczytuje dane z pliku CSV z Google Cloud Storage lub lokalnie"""
    badania = []
    csv_content = None
    
    # Próbuj pobrać z Google Cloud Storage
    storage_client = get_storage_client()
    if storage_client:
        try:
            bucket = storage_client.bucket(BUCKET_NAME)
            blob = bucket.blob(CSV_FILE_NAME)
            csv_content = blob.download_as_text(encoding='utf-8')
        except Exception as e:
            print(f"Błąd podczas pobierania z Cloud Storage: {e}")
            # Fallback do lokalnego pliku
    
    # Jeśli nie udało się pobrać z Cloud Storage, spróbuj lokalnie
    if csv_content is None:
        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, 'r', encoding='utf-8') as f:
                csv_content = f.read()
        else:
            return badania
    
    # Parsuj CSV
    csv_io = io.StringIO(csv_content)
    reader = csv.DictReader(csv_io, delimiter=';')
    for row in reader:
        kod = row.get('KOD', '').strip()
        nazwa = row.get('NAZWA BADANIA', '').strip()
        kwota_str = row.get('KWOTA', '').strip()
        kwota = parse_price(kwota_str)
        
        if nazwa:  # Tylko badania z nazwą
            badania.append({
                'kod': kod,
                'nazwa': nazwa,
                'kwota': kwota,
                'kwota_str': kwota_str
            })
    
    return badania

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Zwraca stronę główną"""
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/api/login")
async def login(request: Request):
    """Weryfikuje hasło"""
    data = await request.json()
    password = data.get("password", "")
    
    if password == "hipokrates":
        return {"success": True}
    else:
        raise HTTPException(status_code=401, detail="Nieprawidłowe hasło")

@app.get("/api/badania")
async def get_badania():
    """Zwraca wszystkie badania posortowane alfabetycznie"""
    badania = load_badania()
    # Sortuj alfabetycznie po nazwie
    badania_sorted = sorted(badania, key=lambda x: x['nazwa'].lower())
    return {"badania": badania_sorted}

@app.post("/api/search")
async def search_badania(request: Request):
    """Wyszukuje badania po nazwie"""
    data = await request.json()
    query = data.get("query", "").strip().lower()
    
    if not query:
        return {"badania": []}
    
    wszystkie_badania = load_badania()
    # Wyszukiwanie case-insensitive
    results = [
        badanie for badanie in wszystkie_badania
        if query in badanie['nazwa'].lower()
    ]
    
    return {"badania": results}

def load_full_csv() -> List[Dict]:
    """Wczytuje pełne dane CSV (wszystkie wiersze)"""
    csv_content = None
    
    # Próbuj pobrać z Google Cloud Storage
    storage_client = get_storage_client()
    if storage_client:
        try:
            bucket = storage_client.bucket(BUCKET_NAME)
            blob = bucket.blob(CSV_FILE_NAME)
            csv_content = blob.download_as_text(encoding='utf-8')
        except Exception as e:
            print(f"Błąd podczas pobierania z Cloud Storage: {e}")
    
    # Jeśli nie udało się pobrać z Cloud Storage, spróbuj lokalnie
    if csv_content is None:
        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, 'r', encoding='utf-8') as f:
                csv_content = f.read()
        else:
            return []
    
    # Parsuj CSV
    csv_io = io.StringIO(csv_content)
    reader = csv.DictReader(csv_io, delimiter=';')
    return list(reader)

@app.get("/api/badania/edit")
async def get_badania_for_edit():
    """Zwraca wszystkie badania do edycji"""
    badania = load_full_csv()
    # Konwertuj nazwy kolumn dla frontendu
    result = []
    for row in badania:
        result.append({
            'KOD': row.get('KOD', ''),
            'NAZWA_BADANIA': row.get('NAZWA BADANIA', ''),
            'KWOTA': row.get('KWOTA', ''),
            'KWOTA_2': row.get('KWOTA 2', '')
        })
    return {"badania": result}

class BadanieRow(BaseModel):
    KOD: str
    NAZWA_BADANIA: str
    KWOTA: str
    KWOTA_2: Optional[str] = ""

    @validator('KOD', pre=True)
    def validate_kod(cls, v):
        if v is None or (isinstance(v, str) and not v.strip()):
            return ""
        v = str(v).strip()
        if not v:
            return ""
        try:
            kod_int = int(v)
            if kod_int < 0:
                raise ValueError("KOD musi być liczbą całkowitą >= 0")
            return str(kod_int)
        except (ValueError, TypeError):
            raise ValueError("KOD musi być liczbą całkowitą")

    @validator('NAZWA_BADANIA', pre=True)
    def validate_nazwa(cls, v):
        if v is None:
            return ""
        nazwa = str(v).strip()
        if '\n' in nazwa or '\r' in nazwa:
            raise ValueError("Nazwa badania nie może zawierać znaków końca linii")
        return nazwa

    @validator('KWOTA', pre=True)
    def validate_kwota(cls, v):
        if v is None or (isinstance(v, str) and not v.strip()):
            return ""
        kwota_str = str(v).strip().replace(",", ".")
        if not kwota_str:
            return ""
        try:
            kwota = float(kwota_str)
            if kwota < 0 or kwota > 10000:
                raise ValueError("Kwota musi być w przedziale od 0 do 10000")
            return kwota_str.replace(".", ",")
        except (ValueError, TypeError) as e:
            if "could not convert" in str(e).lower() or "invalid literal" in str(e).lower():
                raise ValueError("Kwota musi być liczbą")
            raise

class BadaniaUpdate(BaseModel):
    badania: List[BadanieRow]

@app.post("/api/badania/save")
async def save_badania(data: BadaniaUpdate):
    """Zapisuje badania do Cloud Storage"""
    try:
        # Filtruj puste wiersze (bez nazwy badania)
        valid_badania = [row for row in data.badania if row.NAZWA_BADANIA and row.NAZWA_BADANIA.strip()]
        
        # Walidacja unikalności KOD (tylko dla niepustych kodów)
        kody = [row.KOD for row in valid_badania if row.KOD and row.KOD.strip()]
        if len(kody) != len(set(kody)):
            raise HTTPException(status_code=400, detail="KOD musi być unikalny dla każdego badania")
        
        # Przygotuj dane do zapisu
        output = io.StringIO()
        writer = csv.writer(output, delimiter=';')
        
        # Nagłówek
        writer.writerow(['KOD', 'NAZWA BADANIA', 'KWOTA', 'KWOTA 2'])
        
        # Wiersze danych
        for row in valid_badania:
            writer.writerow([
                row.KOD or "",
                row.NAZWA_BADANIA or "",
                row.KWOTA or "",
                row.KWOTA_2 or ""
            ])
        
        csv_content = output.getvalue()
        
        # Zapisz do Cloud Storage
        storage_client = get_storage_client()
        if not storage_client:
            raise HTTPException(status_code=500, detail="Google Cloud Storage nie jest dostępny")
        
        try:
            bucket = storage_client.bucket(BUCKET_NAME)
            blob = bucket.blob(CSV_FILE_NAME)
            blob.upload_from_string(csv_content, content_type='text/csv')
            return {"success": True, "message": "Dane zostały zapisane"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Błąd podczas zapisu: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Błąd walidacji: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

