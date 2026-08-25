import './Results.css';

type ResultsProps = {
    hasCalculated: boolean;
    calculationResult: {
        objective_value: number | null;
        results: {
            columns: string[];
            index: string[];
            data: (number | string | null)[][];
        };
    } | null;
};

function Results({hasCalculated, calculationResult}: ResultsProps) {
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
                        <p className="ObjectiveValue">
                            Zielfunktionswert: <strong>{calculationResult.objective_value ?? 'n/a'}</strong>
                        </p>
                        <div className="ResultTableWrapper">
                            <table className="ResultTable">
                                <thead>
                                    <tr>
                                        <th>Zeitpunkt</th>
                                        {calculationResult.results.columns.map(column => <th key={column}>{column}</th>)}
                                    </tr>
                                </thead>
                                <tbody>
                                    {calculationResult.results.data.map((row, rowIndex) => (
                                        <tr key={calculationResult.results.index[rowIndex]}>
                                            <th>{calculationResult.results.index[rowIndex]}</th>
                                            {row.map((value, columnIndex) => <td key={`${rowIndex}-${columnIndex}`}>{String(value ?? '-')}</td>)}
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </>
                ) : (
                    <p className="ResultsEmpty">Keine Ergebnisdaten vom Backend erhalten.</p>
                )
            )}
        </section>
    );
}

export default Results;
