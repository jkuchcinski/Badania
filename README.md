# System Badań Lekarskich

Aplikacja webowa do wyszukiwania i zarządzania badaniami lekarskimi.

## Funkcjonalności

- Logowanie z hasłem "hipokrates"
- Wyświetlanie wszystkich badań posortowanych alfabetycznie (lewa strona)
- Wyszukiwanie badań po nazwie (prawa strona)
- Dodawanie badań do listy wybranych
- Obliczanie sumy wszystkich wybranych badań

## Konfiguracja Google Cloud Storage

Aplikacja wczytuje plik `badania.csv` z Google Cloud Storage bucket o nazwie `hipokrates`.

**Wymagane kroki:**
1. Utwórz bucket w Google Cloud Storage o nazwie `hipokrates`
2. Prześlij plik `badania.csv` do tego bucketu
3. Upewnij się, że konto serwisowe Cloud Run ma uprawnienia do odczytu z tego bucketu:
   ```bash
   gcloud projects add-iam-policy-binding hipokrates-478419 \
     --member="serviceAccount:SERVICE_ACCOUNT_EMAIL" \
     --role="roles/storage.objectViewer"
   ```

**Lokalne uruchomienie:**
- Aplikacja automatycznie użyje lokalnego pliku `badania.csv` jako fallback, jeśli Cloud Storage nie jest dostępny

## Lokalne uruchomienie

```bash
# Zainstaluj zależności
pip install -r requirements.txt

# Uruchom aplikację
python main.py
```

Aplikacja będzie dostępna pod adresem: http://localhost:8080

**Uwaga:** W środowisku lokalnym aplikacja użyje lokalnego pliku `badania.csv` jeśli Cloud Storage nie jest skonfigurowany.

## Publikacja na Google Cloud Run

### Rozwiązanie problemu z uprawnieniami

Jeśli otrzymujesz błąd `storage.objects.get access`, najpierw uruchom:

```bash
./fix-permissions.sh
```

Lub ręcznie nadaj uprawnienia:

```bash
PROJECT_NUMBER=$(gcloud projects describe hipokrates-478419 --format="value(projectNumber)")
CLOUD_BUILD_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"

gcloud projects add-iam-policy-binding hipokrates-478419 \
  --member="serviceAccount:${CLOUD_BUILD_SA}" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding hipokrates-478419 \
  --member="serviceAccount:${CLOUD_BUILD_SA}" \
  --role="roles/run.admin"
```

### Metoda 1: Lokalne budowanie (zalecane, omija problemy z uprawnieniami)

```bash
./deploy-local.sh
```

Ta metoda buduje obraz lokalnie i pushuje go bezpośrednio do Container Registry. Skrypt automatycznie ustawia aktywny projekt Google Cloud na `hipokrates-478419`.

### Metoda 2: Cloud Build (po naprawie uprawnień)

```bash
./deploy.sh
```

Skrypt automatycznie ustawia aktywny projekt Google Cloud na `hipokrates-478419`.

Lub:

```bash
gcloud builds submit --config cloudbuild.yaml
```

### Metoda 3: Ręczne wdrożenie

```bash
# Ustaw aktywny projekt Google Cloud
gcloud config set project hipokrates-478419

# Zbuduj obraz lokalnie
docker build -t gcr.io/hipokrates-478419/badania-app .

# Zaloguj się do Container Registry
gcloud auth configure-docker

# Wyślij obraz
docker push gcr.io/hipokrates-478419/badania-app

# Wdróż na Cloud Run
gcloud run deploy badania-app \
  --image gcr.io/hipokrates-478419/badania-app \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated \
  --port 8080
```

## Struktura projektu

- `main.py` - Backend FastAPI
- `index.html` - Frontend aplikacji
- `badania.csv` - Plik z danymi badań
- `Dockerfile` - Konfiguracja Docker
- `requirements.txt` - Zależności Pythona

