#!/usr/bin/env bash
# Deployment aplikacji w Docker Desktop: budowa obrazu i uruchomienie kontenera.
set -euo pipefail

IMAGE_NAME="${IMAGE_NAME:-badania-app}"
CONTAINER_NAME="${CONTAINER_NAME:-badania-app}"
HOST_PORT="${PORT:-8080}"
CONTAINER_PORT=8080

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

usage() {
  cat <<'EOF'
Użycie: ./deploy-docker.sh [opcje]

  Buduje obraz (Dockerfile) i uruchamia kontener z mapowaniem portu.

Opcje:
  --no-build    Pomiń docker build (użyj istniejącego obrazu)
  --stop        Zatrzymaj i usuń kontener, wyjdź (bez uruchamiania)
  -h, --help    Ta pomoc

Zmienne środowiskowe:
  IMAGE_NAME       Tag obrazu (domyślnie: badania-app)
  CONTAINER_NAME   Nazwa kontenera (domyślnie: badania-app)
  PORT             Port na hoście (domyślnie: 8080)

  GOOGLE_APPLICATION_CREDENTIALS  Opcjonalnie; w ENVIRONMENT=development aplikacja
                                  i tak nie używa GCS do CSV — tylko pliki w /app.

  Pliki badania.csv i platnosci.csv z katalogu projektu (jeśli istnieją) są
  montowane do kontenera, tak jak przy lokalnym uruchomieniu bez Dockera.

Przykład:
  PORT=9000 ./deploy-docker.sh
EOF
}

NO_BUILD=false
STOP_ONLY=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --no-build) NO_BUILD=true ;;
    --stop) STOP_ONLY=true ;;
    -h|--help) usage; exit 0 ;;
    *)
      echo "Nieznana opcja: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
  shift
done

if ! docker info >/dev/null 2>&1; then
  echo "Błąd: Docker nie odpowiada. Uruchom Docker Desktop i spróbuj ponownie." >&2
  exit 1
fi

if [[ "$STOP_ONLY" == true ]]; then
  docker stop "$CONTAINER_NAME" 2>/dev/null || true
  docker rm "$CONTAINER_NAME" 2>/dev/null || true
  echo "Kontener $CONTAINER_NAME został zatrzymany i usunięty."
  exit 0
fi

if [[ "$NO_BUILD" == false ]]; then
  echo "Budowanie obrazu $IMAGE_NAME:latest ..."
  docker build -t "${IMAGE_NAME}:latest" .
fi

docker stop "$CONTAINER_NAME" 2>/dev/null || true
docker rm "$CONTAINER_NAME" 2>/dev/null || true

DOCKER_EXTRA=()
if [[ -n "${GOOGLE_APPLICATION_CREDENTIALS:-}" && -f "${GOOGLE_APPLICATION_CREDENTIALS}" ]]; then
  cred_host="$(cd "$(dirname "${GOOGLE_APPLICATION_CREDENTIALS}")" && pwd)/$(basename "${GOOGLE_APPLICATION_CREDENTIALS}")"
  cred_in="/secrets/gcp-credentials.json"
  DOCKER_EXTRA+=(-v "${cred_host}:${cred_in}:ro" -e "GOOGLE_APPLICATION_CREDENTIALS=${cred_in}")
  echo "Montowanie poświadczeń GCP: ${cred_host} -> ${cred_in}"
fi

if [[ -f "$SCRIPT_DIR/badania.csv" ]]; then
  DOCKER_EXTRA+=(-v "$SCRIPT_DIR/badania.csv:/app/badania.csv")
  echo "Montowanie badania.csv (tryb development — odczyt/zapis jak lokalnie, bez GCS)."
else
  echo "Uwaga: brak pliku $SCRIPT_DIR/badania.csv — lista badań w kontenerze będzie pusta." >&2
fi

if [[ -f "$SCRIPT_DIR/platnosci.csv" ]]; then
  DOCKER_EXTRA+=(-v "$SCRIPT_DIR/platnosci.csv:/app/platnosci.csv")
  echo "Montowanie platnosci.csv."
fi

# Lokalny Docker Desktop: CORS i ciasteczka sesji jak w development
# Przy set -u nie wolno rozwijać pustej tablicy "${DOCKER_EXTRA[@]}" — opcjonalne argi przez "$@".
run_container() {
  docker run -d \
    --name "$CONTAINER_NAME" \
    --platform linux/amd64 \
    -e ENVIRONMENT=development \
    "$@" \
    -p "${HOST_PORT}:${CONTAINER_PORT}" \
    "${IMAGE_NAME}:latest"
}

if [[ ${#DOCKER_EXTRA[@]} -gt 0 ]]; then
  run_container "${DOCKER_EXTRA[@]}"
else
  run_container
fi

echo "Kontener $CONTAINER_NAME uruchomiony."
echo "Aplikacja: http://127.0.0.1:${HOST_PORT}/"
echo "Logi: docker logs -f $CONTAINER_NAME"
