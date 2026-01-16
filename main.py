from datetime import date
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi import UploadFile, File
from fastapi.staticfiles import StaticFiles
from models.models import AmiCreate, Auteur, Genre, Livre, LivreComplet, Prêt
import sqlite3
import os


app = FastAPI(title="Library API")
DB = "library.db"

origins = [
    "http://localhost:5173",
]

UPLOAD_DIR = "images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.mount("/images", StaticFiles(directory="images"), name="images")


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],    
)

# connexion à la bdd
def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

@app.post("/livres/")
def create_livre_complet(livre: LivreComplet):
    conn = get_db()
    try:
        conn.execute("BEGIN") #permet de lancer les transactions seulement au commit

        # SERIE
        serie_id = None
        if livre.serie:
            conn.execute(
                "INSERT OR IGNORE INTO serie (nom) VALUES (?)",
                (livre.serie,)
            )
            serie_id = conn.execute(
                "SELECT id FROM serie WHERE nom = ?",
                (livre.serie,)
            ).fetchone()["id"]

        # LIVRE
        req = conn.execute(
            """
            INSERT INTO livre (titre, resume, annee_publication, serie_id)
            VALUES (?, ?, ?, ?)
            """,
            (livre.titre, livre.resume, livre.annee_publication, serie_id)
        )
        livre_id = req.lastrowid

        # AUTEURS
        for nom in livre.auteurs:
            conn.execute(
                "INSERT OR IGNORE INTO auteur (nom) VALUES (?)",
                (nom,)
            )
            auteur_id = conn.execute(
                "SELECT id FROM auteur WHERE nom = ?",
                (nom,)
            ).fetchone()["id"]

            conn.execute(
                "INSERT INTO livre_auteur (livre_id, auteur_id) VALUES (?, ?)",
                (livre_id, auteur_id)
            )

        # GENRES
        for nom in livre.genres:
            conn.execute(
                "INSERT OR IGNORE INTO genre (nom) VALUES (?)",
                (nom,)
            )
            genre_id = conn.execute(
                "SELECT id FROM genre WHERE nom = ?",
                (nom,)
            ).fetchone()["id"]

            conn.execute(
                "INSERT INTO livre_genre (livre_id, genre_id) VALUES (?, ?)",
                (livre_id, genre_id)
            )

        # EDITEUR
        conn.execute(
            "INSERT OR IGNORE INTO editeur (nom) VALUES (?)",
            (livre.edition.editeur,)
        )
        editeur_id = conn.execute(
            "SELECT id FROM editeur WHERE nom = ?",
            (livre.edition.editeur,)
        ).fetchone()["id"]

        # Edition
        
        co_edition = conn.execute(
            """
            INSERT INTO edition (nom, isbn, livre_id, editeur_id)
            VALUES (?, ?, ?, ?)
            """,
            (
                livre.edition.nom,
                livre.edition.isbn,
                livre_id,
                editeur_id
            )
        )
        
        edition_id = co_edition.lastrowid
        
        # Exemplaire
        conn.execute(
            "INSERT INTO exemplaire (etat, edition_id, etagere_id) VALUES (?, ?, ?)",
            (
                livre.exemplaire.etat,
                edition_id,
                None
            )
        )

       

        conn.commit()
        return {"success": True, "livre_id": livre_id}


    except Exception as e:
        conn.rollback() #annule les requetes si erreurs
        print("Erreur: ", e)
        return {"success": False, "message": f"Erreur: {e}"}
    finally:
        conn.close()

        

@app.get("/livres/")
def read_livres():
    conn = get_db()
    try:
        req = conn.execute("SELECT * FROM livre").fetchall()
        return [dict(row) for row in req]
    except Exception as e:
        return {"success": False, "message": f"Erreur: {e}"}
    finally:
        conn.close()

@app.get("/livres/{livre_id}")
def read_livre(livre_id: int):
    conn = get_db()
    req = conn.execute("SELECT * FROM livre WHERE id = ?", (livre_id,)).fetchone()
    conn.close()
    if not req:
        raise HTTPException(status_code=404, detail="Livre non trouvé")
    return dict(req)


@app.post("/auteurs/")
def create_auteur(auteur: Auteur):
    conn = get_db()
    try:
        req = conn.execute("INSERT INTO auteur (nom) VALUES (?)", (auteur.nom,))
        conn.commit()
        return {"success": True, "message": "Auteur créé", "id": req.lastrowid}
    except sqlite3.IntegrityError as e:
        return {"success": False, "message": f"Erreur: {e}"}
    finally:
        conn.close()

@app.get("/auteurs/")
def read_auteurs():
    conn = get_db()
    req = conn.execute("SELECT * FROM auteur").fetchall()
    conn.close()
    return [dict(row) for row in req]


@app.post("/genres/")
def create_genre(genre: Genre):
    conn = get_db()
    try:
        req = conn.execute("INSERT INTO genre (nom) VALUES (?)", (genre.nom,))
        conn.commit()
        return {"success": True, "message": "Genre créé", "id": req.lastrowid}
    except sqlite3.IntegrityError as e:
        return {"success": False, "message": f"Erreur: {e}"}
    finally:
        conn.close()

@app.get("/genres/")
def read_genres():
    conn = get_db()
    req = conn.execute("SELECT * FROM genre").fetchall()
    conn.close()
    return {"genres": [dict(row) for row in req]}


