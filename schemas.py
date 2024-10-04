from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date

class UtilisateurCreate(BaseModel):
    nom: str
    email: EmailStr
    telephone: Optional[str] = None
    mot_de_passe: str

class UtilisateurRead(BaseModel):
    id_utilisateur: int
    nom: str
    email: EmailStr
    telephone: Optional[str] = None
    is_admin: bool

    class Config:
        from_attributes = True

class LivreCreate(BaseModel):
    titre: str
    auteur: Optional[str] = None
    date_publication: Optional[date] = None
    genre: Optional[str] = None

class LivreRead(BaseModel):
    id_livre: int
    titre: str
    auteur: Optional[str] = None
    date_publication: Optional[date] = None
    genre: Optional[str] = None
    disponibilite: bool
    
    class Config:
        from_attributes = True
        
class LivreUpdate(BaseModel):
    titre: Optional[str] = None
    auteur: Optional[str] = None
    date_publication: Optional[date] = None
    genre: Optional[str] = None
    disponibilite: Optional[bool] = None
    
class Livre(BaseModel):
    id_livre: int
    titre: str
    auteur: Optional[str] = None
    date_publication: Optional[date] = None
    genre: Optional[str] = None
    disponibilite: Optional[bool] = None

    class Config:
        orm_mode = True

class EmpruntCreate(BaseModel):
    id_livre: int
    date_emprunt: date

class EmpruntRead(BaseModel):
    id_emprunt: int
    id_utilisateur: int
    id_livre: int
    date_emprunt: date
    date_retour: Optional[date] = None

    class Config:
        from_attributes = True
