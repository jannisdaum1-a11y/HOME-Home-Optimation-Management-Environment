import { useState } from 'react'
import './App.css'

import SidebarLeft from './SidebarLeft'
import SidebarRight from './SidebarRight'
import DragAndDrop from './DragAndDrop'
import Results from './Results'

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
                    <Results objects={objects} hasCalculated={hasCalculated}></Results>
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
