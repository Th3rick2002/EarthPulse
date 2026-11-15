#!/usr/bin/env bash
set -uo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"
BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-5173}"
IMAGE="${TRENDSCOPE_BACKEND_IMAGE:-trendscope-backend:dev}"
CONTAINER_NAME="trendscope-backend-dev"

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker no está instalado o no está disponible en PATH." >&2
  exit 1
fi
if ! docker info >/dev/null 2>&1; then
  echo "Docker no está iniciado o el usuario no puede acceder al daemon." >&2
  exit 1
fi
if ! command -v pnpm >/dev/null 2>&1; then
  echo "pnpm no está instalado. Instala pnpm 12 y vuelve a ejecutar este script." >&2
  exit 1
fi
if [[ ! -x "$FRONTEND_DIR/node_modules/.bin/vite" ]]; then
  echo "Faltan dependencias frontend. Ejecuta: cd frontend && pnpm install --frozen-lockfile" >&2
  exit 1
fi

echo "Construyendo imagen Docker del backend: $IMAGE"
docker build -t "$IMAGE" "$BACKEND_DIR" || exit $?

DOCKER_ENV_ARGS=()
if [[ -f "$BACKEND_DIR/.env" ]]; then
  DOCKER_ENV_ARGS+=(--env-file "$BACKEND_DIR/.env")
fi

cleanup() {
  trap - INT TERM EXIT
  kill "$FRONTEND_PID" "$BACKEND_PID" 2>/dev/null || true
  wait "$FRONTEND_PID" 2>/dev/null || true
  wait "$BACKEND_PID" 2>/dev/null || true
}

docker run --rm --name "$CONTAINER_NAME" \
  -p "$BACKEND_PORT:8080" \
  "${DOCKER_ENV_ARGS[@]}" \
  "$IMAGE" &
BACKEND_PID=$!

(
  cd "$FRONTEND_DIR"
  exec env "VITE_API_URL=http://localhost:$BACKEND_PORT" \
    pnpm dev --host 0.0.0.0 --port "$FRONTEND_PORT"
) &
FRONTEND_PID=$!

trap cleanup INT TERM EXIT
echo "Backend Docker: http://localhost:$BACKEND_PORT (Swagger: /docs)"
echo "Frontend:       http://localhost:$FRONTEND_PORT"
echo "Presiona Ctrl+C para detener ambos procesos y eliminar el contenedor."

wait -n "$BACKEND_PID" "$FRONTEND_PID"
STATUS=$?
exit "$STATUS"
