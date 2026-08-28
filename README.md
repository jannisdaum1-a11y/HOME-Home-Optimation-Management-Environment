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

## Auf Render hosten

Das Projekt besteht auf Render aus zwei Services: einem Python-Webservice fuer
die FastAPI und einer Static Site fuer das React-Frontend.

1. Repository zu GitHub pushen und in Render ueber **New > Blueprint** verbinden.
2. Die Datei `render.yaml` im Repository auswaehlen bzw. automatisch erkennen lassen.
3. Render legt `home-optimization-api` und `home-optimization-frontend` an. Die
	Frontend-Variable `VITE_API_URL` wird automatisch auf die API-URL gesetzt.
4. Nach dem Deployment zuerst `https://<api-url>/health` pruefen und danach die
	Static-Site-URL oeffnen.

Bei manueller Einrichtung gelten diese Werte:

- API: Root Directory leer, Build `pip install -r api/requirements.txt`, Start
  `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
- Frontend: Root Directory leer, Build `cd frontend/reactapp && npm ci && npm run build`,
  Publish Directory `frontend/reactapp/dist`
- Frontend Environment Variable: `VITE_API_URL=https://<api-service>.onrender.com`

Die API benoetigt die Datei `data/spotmarktpreise.csv`; sie wird aus dem
Repository geladen und ist in der Deployment-Konfiguration enthalten.