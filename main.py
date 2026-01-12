from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel, validator
import csv
import os
import io
import secrets
import time
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import pytz
from collections import defaultdict

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Utwórz folder dla plików statycznych jeśli nie istnieje
STATIC_DIR = "static_files"
os.makedirs(STATIC_DIR, exist_ok=True)

# Serwuj pliki statyczne tylko z dedykowanego folderu
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# CORS middleware - tylko dla domeny produkcyjnej
ALLOWED_ORIGINS = [
    "https://badania.decentcode.pl",
    "https://www.badania.decentcode.pl",
    "https://badania-app-523686224252.europe-west1.run.app",
]
# W trybie developmentu można dodać localhost
if os.getenv("ENVIRONMENT") == "development":
    ALLOWED_ORIGINS.extend(["http://localhost:8080", "http://127.0.0.1:8080"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Session middleware dla autentykacji
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    max_age=3600 * 24,  # 24 godziny
    same_site="lax",
    https_only=True if os.getenv("ENVIRONMENT") != "development" else False
)

# Rate limiting - słownik do przechowywania prób logowania
login_attempts = defaultdict(list)
MAX_LOGIN_ATTEMPTS = 5
LOGIN_LOCKOUT_TIME = 900  # 15 minut w sekundach

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """Obsługa błędów walidacji - ograniczone szczegóły dla bezpieczeństwa"""
    # Loguj szczegółowe błędy na serwerze
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error.get("loc", []))
        msg = error.get("msg", "Błąd walidacji")
        errors.append(f"{field}: {msg}")
    logger.warning(f"Błąd walidacji: {errors} z IP: {request.client.host if request.client else 'unknown'}")
    # Zwróć ogólny komunikat dla użytkownika
    return JSONResponse(
        status_code=422,
        content={"detail": "Błąd walidacji danych"}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Obsługa ogólnych błędów - nie ujawnia szczegółów"""
    logger.error(f"Nieoczekiwany błąd: {str(exc)} z IP: {request.client.host if request.client else 'unknown'}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Wystąpił błąd serwera"}
    )

# Middleware do dodawania nagłówków bezpieczeństwa
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    # HSTS tylko dla HTTPS
    if request.url.scheme == "https":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    # Content Security Policy
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data:; "
        "connect-src 'self';"
    )
    return response

# Konfiguracja Google Cloud Storage
BUCKET_NAME = "hipokrates"
CSV_FILE_NAME = "badania.csv"
CSV_FILE = "badania.csv"  # Dla lokalnego fallback
PLATNOSCI_FILE_NAME = "platnosci.csv"
PLATNOSCI_FILE = "platnosci.csv"  # Dla lokalnego fallback

# Hasło z zmiennej środowiskowej (domyślnie dla developmentu)
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "hipokrates")
if ADMIN_PASSWORD == "hipokrates" and os.getenv("ENVIRONMENT") != "development":
    logger.warning("Używane domyślne hasło! Ustaw ADMIN_PASSWORD w zmiennych środowiskowych.")

# Timeouty dla operacji I/O (w sekundach)
STORAGE_TIMEOUT = 30

def get_storage_client():
    """Zwraca klienta Google Cloud Storage lub None jeśli nie jest dostępny"""
    try:
        from google.cloud import storage
        from google.api_core import timeout
        # Dodaj timeout dla operacji
        return storage.Client()
    except Exception as e:
        logger.error(f"Błąd podczas inicjalizacji Cloud Storage: {e}")
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
    
    # Próbuj pobrać z Google Cloud Storage z timeoutem
    storage_client = get_storage_client()
    if storage_client:
        try:
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError("Timeout podczas pobierania z Cloud Storage")
            
            # Ustaw timeout (tylko na Unix)
            if hasattr(signal, 'SIGALRM'):
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(STORAGE_TIMEOUT)
            
            try:
                bucket = storage_client.bucket(BUCKET_NAME)
                blob = bucket.blob(CSV_FILE_NAME)
                csv_content = blob.download_as_text(encoding='utf-8', timeout=STORAGE_TIMEOUT)
            finally:
                if hasattr(signal, 'SIGALRM'):
                    signal.alarm(0)  # Wyłącz alarm
        except TimeoutError:
            logger.error("Timeout podczas pobierania z Cloud Storage")
            csv_content = None
        except Exception as e:
            logger.error(f"Błąd podczas pobierania z Cloud Storage: {e}")
            csv_content = None
    
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

# Funkcja pomocnicza do sprawdzania rate limiting
def check_rate_limit(client_ip: str) -> bool:
    """Sprawdza czy IP nie przekroczyło limitu prób logowania"""
    now = time.time()
    # Usuń stare próby (starsze niż LOGIN_LOCKOUT_TIME)
    login_attempts[client_ip] = [
        attempt_time for attempt_time in login_attempts[client_ip]
        if now - attempt_time < LOGIN_LOCKOUT_TIME
    ]
    
    # Sprawdź czy przekroczono limit
    if len(login_attempts[client_ip]) >= MAX_LOGIN_ATTEMPTS:
        return False
    return True

def record_login_attempt(client_ip: str):
    """Zapisuje próbę logowania"""
    login_attempts[client_ip].append(time.time())

@app.post("/api/login")
async def login(request: Request):
    """Weryfikuje hasło z rate limiting"""
    client_ip = request.client.host if request.client else "unknown"
    
    # Sprawdź rate limiting
    if not check_rate_limit(client_ip):
        logger.warning(f"Zbyt wiele prób logowania z IP: {client_ip}")
        raise HTTPException(
            status_code=429,
            detail="Zbyt wiele prób logowania. Spróbuj ponownie za 15 minut."
        )
    
    try:
        data = await request.json()
        password = data.get("password", "")
        
        # Porównaj hasło używając bezpiecznego porównania
        if secrets.compare_digest(password, ADMIN_PASSWORD):
            # Zalogowano pomyślnie - wyczyść próby
            login_attempts[client_ip] = []
            # Ustaw sesję
            request.session["authenticated"] = True
            request.session["login_time"] = time.time()
            logger.info(f"Pomyślne logowanie z IP: {client_ip}")
            return {"success": True}
        else:
            # Nieprawidłowe hasło - zapisz próbę
            record_login_attempt(client_ip)
            logger.warning(f"Nieprawidłowe hasło z IP: {client_ip}")
            raise HTTPException(status_code=401, detail="Nieprawidłowe hasło")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Błąd podczas logowania: {e}")
        raise HTTPException(status_code=500, detail="Wystąpił błąd podczas logowania")

# Dependency do sprawdzania autentykacji
async def require_auth(request: Request):
    """Sprawdza czy użytkownik jest zalogowany"""
    if not request.session.get("authenticated"):
        logger.warning(f"Próba dostępu bez autentykacji z IP: {request.client.host if request.client else 'unknown'}")
        raise HTTPException(
            status_code=401,
            detail="Wymagane logowanie"
        )
    # Sprawdź czy sesja nie wygasła (24 godziny)
    login_time = request.session.get("login_time", 0)
    if time.time() - login_time > 3600 * 24:
        request.session.clear()
        raise HTTPException(
            status_code=401,
            detail="Sesja wygasła"
        )
    return True

@app.get("/api/badania")
async def get_badania(auth: bool = Depends(require_auth)):
    """Zwraca wszystkie badania posortowane alfabetycznie - wymaga autentykacji"""
    logger.info(f"Pobieranie listy badań")
    badania = load_badania()
    # Sortuj alfabetycznie po nazwie
    badania_sorted = sorted(badania, key=lambda x: x['nazwa'].lower())
    return {"badania": badania_sorted}

@app.post("/api/search")
async def search_badania(request: Request, auth: bool = Depends(require_auth)):
    """Wyszukuje badania po nazwie - wymaga autentykacji"""
    data = await request.json()
    query = data.get("query", "").strip().lower()
    
    # Walidacja długości zapytania
    if len(query) > 200:
        raise HTTPException(status_code=400, detail="Zapytanie zbyt długie")
    
    if not query:
        return {"badania": []}
    
    logger.info(f"Wyszukiwanie: {query[:50]}...")
    wszystkie_badania = load_badania()
    # Wyszukiwanie case-insensitive
    results = [
        badanie for badanie in wszystkie_badania
        if query in badanie['nazwa'].lower()
    ]
    
    return {"badania": results}

def load_full_csv() -> Tuple[List[Dict], Optional[int]]:
    """Wczytuje pełne dane CSV (wszystkie wiersze)
    Zwraca tuple: (lista badań, generation number dla optimistic locking)"""
    csv_content = None
    generation = None
    
    # Próbuj pobrać z Google Cloud Storage z timeoutem
    storage_client = get_storage_client()
    if storage_client:
        try:
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError("Timeout podczas pobierania z Cloud Storage")
            
            # Ustaw timeout (tylko na Unix)
            if hasattr(signal, 'SIGALRM'):
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(STORAGE_TIMEOUT)
            
            try:
                bucket = storage_client.bucket(BUCKET_NAME)
                blob = bucket.blob(CSV_FILE_NAME)
                # Pobierz generation number dla optimistic locking
                blob.reload(timeout=STORAGE_TIMEOUT)
                generation = blob.generation
                csv_content = blob.download_as_text(encoding='utf-8', timeout=STORAGE_TIMEOUT)
            finally:
                if hasattr(signal, 'SIGALRM'):
                    signal.alarm(0)  # Wyłącz alarm
        except TimeoutError:
            logger.error("Timeout podczas pobierania z Cloud Storage")
            csv_content = None
        except Exception as e:
            logger.error(f"Błąd podczas pobierania z Cloud Storage: {e}")
            csv_content = None
    
    # Jeśli nie udało się pobrać z Cloud Storage, spróbuj lokalnie
    if csv_content is None:
        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, 'r', encoding='utf-8') as f:
                csv_content = f.read()
        else:
            return [], None
    
    # Parsuj CSV
    csv_io = io.StringIO(csv_content)
    reader = csv.DictReader(csv_io, delimiter=';')
    return list(reader), generation

@app.get("/api/badania/edit")
async def get_badania_for_edit(auth: bool = Depends(require_auth)):
    """Zwraca wszystkie badania do edycji - wymaga autentykacji"""
    logger.info("Pobieranie badań do edycji")
    badania, _ = load_full_csv()  # Ignoruj generation number dla odczytu
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
async def save_badania(data: BadaniaUpdate, request: Request, auth: bool = Depends(require_auth)):
    """Zapisuje badania do Cloud Storage lub lokalnie - wymaga autentykacji
    Używa optimistic locking z generation numbers aby zapobiec race conditions"""
    client_ip = request.client.host if request.client else "unknown"
    
    # Walidacja rozmiaru danych
    if len(data.badania) > 10000:
        logger.warning(f"Próba zapisu zbyt dużej liczby badań ({len(data.badania)}) z IP: {client_ip}")
        raise HTTPException(status_code=400, detail="Zbyt duża liczba badań (maksymalnie 10000)")
    
    logger.info(f"Zapisywanie {len(data.badania)} badań z IP: {client_ip}")
    
    max_retries = 5
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # Wczytaj aktualny stan pliku z generation number
            _, generation = load_full_csv()
            
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
            
            # Próbuj zapisać do Cloud Storage z optimistic locking
            storage_client = get_storage_client()
            if storage_client:
                try:
                    bucket = storage_client.bucket(BUCKET_NAME)
                    blob = bucket.blob(CSV_FILE_NAME)
                    
                    # Jeśli mamy generation number, użyj go do optimistic locking
                    if generation is not None:
                        # Ustaw generation precondition - zapis się powiedzie tylko jeśli plik nie został zmieniony
                        blob.upload_from_string(
                            csv_content, 
                            content_type='text/csv',
                            if_generation_match=generation
                        )
                    else:
                        # Pierwszy zapis lub lokalny fallback
                        blob.upload_from_string(csv_content, content_type='text/csv')
                    
                    return {"success": True, "message": "Dane zostały zapisane do Cloud Storage"}
                except Exception as e:
                    error_str = str(e)
                    error_code = getattr(e, 'code', None) if hasattr(e, 'code') else None
                    # Sprawdź czy to błąd generation mismatch (412 Precondition Failed)
                    # Google Cloud Storage zwraca 412 gdy if_generation_match się nie zgadza
                    if (error_code == 412 or 
                        "412" in error_str or 
                        "Precondition" in error_str or 
                        "generation" in error_str.lower() or
                        "conditionNotMet" in error_str):
                        # Plik został zmieniony przez innego użytkownika - spróbuj ponownie
                        retry_count += 1
                        if retry_count < max_retries:
                            import time
                            time.sleep(0.1 * retry_count)  # Exponential backoff
                            continue
                        else:
                            raise HTTPException(
                                status_code=409, 
                                detail="Plik został zmieniony przez innego użytkownika. Odśwież dane i spróbuj ponownie."
                            )
                    else:
                        print(f"Błąd podczas zapisu do Cloud Storage: {e}")
                        # Fallback do lokalnego zapisu
                        break
            
            # Jeśli Cloud Storage nie jest dostępny lub wystąpił błąd, zapisz lokalnie
            try:
                with open(CSV_FILE, 'w', encoding='utf-8') as f:
                    f.write(csv_content)
                return {"success": True, "message": "Dane zostały zapisane lokalnie"}
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Błąd podczas zapisu do pliku lokalnego: {str(e)}")
        except HTTPException:
            raise
        except Exception as e:
            if retry_count < max_retries - 1:
                retry_count += 1
                import time
                time.sleep(0.1 * retry_count)
                continue
            raise HTTPException(status_code=400, detail=f"Błąd walidacji: {str(e)}")
    
    # Jeśli dotarliśmy tutaj, wszystkie próby się nie powiodły
    raise HTTPException(status_code=500, detail="Nie udało się zapisać danych po kilku próbach")

class PlatnoscCreate(BaseModel):
    uid: str
    data: str
    badania: str
    kwota: float
    uwagi: str = ""

def load_platnosci() -> Tuple[List[Dict], Optional[int]]:
    """Wczytuje dane z pliku platnosci.csv z Google Cloud Storage lub lokalnie
    Zwraca tuple: (lista płatności, generation number dla optimistic locking)"""
    csv_content = None
    generation = None
    
    # Próbuj pobrać z Google Cloud Storage z timeoutem
    storage_client = get_storage_client()
    if storage_client:
        try:
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError("Timeout podczas pobierania z Cloud Storage")
            
            # Ustaw timeout (tylko na Unix)
            if hasattr(signal, 'SIGALRM'):
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(STORAGE_TIMEOUT)
            
            try:
                bucket = storage_client.bucket(BUCKET_NAME)
                blob = bucket.blob(PLATNOSCI_FILE_NAME)
                # Pobierz generation number dla optimistic locking
                blob.reload(timeout=STORAGE_TIMEOUT)
                generation = blob.generation
                csv_content = blob.download_as_text(encoding='utf-8', timeout=STORAGE_TIMEOUT)
            finally:
                if hasattr(signal, 'SIGALRM'):
                    signal.alarm(0)  # Wyłącz alarm
        except TimeoutError:
            logger.error("Timeout podczas pobierania platnosci.csv z Cloud Storage")
            csv_content = None
        except Exception as e:
            logger.error(f"Błąd podczas pobierania platnosci.csv z Cloud Storage: {e}")
            csv_content = None
    
    # Jeśli nie udało się pobrać z Cloud Storage, spróbuj lokalnie
    if csv_content is None:
        if os.path.exists(PLATNOSCI_FILE):
            with open(PLATNOSCI_FILE, 'r', encoding='utf-8') as f:
                csv_content = f.read()
        else:
            return [], None
    
    # Parsuj CSV
    csv_io = io.StringIO(csv_content)
    reader = csv.DictReader(csv_io, delimiter=';')
    return list(reader), generation

@app.post("/api/platnosci/save")
async def save_platnosc(data: PlatnoscCreate, request: Request, auth: bool = Depends(require_auth)):
    """Zapisuje płatność do pliku platnosci.csv w Cloud Storage lub lokalnie - wymaga autentykacji
    Używa optimistic locking z generation numbers aby zapobiec race conditions"""
    client_ip = request.client.host if request.client else "unknown"
    
    # Walidacja danych
    if data.kwota < 0 or data.kwota > 1000000:
        logger.warning(f"Nieprawidłowa kwota ({data.kwota}) z IP: {client_ip}")
        raise HTTPException(status_code=400, detail="Nieprawidłowa kwota")
    
    if len(data.uwagi) > 1000:
        raise HTTPException(status_code=400, detail="Uwagi zbyt długie (maksymalnie 1000 znaków)")
    
    logger.info(f"Zapisywanie płatności: {data.kwota} zł z IP: {client_ip}")
    
    max_retries = 5
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # Wczytaj istniejące płatności z generation number
            existing_platnosci, generation = load_platnosci()
            
            # Dodaj nową płatność
            new_row = {
                'UID': data.uid,
                'DATA': data.data,
                'BADANIA': data.badania,
                'KWOTA': str(data.kwota).replace('.', ','),
                'UWAGI': data.uwagi
            }
            existing_platnosci.append(new_row)
            
            # Przygotuj dane do zapisu
            output = io.StringIO()
            writer = csv.writer(output, delimiter=';')
            
            # Nagłówek
            writer.writerow(['UID', 'DATA', 'BADANIA', 'KWOTA', 'UWAGI'])
            
            # Wiersze danych
            for row in existing_platnosci:
                writer.writerow([
                    row.get('UID', ''),
                    row.get('DATA', ''),
                    row.get('BADANIA', ''),
                    row.get('KWOTA', ''),
                    row.get('UWAGI', '')
                ])
            
            csv_content = output.getvalue()
            
            # Próbuj zapisać do Cloud Storage z optimistic locking
            storage_client = get_storage_client()
            if storage_client:
                try:
                    bucket = storage_client.bucket(BUCKET_NAME)
                    blob = bucket.blob(PLATNOSCI_FILE_NAME)
                    
                    # Jeśli mamy generation number, użyj go do optimistic locking
                    if generation is not None:
                        # Ustaw generation precondition - zapis się powiedzie tylko jeśli plik nie został zmieniony
                        blob.upload_from_string(
                            csv_content, 
                            content_type='text/csv',
                            if_generation_match=generation
                        )
                    else:
                        # Pierwszy zapis lub lokalny fallback
                        blob.upload_from_string(csv_content, content_type='text/csv')
                    
                    return {"success": True, "message": "Płatność została zapisana do Cloud Storage"}
                except Exception as e:
                    error_str = str(e)
                    error_code = getattr(e, 'code', None) if hasattr(e, 'code') else None
                    # Sprawdź czy to błąd generation mismatch (412 Precondition Failed)
                    # Google Cloud Storage zwraca 412 gdy if_generation_match się nie zgadza
                    if (error_code == 412 or 
                        "412" in error_str or 
                        "Precondition" in error_str or 
                        "generation" in error_str.lower() or
                        "conditionNotMet" in error_str):
                        # Plik został zmieniony przez innego użytkownika - spróbuj ponownie
                        retry_count += 1
                        if retry_count < max_retries:
                            import time
                            time.sleep(0.1 * retry_count)  # Exponential backoff
                            continue
                        else:
                            raise HTTPException(
                                status_code=409, 
                                detail="Plik został zmieniony przez innego użytkownika. Spróbuj ponownie."
                            )
                    else:
                        print(f"Błąd podczas zapisu do Cloud Storage: {e}")
                        # Fallback do lokalnego zapisu
                        break
            
            # Jeśli Cloud Storage nie jest dostępny lub wystąpił błąd, zapisz lokalnie
            try:
                with open(PLATNOSCI_FILE, 'w', encoding='utf-8') as f:
                    f.write(csv_content)
                return {"success": True, "message": "Płatność została zapisana lokalnie"}
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Błąd podczas zapisu do pliku lokalnego: {str(e)}")
        except HTTPException:
            raise
        except Exception as e:
            if retry_count < max_retries - 1:
                retry_count += 1
                import time
                time.sleep(0.1 * retry_count)
                continue
            raise HTTPException(status_code=400, detail=f"Błąd podczas zapisu płatności: {str(e)}")
    
    # Jeśli dotarliśmy tutaj, wszystkie próby się nie powiodły
    raise HTTPException(status_code=500, detail="Nie udało się zapisać płatności po kilku próbach")

@app.get("/api/platnosci/stats")
async def get_daily_stats(auth: bool = Depends(require_auth)):
    """Zwraca statystyki transakcji z dzisiejszego dnia - wymaga autentykacji"""
    try:
        # Wczytaj wszystkie płatności (ignoruj generation number dla odczytu)
        platnosci, _ = load_platnosci()
        
        # Pobierz dzisiejszą datę w strefie czasowej Polski (DD.MM.YYYY)
        poland_tz = pytz.timezone('Europe/Warsaw')
        today = datetime.now(poland_tz)
        today_str = today.strftime('%d.%m.%Y')
        
        # Filtruj transakcje z dzisiejszego dnia
        today_platnosci = []
        for platnosc in platnosci:
            data_str = platnosc.get('DATA', '').strip()
            if not data_str:
                continue
            
            # Sprawdź czy data zaczyna się od dzisiejszej daty (może być z godziną)
            # Format: "DD.MM.YYYY, HH:MM:SS" lub "DD.MM.YYYY HH:MM:SS"
            if data_str.startswith(today_str):
                today_platnosci.append(platnosc)
        
        # Oblicz sumę i znajdź najnowszą transakcję
        suma = 0.0
        latest_date = None
        
        for platnosc in today_platnosci:
            kwota_str = platnosc.get('KWOTA', '0').replace(',', '.')
            try:
                suma += float(kwota_str)
            except ValueError:
                pass
            
            # Znajdź najnowszą datę
            data_str = platnosc.get('DATA', '').strip()
            if data_str and (latest_date is None or data_str > latest_date):
                latest_date = data_str
        
        # Jeśli nie ma transakcji z dzisiaj, latest_date powinno być puste
        if not today_platnosci:
            latest_date = ""
        
        return {
            "count": len(today_platnosci),
            "sum": suma,
            "latest_date": latest_date or ""
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd podczas pobierania statystyk: {str(e)}")

@app.get("/api/platnosci/by-date")
async def get_platnosci_by_date(date: str, auth: bool = Depends(require_auth)):
    """Zwraca transakcje z wybranego dnia - wymaga autentykacji"""
    try:
        # Walidacja formatu daty
        if len(date) > 20:
            raise HTTPException(status_code=400, detail="Nieprawidłowy format daty")
        # Wczytaj wszystkie płatności (ignoruj generation number dla odczytu)
        platnosci, _ = load_platnosci()
        
        # Konwertuj datę z formatu YYYY-MM-DD lub YYYY.MM.DD na DD.MM.YYYY
        date_str = date
        if '-' in date:
            # Format YYYY-MM-DD
            date_parts = date.split('-')
            if len(date_parts) == 3:
                date_str = f"{date_parts[2]}.{date_parts[1]}.{date_parts[0]}"
        elif '.' in date:
            # Format YYYY.MM.DD
            date_parts = date.split('.')
            if len(date_parts) == 3:
                date_str = f"{date_parts[2]}.{date_parts[1]}.{date_parts[0]}"
        
        # Filtruj transakcje z wybranego dnia
        filtered_platnosci = []
        for platnosc in platnosci:
            data_str = platnosc.get('DATA', '').strip()
            if data_str.startswith(date_str):
                filtered_platnosci.append(platnosc)
        
        # Sortuj po dacie i godzinie (od najnowszych)
        filtered_platnosci.sort(key=lambda x: x.get('DATA', ''), reverse=True)
        
        return {
            "transactions": filtered_platnosci
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Błąd podczas pobierania transakcji: {e}")
        raise HTTPException(status_code=500, detail="Błąd podczas pobierania transakcji")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

