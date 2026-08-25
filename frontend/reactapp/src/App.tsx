import { useState } from 'react'
import './App.css'

import SidebarLeft from './SidebarLeft'
import SidebarRight from './SidebarRight'
import DragAndDrop from './DragAndDrop'

type Asset = {
    image: string;
    [key: string]: unknown;
};

type Tab = 'configuration' | 'results';

function App() {
    const [objects, setObjects] = useState<Asset[]>([]);
    const [selectedObject, setSelectedObject] = useState<Asset|null>(null)
    const [activeTab, setActiveTab] = useState<Tab>('configuration');
    const [hasCalculated, setHasCalculated] = useState(false);

    function startCalculation() {
        setHasCalculated(true);
        setActiveTab('results');
    }

    const totalCapacity = objects.reduce((total, object) =>
        total + (typeof object.Capacity === 'number' ? object.Capacity : 0), 0
    );
    
    return (
        <div className="AppShell">
        <div className="TopBar">
            <nav className="Tabs" aria-label="Ansichten">
                <button
                    type="button"
                    className={activeTab === 'configuration' ? 'Tab active' : 'Tab'}
                    onClick={() => setActiveTab('configuration')}
                >
                    Konfiguration
                </button>
                <button
                    type="button"
                    className={activeTab === 'results' ? 'Tab active' : 'Tab'}
                    onClick={() => setActiveTab('results')}
                >
                    Ergebnisse
                </button>
            </nav>
            <button type="button" className="CalculateButton" onClick={startCalculation}>
                <span aria-hidden="true">→</span>
                Berechnung starten
            </button>
        </div>

        <div className={activeTab === 'results' ? 'MainContent results-mode' : 'MainContent'}>
        {activeTab === 'configuration' && (
            <aside>
                <SidebarLeft></SidebarLeft>
            </aside>
        )}
        
        <div className='Workspace'>
            <main className="ViewContent">
                {activeTab === 'configuration' ? (
                    <DragAndDrop
                        objects={objects}
                        setObjects={setObjects}
                        setSelectedObject={setSelectedObject}
                    ></DragAndDrop>
                ) : (
                    <section className="ResultsView" aria-labelledby="results-title">
                        <div className="ResultsHeader">
                            <div>
                                <p className="Eyebrow">Auswertung</p>
                                <h1 id="results-title">Optimierungsergebnisse</h1>
                            </div>
                            <span className={hasCalculated ? 'Status ready' : 'Status'}>
                                {hasCalculated ? 'Berechnung abgeschlossen' : 'Noch keine Berechnung'}
                            </span>
                        </div>
                        {!hasCalculated ? (
                            <p className="ResultsEmpty">Platziere Anlagen in der Konfiguration und starte anschließend die Berechnung.</p>
                        ) : (
                            <div className="ResultGrid">
                                <article className="ResultCard result-primary">
                                    <span>Komponenten</span>
                                    <strong>{objects.length}</strong>
                                    <small>im System platziert</small>
                                </article>
                                <article className="ResultCard">
                                    <span>Gesamtkapazität</span>
                                    <strong>{totalCapacity.toLocaleString('de-DE')} <small>kWh</small></strong>
                                    <small>konfigurierte Kapazität</small>
                                </article>
                                <article className="ResultCard">
                                    <span>Systemstatus</span>
                                    <strong>Bereit</strong>
                                    <small>Ergebnisdaten verfügbar</small>
                                </article>
                            </div>
                        )}
                    </section>
                )}
            </main>

        </div>

        {activeTab === 'configuration' && (
            <aside className="InspectorColumn">
                <SidebarRight selectedAsset={selectedObject} setSelectedAsset={setSelectedObject} setAssets={setObjects}></SidebarRight>
            </aside>
        )}
        </div>  
        </div>
    )
}

export default App
