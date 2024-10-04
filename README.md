# 5BDDD

Projet 5BDDD

## Installation (Windows)

# Creation environnement virtuel & activation

```bash
py -m venv .venv
.venv\Scripts\Activate.ps1
```
# Installation librairie listé dans requirements
```bash
pip install -r requirements.txt
pip freeze
```

# Désactivation de l'environnement virtuel
```bash
deactivate
```

# Démarrage application

# Variables d'environnement à définir (exemple):

```bash
TEST=147852369
BDD_URL=sqlite://:memory:
```

```bash
fastapi dev main.py
```

# Accès au swagger
http://127.0.0.1:8000/docs

# Accès a ma page static
http://127.0.0.1:8000/static/index.html

# Page template 
http://127.0.0.1:8000/items/123?q=test

Connection python - Oracle
Utilisation librairie oracledb (à ajouter dans requirements.txt)
Définir dans .env :

# connect oracledb

```bash
DATABASE_USER=USER
DATABASE_PASSWORD=*************
DATABASE_DSN=localhost:1521/FREEPDB1

DATABASE_TABLE=SCHEMA.TABLE_NAME
```

# Execution de la démo :

```bash
 python3 conn_oracle.py 
 ```