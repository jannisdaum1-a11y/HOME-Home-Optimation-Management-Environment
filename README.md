# HOME-Home-Optimation-Management-Environment

## Projektstruktur

Das Projekt ist jetzt in drei getrennte Bereiche aufgeteilt:

- backend/: Python-Domainlogik und Optimierung
- api/: FastAPI-Schnittstelle
- frontend/: React-Frontend (Vite)

Kompatibilitaet fuer bestehende Imports bleibt erhalten:

- assets.*, data_collection.*, optimization.* funktionieren weiter ueber Wrapper im Root.

## Ordneruebersicht

- backend/assets/: Asset-Modelle (z. B. PV, Load, Battery)
- backend/data_collection/: Preise, Wetter, Konfiguration
- backend/optimization/: Optimierungslogik
- api/main.py: FastAPI-App
- frontend/src/: React-Quellcode

## Starten

### 1) Backend-Skript

```bash
python main.py
```

### 2) FastAPI starten

```bash
pip install -r api/requirements.txt
uvicorn api.main:app --reload
```

API ist danach unter http://127.0.0.1:8000 erreichbar.

### 3) Frontend starten

```bash
cd frontend
npm install
npm run dev
```

Frontend laeuft standardmaessig unter http://127.0.0.1:5173.