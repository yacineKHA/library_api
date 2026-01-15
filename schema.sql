PRAGMA foreign_keys = ON;

CREATE TABLE auteur (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  nom TEXT NOT NULL UNIQUE
);

CREATE TABLE genre (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  nom TEXT NOT NULL UNIQUE
);

CREATE TABLE editeur (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  nom TEXT NOT NULL UNIQUE
);

CREATE TABLE serie (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  nom TEXT NOT NULL
);

CREATE TABLE etagere (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  nom TEXT
);

CREATE TABLE ami (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  nom TEXT NOT NULL,
  email TEXT,
  tel TEXT
);


CREATE TABLE livre (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  titre TEXT NOT NULL,
  resume TEXT,
  annee_publication INTEGER,
  serie_id INTEGER,
  FOREIGN KEY (serie_id) REFERENCES serie(id)
);

CREATE TABLE livre_auteur (
  livre_id INTEGER NOT NULL,
  auteur_id INTEGER NOT NULL,
  PRIMARY KEY (livre_id, auteur_id),
  FOREIGN KEY (livre_id) REFERENCES livre(id) ON DELETE CASCADE,
  FOREIGN KEY (auteur_id) REFERENCES auteur(id) ON DELETE CASCADE
);

CREATE TABLE livre_genre (
  livre_id INTEGER NOT NULL,
  genre_id INTEGER NOT NULL,
  PRIMARY KEY (livre_id, genre_id),
  FOREIGN KEY (livre_id) REFERENCES livre(id) ON DELETE CASCADE,
  FOREIGN KEY (genre_id) REFERENCES genre(id) ON DELETE CASCADE
);

CREATE TABLE edition (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  nom TEXT,
  isbn TEXT UNIQUE,
  livre_id INTEGER NOT NULL,
  editeur_id INTEGER NOT NULL,
  FOREIGN KEY (livre_id) REFERENCES livre(id) ON DELETE CASCADE,
  FOREIGN KEY (editeur_id) REFERENCES editeur(id)
);

CREATE TABLE exemplaire (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  etat TEXT NOT NULL DEFAULT 'BON',
  edition_id INTEGER NOT NULL,
  etagere_id INTEGER,
  FOREIGN KEY (edition_id) REFERENCES edition(id) ON DELETE CASCADE,
  FOREIGN KEY (etagere_id) REFERENCES etagere(id)
);

CREATE TABLE pret (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  exemplaire_id INTEGER NOT NULL,
  ami_id INTEGER NOT NULL,
  date_pret TEXT NOT NULL,
  date_retour TEXT,
  FOREIGN KEY (exemplaire_id) REFERENCES exemplaire(id) ON DELETE CASCADE,
  FOREIGN KEY (ami_id) REFERENCES ami(id)
);