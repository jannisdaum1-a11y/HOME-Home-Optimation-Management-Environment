import { useState } from 'react'
import './App.css'

import SidebarLeft from './SidebarLeft'
import SidebarRight from './SidebarRight'
import DragAndDrop from './DragAndDrop'
import Results from './Results'

import assets from './assets/assets.json'

type Asset = {
    image?: string;
    [key: string]: unknown;
};

type Tab = 'configuration' | 'results';

type CalculationResult = {
    objective_value: number | null;
    results: {
        columns: string[];
        index: string[];
        data: (number | string | null)[][];
    };
};

const apiUrl = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

function App() {
    const [objects, setObjects] = useState<Asset[]>([{...assets.Config}]);
    const [selectedObject, setSelectedObject] = useState<Asset|null>(objects[0]??null)
    const [activeTab, setActiveTab] = useState<Tab>('configuration');
    const [hasCalculated, setHasCalculated] = useState(false);
    const [calculationResult, setCalculationResult] = useState<CalculationResult | null>(null);
    const [isCalculating, setIsCalculating] = useState(false);
    const [calculationError, setCalculationError] = useState<string | null>(null);

    async function startCalculation() {
        setIsCalculating(true);
        setCalculationError(null);

        try {
            const response = await fetch(`${apiUrl}/calculate`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({objects}),
            });

            if (!response.ok) {
                throw new Error(`Backend antwortet mit Status ${response.status}`);
            }

            const result: CalculationResult = await response.json();
            setCalculationResult(result);
            setHasCalculated(true);
            setActiveTab('results');
        } catch (error) {
            setCalculationError(error instanceof Error ? error.message : 'Berechnung konnte nicht gestartet werden.');
        } finally {
            setIsCalculating(false);
        }
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
            <button type="button" className="CalculateButton" onClick={startCalculation} disabled={isCalculating}>
                <span aria-hidden="true">→</span>
                {isCalculating ? 'Wird berechnet...' : 'Berechnung starten'}
            </button>
        </div>

        {calculationError && <p className="CalculationError" role="alert">{calculationError}</p>}

        <div className={activeTab === 'results' ? 'MainContent results-mode' : 'MainContent'}>
        {activeTab === 'configuration' && (
            <aside>
                <SidebarLeft></SidebarLeft>
            </aside>
        )}
        
        <div className='Workspace' 
        onKeyDown={(e)=>e.key ==='Escape'?setSelectedObject(objects[0])??null:null}
        tabIndex={0}>
            <main className="ViewContent">
                {activeTab === 'configuration' ? (
                    <DragAndDrop
                        objects={objects}
                        setObjects={setObjects}
                        setSelectedObject={setSelectedObject}
                    ></DragAndDrop>
                ) : (
                    <Results
                        hasCalculated={hasCalculated}
                        calculationResult={calculationResult}
                    ></Results>
                )}
            </main>

        </div>

        {activeTab === 'configuration' && (
            <aside className="InspectorColumn">
                <SidebarRight selectedAsset={selectedObject} setSelectedAsset={setSelectedObject} setAssets={setObjects}></SidebarRight>
            </aside>
        )}
        </div>  
        {isCalculating && (
            <div className="CalculationOverlay" role="status" aria-live="polite" aria-label="Berechnung läuft">
                <div className="CalculationLoader">
                    <span className="Spinner" aria-hidden="true"></span>
                    <strong>Berechnung läuft...</strong>
                    <span>Bitte warten</span>
                </div>
            </div>
        )}
        </div>
    )
}

export default App
