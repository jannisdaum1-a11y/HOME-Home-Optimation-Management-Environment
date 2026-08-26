import type {CalculationResult} from './ResultTypes';

type AusbauplanungProps = {
    calculationResult: CalculationResult;
};

function Ausbauplanung({calculationResult}: AusbauplanungProps) {
    return (
        <div className="ResultTabPanel">
            <p className="Eyebrow">Ausbauplanung</p>
            <p className="ResultsEmpty">Noch keine Ausbaukennzahlen verfügbar.</p>
            <span>{calculationResult.results.columns.length} Ergebnisgrößen verfügbar</span>
        </div>
    );
}

export default Ausbauplanung;
