export type CalculationResult = {
    objective_value: number | null;
    results: {
        columns: string[];
        index: string[];
        data: (number | string | null)[][];
    };
};

export type ResultsTab = 'Ausbauplanung' | 'Zeitreihen' | 'Wirtschaftlichkeit';
