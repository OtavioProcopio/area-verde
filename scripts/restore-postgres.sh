#!/usr/bin/env bash
# Restaura um backup gerado por backup-postgres.sh no stack de producao.
# ISSO SUBSTITUI OS DADOS ATUAIS DO BANCO. Pede confirmacao explicita.
# Equivalente Linux de scripts/restore-postgres.ps1 (Windows).
# Ver docs/workflows/deploy-vps-tailscale.md.
#
# Uso:
#   ./scripts/restore-postgres.sh ../../area-verde-backups/area-verde_2026-09-12_03-00.sql.gz

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

GZ_FILE="${1:-}"
if [[ -z "$GZ_FILE" ]]; then
  echo "Uso: $0 <arquivo.sql.gz>" >&2
  exit 1
fi
if [[ ! -f "$GZ_FILE" ]]; then
  echo "Arquivo nao encontrado: $GZ_FILE" >&2
  exit 1
fi

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

echo "Isso vai APAGAR os dados atuais do banco '$PG_DB' e substituir pelo conteudo de $GZ_FILE." >&2
read -rp "Digite RESTAURAR para confirmar: " CONFIRM
if [[ "$CONFIRM" != "RESTAURAR" ]]; then
  echo "Cancelado."
  exit 0
fi

echo "Recriando o banco '$PG_DB' antes de restaurar..."
docker compose -f docker-compose.prod.yml exec -T db dropdb -U "$PG_USER" --if-exists "$PG_DB"
docker compose -f docker-compose.prod.yml exec -T db createdb -U "$PG_USER" "$PG_DB"

echo "Restaurando $GZ_FILE ..."
gunzip -c "$GZ_FILE" | docker compose -f docker-compose.prod.yml exec -T db psql -U "$PG_USER" -d "$PG_DB"

echo "Restauracao concluida. Reinicie a API se ela ja estava rodando:"
echo "  docker compose -f docker-compose.prod.yml restart api"
