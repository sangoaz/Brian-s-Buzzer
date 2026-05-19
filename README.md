# Brian's Buzzer

Brian's Buzzer est une application de buzzer en temps réel permettant à plusieurs joueurs de rejoindre une salle et de répondre à des quiz, blind tests ou jeux en soirée.

## Fonctionnalités

- Création d'une salle avec un code unique
- Rejoindre une salle via un code
- Bouton buzzer sur téléphone ou ordinateur
- Blocage des autres buzzers lorsqu'un joueur a buzzé
- Affichage en temps réel du joueur ayant buzzé
- Synchronisation instantanée entre tous les participants

## Stack technique

### Backend

- Python
- FastAPI
- WebSockets

### Frontend

- Next.js
- React
- Tailwind CSS

## Installation et lancement

### Prérequis

- Python 3.11+
- Node.js 18+

### Backend

1. Aller dans le dossier backend :
   ```bash
   cd backend
   ```
2. Créer et activer un environnement virtuel :
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
3. Installer les dépendances :
   ```bash
   pip install -r requirements.txt
   ```
4. Lancer le serveur :
   ```bash
   uvicorn app.main:app --reload
   ```

### Frontend

1. Aller dans le dossier frontend :
   ```bash
   cd frontend
   ```
2. Installer les dépendances :
   ```bash
   npm install
   ```
3. Lancer le serveur de développement :
   ```bash
   npm run dev
   ```
4. Ouvrir [http://localhost:3000](http://localhost:3000) dans le navigateur.

## Structure du projet

```
backend/
  app/
    main.py
    routes/
    schemas/
    services/
    websocket/
  requirements.txt

frontend/
  src/
    app/
    components/
    hooks/
    services/
    utils/
  package.json
  tailwind.config.js
```

## Licence

MIT

---

Développé avec ❤️ pour les soirées entre amis.
