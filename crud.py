from datetime import date
from typing import Optional

from fastapi import HTTPException
from models import Utilisateur
import models
import schemas
from utils import hash_password, verify_password
from sqlalchemy.orm import Session
from models import Utilisateur, Livre, Emprunt
from schemas import UtilisateurCreate, LivreCreate, EmpruntCreate

def get_user_by_email(db: Session, email: str):
    return db.query(Utilisateur).filter(Utilisateur.email == email).first()

def create_user(db: Session, user: UtilisateurCreate):
    hashed_pw = hash_password(user.mot_de_passe)
    db_user = Utilisateur(
        nom=user.nom,
        email=user.email,
        telephone=user.telephone,
        mot_de_passe=hashed_pw,
        is_admin=False
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.mot_de_passe):
        return False
    return user

def create_livre(db: Session, livre: LivreCreate):
    db_livre = Livre(
        titre=livre.titre,
        auteur=livre.auteur,
        date_publication=livre.date_publication,
        genre=livre.genre,
        disponibilite=True  # Par défaut, un livre est disponible lorsqu'il est créé
    )
    db.add(db_livre)
    db.commit()
    db.refresh(db_livre)
    return db_livre

# Récupérer la liste de tous les livres avec pagination
def get_livres(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Livre).offset(skip).limit(limit).all()

# Récupérer un livre par son ID
def get_livre_by_id(db: Session, livre_id: int):
    return db.query(Livre).filter(Livre.id_livre == livre_id).first()

# Mettre à jour un livre
def update_livre(db: Session, livre_id: int, livre: schemas.LivreUpdate):
    db_livre = db.query(models.Livre).filter(models.Livre.id_livre == livre_id).first()
    if livre.titre:
        db_livre.titre = livre.titre
    if livre.auteur:
        db_livre.auteur = livre.auteur
    if livre.date_publication:
        db_livre.date_publication = livre.date_publication
    if livre.genre:
        db_livre.genre = livre.genre
    if livre.disponibilite is not None:
        db_livre.disponibilite = livre.disponibilite
    db.commit()
    db.refresh(db_livre)
    return db_livre

# Pour la recherche de livres
def search_livres(db: Session, titre: Optional[str] = None, auteur: Optional[str] = None, genre: Optional[str] = None):
    query = db.query(models.Livre)
    
    if titre:
        query = query.filter(models.Livre.titre.ilike(f"%{titre}%"))
    if auteur:
        query = query.filter(models.Livre.auteur.ilike(f"%{auteur}%"))
    if genre:
        query = query.filter(models.Livre.genre.ilike(f"%{genre}%"))
    
    return query.all()

# Retourner un livre
def return_livre(db: Session, emprunt_id: int, user_id: int):
    # Récupérer l'emprunt
    emprunt = db.query(models.Emprunt).filter(
        models.Emprunt.id_emprunt == emprunt_id,
        models.Emprunt.id_utilisateur == user_id
    ).first()

    # Vérifier si l'emprunt existe
    if not emprunt:
        raise HTTPException(status_code=404, detail="Emprunt non trouvé")

    # Vérifier si le livre a déjà été retourné
    if emprunt.date_retour is not None:
        raise HTTPException(status_code=400, detail="Le livre a déjà été retourné")

    # Mettre à jour la date de retour avec la date du jour
    emprunt.date_retour = date.today()

    # Mettre à jour la disponibilité du livre
    livre = db.query(models.Livre).filter(models.Livre.id_livre == emprunt.id_livre).first()
    livre.disponibilite = 1

    db.commit()
    db.refresh(emprunt)
    return emprunt

# Supprimer un livre
def delete_livre(db: Session, livre_id: int):
    db_livre = get_livre_by_id(db, livre_id)
    if db_livre:
        db.delete(db_livre)
        db.commit()
    return db_livre

# Créer un emprunt
def create_emprunt(db: Session, emprunt: schemas.EmpruntCreate, user_id: int):
    # Vérifier si le livre a déjà été emprunté et n'a pas encore été retourné
    active_emprunt = db.query(models.Emprunt).filter(
        models.Emprunt.id_utilisateur == user_id,
        models.Emprunt.id_livre == emprunt.id_livre,
        models.Emprunt.date_retour == None  # Livre encore emprunté
    ).first()

    if active_emprunt:
        raise HTTPException(status_code=400, detail="Le livre doit être retourné avant d'être emprunté à nouveau.")

    # Créer l'emprunt s'il n'existe pas d'emprunt actif
    db_emprunt = models.Emprunt(
        id_utilisateur=user_id,
        id_livre=emprunt.id_livre,
        date_emprunt=emprunt.date_emprunt
    )
    db.add(db_emprunt)

    # Mettre à jour la disponibilité du livre
    livre = db.query(models.Livre).filter(models.Livre.id_livre == emprunt.id_livre).first()
    livre.disponibilite = 0

    db.commit()
    db.refresh(db_emprunt)
    return db_emprunt

# Récupérer la liste des emprunts avec pagination
def get_emprunts(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Emprunt).offset(skip).limit(limit).all()

# Récupérer un emprunt par son ID
def get_emprunt_by_id(db: Session, emprunt_id: int):
    return db.query(Emprunt).filter(Emprunt.id_emprunt == emprunt_id).first()

def get_emprunts_by_user(db: Session, user_id: int):
    return db.query(models.Emprunt).filter(models.Emprunt.id_utilisateur == user_id).all()

# Mettre à jour un emprunt (par exemple, pour enregistrer la date de retour)
def update_emprunt(db: Session, emprunt_id: int, date_retour):
    db_emprunt = get_emprunt_by_id(db, emprunt_id)
    if db_emprunt:
        db_emprunt.date_retour = date_retour
        db.commit()
        db.refresh(db_emprunt)
    return db_emprunt

# Supprimer un emprunt
def delete_emprunt(db: Session, emprunt_id: int):
    db_emprunt = get_emprunt_by_id(db, emprunt_id)
    if db_emprunt:
        db.delete(db_emprunt)
        db.commit()
    return db_emprunt

def get_historique_emprunts(db: Session, user_id: int):
    return db.query(models.Emprunt).filter(
        models.Emprunt.id_utilisateur == user_id
    ).order_by(models.Emprunt.date_emprunt.desc()).all()
