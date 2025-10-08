#!/usr/bin/env bash
set -euo pipefail
# Usage: ./scripts/backup.sh [backup_dir]
BACKUP_DIR=${1:-backups}
mkdir -p "$BACKUP_DIR"
STAMP=$(date +%Y%m%d-%H%M%S)

# DB dump
if docker compose ps db >/dev/null 2>&1; then
	docker compose exec -T db pg_dump -U dcat -d dcat | gzip > "$BACKUP_DIR/db-$STAMP.sql.gz"
fi

# Media archive
if [ -d media ]; then
	tar -czf "$BACKUP_DIR/media-$STAMP.tar.gz" media/
fi

echo "Backups written to $BACKUP_DIR"
