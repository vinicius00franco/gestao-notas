#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

# Dependências básicas
if ! command -v curl >/dev/null 2>&1; then
  echo "curl não encontrado. Instale curl para executar verificações HTTP." >&2
  exit 1
fi

PY=$(command -v python3 || true)

echo "Verificando processo Celery..."
if pgrep -f 'celery.*worker' >/dev/null; then
  echo "Celery worker: OK"
  # Tentativa opcional de ping no Celery (ignora falhas)
  if [ -n "$PY" ]; then
    if "$PY" -m celery -A backend inspect ping -d "auto" -t 2 >/dev/null 2>&1; then
      echo "Celery ping: OK"
    else
      echo "Celery ping não confirmado (pode ser normal se sem nós nomeados)." 
    fi
  fi
else
  echo "Celery worker não encontrado" >&2
fi

echo "Verificando servidor Django (health check e endpoints da API)..."
BASE="http://127.0.0.1:8000"
API_BASE="$BASE/api"

# Função para obter código HTTP
http_code() {
  local url="$1"
  curl -s -o /dev/null -w "%{http_code}" "$url"
}

# Checa healthz (GET deve retornar 200)
HEALTH_CODE=$(http_code "$BASE/healthz")
if [ "$HEALTH_CODE" = "200" ]; then
  echo "Healthz: OK (200)"
else
  echo "Healthz: código $HEALTH_CODE (esperado 200). Veja django.log" >&2
fi

# Checa dashboard (GET deve retornar 200)
DASH_CODE=$(http_code "$API_BASE/dashboard/")
if [ "$DASH_CODE" = "200" ]; then
  echo "API /api/dashboard/: OK (200)"
else
  echo "API /api/dashboard/: código $DASH_CODE (esperado 200)." >&2
fi

# Checa JobStatus endpoint com UUID inexistente; 404 indica endpoint ativo
TEST_UUID="00000000-0000-0000-0000-000000000000"
JOB_CODE=$(http_code "$API_BASE/jobs/$TEST_UUID/")
if [ "$JOB_CODE" = "404" ] || [ "$JOB_CODE" = "200" ]; then
  echo "Endpoint /api/jobs/<uuid> acessível (HTTP $JOB_CODE)"
else
  echo "Endpoint /api/jobs/<uuid> retornou HTTP $JOB_CODE (esperado 404 p/ inexistente)." >&2
fi

echo "Verificação finalizada. Para detalhes, veja django.log e celery.log"
