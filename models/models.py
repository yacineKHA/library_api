from typing import List, Optional
from pydantic import BaseModel
    
class Livre(BaseModel):
    titre: str
    resume: Optional[str] = None
    annee_publication: Optional[int] = None
    serie_id: Optional[int] = None

class Auteur(BaseModel):
    nom: str

class Genre(BaseModel):
    nom: str
    
class Edition(BaseModel):
    nom: str
    isbn: str
    editeur: str
    
class Exemplaire(BaseModel):
    etat: str = "bon"
    etagere_id: Optional[int] = None
    ami_id: Optional[int] = None
    
class LivreComplet(BaseModel):
    titre: str
    resume: Optional[str] = None
    annee_publication: Optional[int] = None
    serie: Optional[str] = None
    auteurs: List[str]
    genres: List[str]
    edition: Edition
    exemplaire : Exemplaire
    
class AmiCreate(BaseModel):
    nom: str
    email: Optional[str] = None
    tel: Optional[str] = None
    
class Prêt(BaseModel):
    exemplaire_id: int
    ami_id: int
    date_pret: Optional[str] = None