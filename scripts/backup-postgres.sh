#!/usr/bin/env bash
# Faz backup do Postgres do stack de producao (docker-compose.prod.yml) e
# aplica retencao local. Opcionalmente envia uma copia para outra maquina
# via scp. Pensado para ser chamado por cron uma vez por dia numa VPS.
# Equivalente Linux de scripts/backup-postgres.ps1 (Windows).
# Ver docs/workflows/deploy-vps-tailscale.md.
#
# Uso:
#   ./scripts/backup-postgres.sh
#   ./scripts/backup-postgres.sh --remote usuario@outra-maquina.com

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

BACKUP_DIR="${BACKUP_DIR:-$REPO_ROOT/../area-verde-backups}"
RETENTION_DAYS="${RETENTION_DAYS:-14}"
REMOTE_HOST=""
REMOTE_PATH="${REMOTE_PATH:-~/area-verde-backups/}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --remote)
      REMOTE_HOST="$2"
      shift 2
      ;;
    --remote-path)
      REMOTE_PATH="$2"
      shift 2
      ;;
    *)
      echo "Argumento desconhecido: $1" >&2
      exit 1
      ;;
  esac
done

get_env_value() {
  local name="$1" default="$2"
  if [[ -f "$REPO_ROOT/.env" ]]; then
    local value
    value=$(grep -E "^${name}=" "$REPO_ROOT/.env" | tail -n1 | cut -d= -f2-)
    if [[ -n "$value" ]]; then
      echo "$value"
      return
    fi
  fi
  echo "$default"
}

PG_USER=$(get_env_value POSTGRES_USER area_verde)
PG_DB=$(get_env_value POSTGRES_DB area_verde)

mkdir -p "$BACKUP_DIR"

TIMESTAMP=$(date +%Y-%m-%d_%H-%M)
SQL_FILE="$BACKUP_DIR/area-verde_${TIMESTAMP}.sql"
GZ_FILE="$SQL_FILE.gz"

echo "Gerando dump em $SQL_FILE ..."
docker compose -f docker-compose.prod.yml exec -T db \
  pg_dump -U "$PG_USER" -d "$PG_DB" >"$SQL_FILE"

if [[ ! -s "$SQL_FILE" ]]; then
  echo "pg_dump falhou ou gerou arquivo vazio. Backup abortado." >&2
  rm -f "$SQL_FILE"
  exit 1
fi

gzip -f "$SQL_FILE"
echo "Backup salvo em $GZ_FILE"

if [[ -n "$REMOTE_HOST" ]]; then
  echo "Enviando copia para $REMOTE_HOST:$REMOTE_PATH ..."
  if ! scp "$GZ_FILE" "${REMOTE_HOST}:${REMOTE_PATH}"; then
    echo "Aviso: falha ao enviar backup remoto. O backup local em $GZ_FILE continua valido." >&2
  fi
fi

echo "Aplicando retencao de $RETENTION_DAYS dias em $BACKUP_DIR ..."
find "$BACKUP_DIR" -name "area-verde_*.sql.gz" -mtime "+$RETENTION_DAYS" -delete

echo "Backup concluido."
