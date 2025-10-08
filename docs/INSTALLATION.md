# Installation (Ubuntu 24.04 / Proxmox VM)

## 0) Préparer la VM (première connexion)
```bash
sudo apt update && sudo apt upgrade -y
# Installer Docker + Compose
sudo apt install -y docker.io docker-compose-plugin git
sudo usermod -aG docker $USER
newgrp docker

# Cloner le dépôt
cd ~
git clone https://github.com/bognini/inventory-management.git
cd inventory-management
```

## Option A — Docker (recommandé)
```bash
docker compose up -d --build
# Initialiser la base et comptes
docker compose exec web python manage.py migrate
docker compose exec web python manage.py seed_groups
docker compose exec web python manage.py createsuperuser
```
Accéder à `http://<IP_VM>:8000`.

## Option B — Installation locale (sans Docker)
```bash
sudo apt install -y python3-venv python3-pip
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_groups
python manage.py createsuperuser
python manage.py runserver 0.0.0.0:8000
```

## Rôles et droits
Créer les groupes dans `/admin/` si non créés par la commande: Administrateurs, Marketing, Techniciens. Assigner les utilisateurs.

## CSV Import/Export
- Articles: export via `/articles/export.csv`. Import via `/articles/importer/` avec CSV ayant les colonnes:
```
famille,type,fabricant,modele,numero_serie,description,prix_achat,cout_logistique,prix_desire,emplacement,fournisseur,quantite
```
- Mouvements: export via `/mouvements/export.csv`.

Notes d'import:
- Les références manquantes (famille, type, fabricant, modèle, emplacement, fournisseur) seront créées automatiquement.
- Le « prix_désiré » trop bas est relevé au minimum « prix_achat + cout_logistique ».

## Utiliser PostgreSQL (Docker)
La configuration Compose inclut PostgreSQL. Aucune action supplémentaire n'est requise: le service `db` démarre, puis le service `web` applique les migrations et lance le serveur.

Variables utilisées par Django:
- `DJANGO_DB_ENGINE=postgres`
- `DJANGO_DB_NAME=dcat`
- `DJANGO_DB_USER=dcat`
- `DJANGO_DB_PASSWORD=dcatpass`
- `DJANGO_DB_HOST=db`
- `DJANGO_DB_PORT=5432`

Voir `docs/BACKUPS.md` pour mettre en place les sauvegardes nocturnes (base + médias).

## Répertoires et PDF
- Répertoire clients: `/repertoire/clients/` (export CSV disponible)
- Répertoire projets: `/repertoire/projets/` (export CSV disponible)
- Bon de sortie: page imprimable et version PDF via le bouton dans la liste des mouvements.

## Exécution complète (VM neuve) — récapitulatif
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y docker.io docker-compose-plugin git
sudo usermod -aG docker $USER && newgrp docker
cd ~ && git clone https://github.com/bognini/inventory-management.git
cd inventory-management
# Mettre à jour aux derniers changements
git pull
# Lancer
docker compose up -d --build
# Initialisation
docker compose exec web python manage.py migrate
docker compose exec web python manage.py seed_groups
docker compose exec web python manage.py createsuperuser
```

## Multi-entrepôts
- Créez vos entrepôts et emplacements dans `/admin/`.
- Les formulaires d'entrée/sortie demandent l'entrepôt: les quantités sont tenues par entrepôt (`StockEntrepot`) et le total demeure sur l'article.

## Permissions (matrice)
Après création des groupes, vous pouvez appliquer la matrice de permissions par défaut:
```bash
docker compose exec web python manage.py seed_permissions
```
Cela donne: Administrateurs=full, Marketing=création/mouvements/consultation, Techniciens=consultation.
