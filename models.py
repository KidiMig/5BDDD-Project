from sqlalchemy import Column, Identity, Integer, String, Date, ForeignKey, Boolean, UniqueConstraint, DateTime, func
from sqlalchemy.orm import relationship
from database import Base

class Utilisateur(Base):
    __tablename__ = 'Utilisateur'
    
    id_utilisateur = Column(Integer, Identity(start=1), primary_key=True)
    nom = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    telephone = Column(String(20))
    mot_de_passe = Column(String(255), nullable=False)  # Stockage du mot de passe haché
    date_creation = Column(DateTime, server_default=func.sysdate())
    is_admin = Column(Boolean, default=False)
    
    emprunts = relationship("Emprunt", back_populates="utilisateur")

class Livre(Base):
    __tablename__ = 'Livre'
    
    id_livre = Column(Integer, Identity(start=1), primary_key=True)
    titre = Column(String(255), nullable=False)
    auteur = Column(String(100))
    date_publication = Column(Date)
    genre = Column(String(50))
    disponibilite = Column(Boolean, default=True)
    
    emprunts = relationship("Emprunt", back_populates="livre")
    
class Emprunt(Base):
    __tablename__ = 'Emprunt'
    __table_args__ = (UniqueConstraint('id_utilisateur', 'id_livre', 'date_emprunt', name='UC_Emprunt'), {"extend_existing": True})
    
    id_emprunt = Column(Integer, Identity(start=1), primary_key=True)
    id_utilisateur = Column(Integer, ForeignKey('Utilisateur.id_utilisateur'), nullable=False)
    id_livre = Column(Integer, ForeignKey('Livre.id_livre'), nullable=False)
    date_emprunt = Column(DateTime, server_default=func.sysdate())
    date_retour = Column(Date)
    
    utilisateur = relationship("Utilisateur", back_populates="emprunts")
    livre = relationship("Livre", back_populates="emprunts")