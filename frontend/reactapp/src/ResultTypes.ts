export type CalculationResult = {
    objective_value: number | null;
    results: {
        columns: string[];
        index: string[];
        data: (number | string | null)[][];
    };
    initial_capex?: Record<string, number | null>;
};

export type ResultsTab = 'Ausbauplanung' | 'Zeitreihen' | 'Wirtschaftlichkeit';
