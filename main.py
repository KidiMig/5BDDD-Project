from fastapi import FastAPI, Depends, HTTPException, status, Security
from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from database import SessionLocal, engine
from models import Base, Utilisateur
import models
from utils import ALGORITHM, SECRET_KEY, create_access_token
from jose import JWTError, jwt
from pydantic import BaseModel


import crud, schemas

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dépendance pour obtenir la session de la base de données
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class TokenData(BaseModel):
    email: Optional[str] = None
    is_admin: Optional[bool] = False

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},  
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        is_admin: bool = payload.get("is_admin", False)
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email, is_admin=is_admin)
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user

@app.get("/protected-route/")
def protected_route(current_user: Utilisateur = Depends(get_current_user)):
    return {"message": f"Bonjour {current_user.nom}, vous êtes authentifié."}

# Authentification via token
@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.email, "is_admin": user.is_admin})
    return {"access_token": access_token, "token_type": "bearer"}        

# Endpoint pour créer un utilisateur
# Créer un utilisateur
@app.post("/utilisateurs/", response_model=schemas.UtilisateurRead)
def create_utilisateur(user: schemas.UtilisateurCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email déjà enregistré")
    return crud.create_user(db=db, user=user)

# Endpoints pour les livres
# Créer un livre
@app.post("/livres/", response_model=schemas.LivreRead)
def create_livre(livre: schemas.LivreCreate, db: Session = Depends(get_db)):
    return crud.create_livre(db=db, livre=livre)

# Mettre a jour un livre
@app.put("/livres/{livre_id}", response_model=schemas.Livre)
def update_livre(livre_id: int, livre: schemas.LivreUpdate, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    db_livre = crud.get_livre_by_id(db, livre_id=livre_id)
    if db_livre is None:
        raise HTTPException(status_code=404, detail="Livre not found")
    return crud.update_livre(db=db, livre_id=livre_id, livre=livre)

# Retourner un livre
@app.post("/retour-livre/{id_emprunt}")
def return_livre(id_emprunt: int, db: Session = Depends(get_db), current_user: models.Utilisateur = Depends(get_current_user)):
    return crud.return_livre(db=db, emprunt_id=id_emprunt, user_id=current_user.id_utilisateur)

# Recherche de livre
@app.get("/livres/search", response_model=List[schemas.Livre])
def search_livres(titre: Optional[str] = None, auteur: Optional[str] = None, genre: Optional[str] = None, db: Session = Depends(get_db)):
    return crud.search_livres(db=db, titre=titre, auteur=auteur, genre=genre)

@app.get("/livres/{id_livre}", response_model=schemas.LivreRead)
def get_livre(id_livre: int, db: Session = Depends(get_db)):
    """
    Récupérer les détails d'un livre spécifique à partir de son id
    """
    livre = db.query(models.Livre).filter(models.Livre.id_livre == id_livre).first()

    if not livre:
        raise HTTPException(status_code=404, detail="Livre non trouvé")

    return livre

@app.delete("/livres/{livre_id}")
def delete_livre(livre_id: int, current_user: Utilisateur = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Accès refusé")
    return crud.delete_livre(db=db, livre_id=livre_id)

# Endpoints pour les emprunts
# Créer un emprunt
@app.post("/emprunts/", response_model=schemas.EmpruntRead)
def create_emprunt(emprunt: schemas.EmpruntCreate, db: Session = Depends(get_db), current_user: models.Utilisateur = Depends(get_current_user)):
    return crud.create_emprunt(db=db, emprunt=emprunt, user_id=current_user.id_utilisateur)

# Emprunt qui appartiens a un utilisateur
@app.get("/emprunts-user/", response_model=List[schemas.EmpruntRead])
def get_emprunts_by_user(db: Session = Depends(get_db), current_user: models.Utilisateur = Depends(get_current_user)):
    return crud.get_emprunts_by_user(db=db, user_id=current_user.id_utilisateur)

# Historique des emprunts des utilisateurs
@app.get("/historique-emprunts/", response_model=List[schemas.EmpruntRead])
def get_historique_emprunts(db: Session = Depends(get_db), current_user: models.Utilisateur = Depends(get_current_user)):
    return crud.get_historique_emprunts(db=db, user_id=current_user.id_utilisateur)

@app.get("/emprunts-actuels/", response_model=List[schemas.EmpruntRead])
def get_emprunts_actuels(db: Session = Depends(get_db), current_user: models.Utilisateur = Depends(get_current_user)):
    
    emprunts = db.query(models.Emprunt).filter(
        models.Emprunt.id_utilisateur == current_user.id_utilisateur,
        models.Emprunt.date_retour == None  
    ).all()

    if not emprunts:
        raise HTTPException(status_code=404, detail="Aucun emprunt en cours.")

    return emprunts