# Jonathan

Lecteur musical de bureau construit avec PySide6, pygame et SQLite.

## Captures d'écran

![Jonathan — capture A](<./capture a.png>)

![Jonathan — capture B](<./capture b.png>)

## Installation

Depuis la racine du projet, crée un environnement virtuel puis installe les
dépendances :

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Lancement

```powershell
python main.py
```

## Créer l'exécutable Windows

Depuis la racine du projet, lancez le script PowerShell :

```powershell
.\build_windows.ps1
```

Le script installe PyInstaller et les dépendances dans `.venv`, puis crée
`dist\Jonathan\Jonathan.exe`. Envoyez ou copiez **tout le dossier**
`dist\Jonathan` : l'exécutable dépend des fichiers qui l'accompagnent.
L'exécutable possède l'icône de Jonathan et l'application n'a pas besoin de
Python installé sur le PC destinataire.

Pour une distribution publique, signez l'exécutable avec un certificat de
signature de code afin de limiter les avertissements Windows SmartScreen.

## Fonctionnalités

- Import de fichiers MP3, WAV et OGG.
- Affichage des titres, artistes, albums et durées, avec recherche dans la
  bibliothèque et actualisation des métadonnées.
- Bibliothèque locale persistante (métadonnées et chemins sauvegardés dans
  SQLite).
- Pochettes intégrées affichées dans le lecteur et sur les cartes d'albums.
- Albums regroupés par artiste dans une vue dédiée.
- Vue dédiée aux artistes de la collection.
- Thème clair ou sombre, avec mémorisation du choix.
- Page « En lecture » avec pochette grand format et commandes synchronisées.
- Navigation dans la bibliothèque et la file de lecture.
- Lecture, pause, morceau précédent/suivant, progression et volume.
- Lecture aléatoire, répétition de la file ou d'un morceau, et mode muet.
- Lecture automatique du morceau suivant à la fin du morceau en cours.

La base de données est enregistrée dans `%APPDATA%\JonathanMusicPlayer` sous
Windows et dans `$XDG_DATA_HOME/jonathan-music-player` (ou
`~/.local/share/jonathan-music-player`) sous Linux/macOS.
