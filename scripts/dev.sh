#!/usr/bin/env bash
set -uo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"
BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-5173}"

if ! command -v pnpm >/dev/null 2>&1; then
  echo "pnpm no está instalado. Instala pnpm 12 y vuelve a ejecutar este script." >&2
  exit 1
fi

if [[ ! -x "$FRONTEND_DIR/node_modules/.bin/vite" ]]; then
  echo "Faltan dependencias frontend. Ejecuta: cd frontend && pnpm install --frozen-lockfile" >&2
  exit 1
fi

if [[ -x "$BACKEND_DIR/.venv/bin/uvicorn" ]]; then
  UVICORN="$BACKEND_DIR/.venv/bin/uvicorn"
elif [[ -x "$BACKEND_DIR/venv/bin/uvicorn" ]]; then
  UVICORN="$BACKEND_DIR/venv/bin/uvicorn"
else
  echo "No encuentro uvicorn en backend/.venv o backend/venv." >&2
  echo "Crea el entorno con Python 3.11 e instala backend/requirements.txt; ver backend/README.md." >&2
  exit 1
fi

UVICORN_ENV_ARGS=()
if [[ -f "$BACKEND_DIR/.env" ]]; then
  UVICORN_ENV_ARGS+=(--env-file "$BACKEND_DIR/.env")
else
  echo "No existe backend/.env; Meteomatics requiere METEOMATICS_USERNAME y METEOMATICS_PASSWORD." >&2
fi

cleanup() {
  trap - INT TERM EXIT
  kill "$FRONTEND_PID" "$BACKEND_PID" 2>/dev/null || true
  wait "$FRONTEND_PID" 2>/dev/null || true
  wait "$BACKEND_PID" 2>/dev/null || true
}

(
  cd "$BACKEND_DIR"
  exec "$UVICORN" app.main:app --reload --host 0.0.0.0 --port "$BACKEND_PORT" "${UVICORN_ENV_ARGS[@]}"
) &
BACKEND_PID=$!

(
  cd "$FRONTEND_DIR"
  exec env "VITE_API_URL=http://localhost:$BACKEND_PORT" \
    pnpm dev --host 0.0.0.0 --port "$FRONTEND_PORT"
) &
FRONTEND_PID=$!

trap cleanup INT TERM EXIT
echo "Backend:  http://localhost:$BACKEND_PORT (Swagger: /docs)"
echo "Frontend: http://localhost:$FRONTEND_PORT"
echo "Presiona Ctrl+C para detener ambos procesos."

wait -n "$BACKEND_PID" "$FRONTEND_PID"
STATUS=$?
exit "$STATUS"
