import {useState} from 'react';
import './Results.css';
import Ausbauplanung from './Ausbauplanung';
import Zeitreihen from './Zeitreihen';
import Wirtschaftlichkeit from './Wirtschaftlichkeit';
import type {CalculationResult, ResultsTab} from './ResultTypes';

type ResultsProps = {
    hasCalculated: boolean;
    calculationResult: CalculationResult | null;
};

function Results({hasCalculated, calculationResult}: ResultsProps) {
    const [activeResultsTab, setActiveResultsTab] = useState<ResultsTab>('Zeitreihen');

    return (
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
                calculationResult ? (
                    <>
                        <nav className="ResultsTabs" aria-label="Ergebnisansichten">
                            {(['Ausbauplanung', 'Zeitreihen', 'Wirtschaftlichkeit'] as ResultsTab[]).map(tab => (
                                <button
                                    key={tab}
                                    type="button"
                                    className={activeResultsTab === tab ? 'ResultsTab active' : 'ResultsTab'}
                                    onClick={() => setActiveResultsTab(tab)}
                                    aria-selected={activeResultsTab === tab}
                                >
                                    {tab}
                                </button>
                            ))}
                        </nav>
                        {activeResultsTab === 'Zeitreihen' && <Zeitreihen calculationResult={calculationResult} />}
                        {activeResultsTab === 'Wirtschaftlichkeit' && <Wirtschaftlichkeit calculationResult={calculationResult} />}
                        {activeResultsTab === 'Ausbauplanung' && <Ausbauplanung calculationResult={calculationResult} />}
                    </>
                ) : (
                    <p className="ResultsEmpty">Keine Ergebnisdaten vom Backend erhalten.</p>
                )
            )}
        </section>
    );
}

export default Results;
