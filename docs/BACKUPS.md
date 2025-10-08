# Sauvegardes (PostgreSQL + médias)

## Lancer une sauvegarde manuelle
```bash
chmod +x scripts/backup.sh
./scripts/backup.sh
```
Les archives seront dans `./backups/`.

## Planifier une sauvegarde nocturne (cron)
```bash
crontab -e
```
Ajouter (ex: tous les jours à 02:15):
```
15 2 * * * cd /home/<user>/inventory-management && /bin/bash scripts/backup.sh >> backups/cron.log 2>&1
```

## Restaurer
- Base de données:
```bash
gunzip -c backups/db-YYYYMMDD-HHMMSS.sql.gz | docker compose exec -T db psql -U dcat -d dcat
```
- Médias:
```bash
tar -xzf backups/media-YYYYMMDD-HHMMSS.tar.gz -C .
```
