import './Results.css';

type Asset = {
    image: string;
    [key: string]: unknown;
};

type ResultsProps = {
    objects: Asset[];
    hasCalculated: boolean;
};

function Results({objects, hasCalculated}: ResultsProps) {
    const totalCapacity = objects.reduce((total, object) =>
        total + (typeof object.Capacity === 'number' ? object.Capacity : 0), 0
    );

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
    );
}

export default Results;
