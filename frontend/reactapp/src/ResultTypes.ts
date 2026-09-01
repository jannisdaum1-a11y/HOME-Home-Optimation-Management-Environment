export type CalculationResult = {
    objective_value: number | null;
    results: {
        columns: string[];
        index: string[];
        data: (number | string | null)[][];
    };
    initial_capex?: Record<string, number | null>;
};

export type CalculationResultEntry = {
    id: string;
    name: string;
    result: CalculationResult;
};

export function defaultCalculationName(index: number) {
    return `Rechnung ${index + 1}`;
}

export type ResultsTab = 'Ausbauplanung' | 'Zeitreihen' | 'Wirtschaftlichkeit' | 'Vergleich';
