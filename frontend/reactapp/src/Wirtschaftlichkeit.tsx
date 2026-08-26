import type {CalculationResult} from './ResultTypes';

type WirtschaftlichkeitProps = {
    calculationResult: CalculationResult;
};

function Wirtschaftlichkeit({calculationResult}: WirtschaftlichkeitProps) {
    return (
        <div className="ResultTabPanel">
            <p className="Eyebrow">Wirtschaftlichkeit</p>
            <p className="ObjectiveValue">
                Zielfunktionswert: <strong>{calculationResult.objective_value ?? 'n/a'}</strong>
            </p>
        </div>
    );
}

export default Wirtschaftlichkeit;
