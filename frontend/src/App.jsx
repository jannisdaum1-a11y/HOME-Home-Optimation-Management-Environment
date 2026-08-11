import { useMemo, useState } from "react";

const defaultApiBase = "http://127.0.0.1:8000";

export default function App() {
  const [apiBase, setApiBase] = useState(defaultApiBase);
  const [status, setStatus] = useState("Noch nicht geprueft");

  const healthUrl = useMemo(() => `${apiBase}/health`, [apiBase]);

  const checkHealth = async () => {
    setStatus("Pruefe...");
    try {
      const res = await fetch(healthUrl);
      const data = await res.json();
      setStatus(`API erreichbar: ${data.status}`);
    } catch (err) {
      setStatus("API nicht erreichbar");
    }
  };

  return (
    <main className="app-shell">
      <section className="panel">
        <h1>HOME Optimization</h1>
        <p>Frontend mit React, verbunden mit deiner FastAPI-Schnittstelle.</p>

        <label htmlFor="apiBase">FastAPI Base URL</label>
        <input
          id="apiBase"
          value={apiBase}
          onChange={(e) => setApiBase(e.target.value)}
        />

        <button onClick={checkHealth}>Health-Check</button>
        <p>{status}</p>
      </section>
    </main>
  );
}
