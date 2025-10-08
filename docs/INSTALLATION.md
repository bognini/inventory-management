# Installation (Ubuntu 24.04 / Proxmox VM)

## Option A — Docker (recommandé)

```bash
# Prérequis: Docker et Docker Compose
sudo apt update && sudo apt install -y docker.io docker-compose-plugin

# Cloner le dépôt
git clone https://github.com/bognini/inventory-management.git
cd inventory-management

# Lancer
docker compose up -d --build

# Appliquer les migrations et créer un superuser
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

Accéder à `http://<IP_VM>:8000`.

## Option B — Installation locale (sans Docker)

```bash
sudo apt update && sudo apt install -y python3-venv python3-pip git
git clone https://github.com/bognini/inventory-management.git
cd inventory-management
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 0.0.0.0:8000
```

## Rôles et droits
Dans l'interface d'administration (`/admin/`), créer les groupes suivants:
- Administrateurs
- Marketing
- Techniciens

Assigner les utilisateurs aux groupes voulus. Les pages de création/mouvements exigent Administrateurs ou Marketing. Les Techniciens peuvent consulter.

## Thème et logo
Remplacer `static/img/logo.png` par votre logo si souhaité (et ajuster CSS si nécessaire).