@app.post("/livres/{livre_id}/auteurs/{auteur_id}")
def add_auteur_to_livre(livre_id: int, auteur_id: int):
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO livre_auteur (livre_id, auteur_id) VALUES (?, ?)",
            (livre_id, auteur_id)
        )
        conn.commit()
        return {"success": True, "message": "Auteur ajouté au livre"}
    except sqlite3.IntegrityError as e:
        return {"success": False, "message": f"Erreur: {e}"}
    finally:
        conn.close()

@app.post("/livres/{livre_id}/genres/{genre_id}")
def add_genre_to_livre(livre_id: int, genre_id: int):
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO livre_genre (livre_id, genre_id) VALUES (?, ?)",
            (livre_id, genre_id)
        )
        conn.commit()
        return {"success": True, "message": "Genre ajouté au livre"}
    except sqlite3.IntegrityError as e:
        return {"success": False, "message": f"Erreur: {e}"}
    finally:
        conn.close()
        
@app.get("/amis/")
def read_amis():
    conn = get_db()
    req = conn.execute("SELECT * FROM ami").fetchall()
    conn.close()
    return [dict(row) for row in req]

@app.post("/amis/")
def create_ami(ami: AmiCreate):   
    conn = get_db()
    try:
        req = conn.execute(
            "INSERT INTO ami (nom, email, tel) VALUES (?, ?, ?)", 
            (ami.nom, ami.email, ami.tel)
        )
        conn.commit()
        return {"success": True, "message": "Ami créé", "id": req.lastrowid}
    except sqlite3.IntegrityError as e:
        return {"success": False, "message": f"Erreur: {e}"}
    finally:
        conn.close()

@app.post("/prets/")
def create_pret(pret: Prêt):
    conn = get_db()
    try:
        # verif que l'exemplaire existe
        exemplaire = conn.execute(
            "SELECT id FROM exemplaire WHERE id = ?", (pret.exemplaire_id,)
        ).fetchone()
        if not exemplaire:
            return {"success": False, "message": "Exemplaire non trouvé"}
        
        # Vérif que l'ami existe bien
        ami = conn.execute(
            "SELECT id FROM ami WHERE id = ?", (pret.ami_id,)
        ).fetchone()
        if not ami:
            return {"success": False, "message": "Ami non trouvé"}
        
        # Vérif que exemplaire pas déjà prêté
        deja_prete = conn.execute(
            "SELECT id FROM pret WHERE exemplaire_id = ? AND date_retour IS NULL",
            (pret.exemplaire_id,)
        ).fetchone()
        if deja_prete:
            return {"success": False, "message": "Exemplaire déjà emprunté"}
        
        # si ok faire le prêt
        req = conn.execute(
            """
            INSERT INTO pret (exemplaire_id, ami_id, date_pret)
            VALUES (?, ?, ?)
            """,
            (pret.exemplaire_id, pret.ami_id, date.today())
        )
        conn.commit()
        return {"success": True, "message": "Prêt créé", "id": req.lastrowid}
        
    except sqlite3.IntegrityError as e:
        return {"success": False, "message": f"Erreur d'intégrité: {e}"}
    except Exception as e:
        conn.rollback()
        return {"success": False, "message": f"Erreur: {e}"}
    finally:
        conn.close()
        
@app.get("/prets/")
def read_prets():
    conn = get_db()
    try:
        req = conn.execute("SELECT * FROM pret").fetchall()
        return [dict(row) for row in req]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {e}")
    finally:
        conn.close()

@app.get("/prets/en-cours")
def read_prets_en_cours():
    conn = get_db()
    req = conn.execute("""
        SELECT pret.*, ami.nom as ami_nom, livre.titre
        FROM pret
        JOIN ami ON pret.ami_id = ami.id
        JOIN exemplaire ON pret.exemplaire_id = exemplaire.id
        JOIN edition ON exemplaire.edition_id = edition.id
        JOIN livre ON edition.livre_id = livre.id
        WHERE pret.date_retour IS NULL
    """).fetchall()
    conn.close()
    return [dict(row) for row in req]

@app.delete("/prets/{pret_id}/")
def retour_pret(pret_id: int):
    conn = get_db()
    try:
        req = conn.execute(
            """
            DELETE FROM pret
            WHERE id = ? AND date_retour IS NULL
            """,
            (pret_id,)
        )
        if req.rowcount == 0:
            return {"success": False, "message": "Prêt non trouvé ou déjà retourné"}
        conn.commit()
        return {"success": True, "message": "Prêt retourné avec succès"}
    except Exception as e:
        conn.rollback()
        return {"success": False, "message": f"Erreur: {e}"}
    finally:
        conn.close()


@app.post("/livres/{livre_id}/images")
async def upload_image(livre_id: int, file: UploadFile = File(...)):
    conn = get_db()
    try:
        livre = conn.execute("SELECT id FROM livre WHERE id = ?", (livre_id,)).fetchone()
        if not livre:
            raise HTTPException(status_code=404, detail="Livre non trouvé")

        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in [".jpg", ".jpeg", ".png", ".webp"]:
            raise HTTPException(status_code=400, detail="Format non supporté")

        filename = f"livre_{livre_id}_{uuid.uuid4().hex}{ext}"
        filepath = os.path.join(UPLOAD_DIR, filename)

        content = await file.read()
        with open(filepath, "wb") as f:
            f.write(content)

        image_url = f"/images/{filename}"

        conn.execute("UPDATE livre SET image_url = ? WHERE id = ?", (image_url, livre_id))

        conn.commit()
        return {"success": True, "image_url": image_url}

    finally:
        conn.close()
