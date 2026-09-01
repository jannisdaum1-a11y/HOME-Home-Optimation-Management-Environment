import {useEffect, useState} from 'react';
import type {EChartsOption} from 'echarts';
import ReactECharts from 'echarts-for-react';
import './Results.css';
import Ausbauplanung from './Ausbauplanung';
import Zeitreihen from './Zeitreihen';
import Wirtschaftlichkeit from './Wirtschaftlichkeit';
import { defaultCalculationName, type CalculationResult, type CalculationResultEntry, type ResultsTab } from './ResultTypes';

type ResultsProps = {
    hasCalculated: boolean;
    calculationResult: CalculationResult | null;
    resultsHistory: CalculationResultEntry[];
    setResultsHistory: React.Dispatch<React.SetStateAction<CalculationResultEntry[]>>;
};

function Results({hasCalculated, calculationResult, resultsHistory, setResultsHistory}: ResultsProps) {
    const [activeResultsTab, setActiveResultsTab] = useState<ResultsTab>('Zeitreihen');
    const [selectedResultIds, setSelectedResultIds] = useState<string[]>([]);

    useEffect(() => {
        if (!resultsHistory.length) {
            setSelectedResultIds([]);
            return;
        }

        setSelectedResultIds(current => {
            if (current.length === 0) {
                return [resultsHistory[resultsHistory.length - 1].id];
            }

            const validIds = current.filter(id => resultsHistory.some(entry => entry.id === id));
            return validIds.length > 0 ? validIds : [resultsHistory[resultsHistory.length - 1].id];
        });
    }, [resultsHistory]);

    const selectedResults = resultsHistory.filter(entry => selectedResultIds.includes(entry.id));

    const getAusbauChartOption = (result: CalculationResult): EChartsOption => {
        const capacityEntries = result.results.columns
            .map((column, columnIndex) => {
                if (!/^(P_rated_|e_capacity_)/.test(column)) {
                    return null;
                }

                const values = result.results.data
                    .map(row => Number(row[columnIndex] ?? 0))
                    .filter(value => Number.isFinite(value));

                const finalValue = values.length > 0 ? values[values.length - 1] : 0;
                const label = column
                    .replace(/^P_rated_/, '')
                    .replace(/^e_capacity_/, '')
                    .replace(/_[0-9]+$/, '');
                const unit = column.startsWith('e_capacity_') ? 'Wh' : 'W';

                return {label, value: finalValue, unit};
            })
            .filter((entry): entry is {label: string; value: number; unit: string} => entry !== null)
            .sort((a, b) => b.value - a.value);

        return {
            animation: false,
            tooltip: {trigger: 'axis', axisPointer: {type: 'shadow'}},
            grid: {top: 24, right: 24, bottom: 56, left: 64},
            xAxis: {
                type: 'category',
                data: capacityEntries.map(entry => entry.label),
                axisLabel: {rotate: 20, interval: 0},
            },
            yAxis: {type: 'value', name: 'Kapazität'},
            series: [{
                type: 'bar',
                name: 'Ausgebaut',
                data: capacityEntries.map(entry => entry.value),
                itemStyle: {
                    color: '#087f78',
                    borderRadius: [6, 6, 0, 0],
                },
            }],
        };
    };

    const getCapexChartOption = (result: CalculationResult): EChartsOption => {
        const capexEntries = Object.entries(result.initial_capex ?? {}).filter(
            ([key, value]) => key !== 'total_capex' && typeof value === 'number'
        );

        return {
            animation: false,
            tooltip: {trigger: 'axis', axisPointer: {type: 'shadow'}},
            legend: {top: 0},
            grid: {top: 40, right: 24, bottom: 32, left: 64},
            xAxis: {
                type: 'category',
                data: ['Initiale CAPEX'],
            },
            yAxis: {type: 'value', name: '€'},
            series: capexEntries.map(([key, value], index) => ({
                name: key.replace(/^capex_/, ''),
                type: 'bar',
                stack: 'capex',
                emphasis: {focus: 'series'},
                data: [Number(value ?? 0)],
                itemStyle: {color: ['#087f78', '#e8874d', '#4f78a8', '#d25c72', '#8b6faf', '#c4a24c'][index % 6]},
            })),
        };
    };

    const getSystemCostTimeChartOption = (result: CalculationResult): EChartsOption => {
        const costSeries = result.results.columns
            .filter(column => column === 'system_costs' || column === 'system_costs_aggregated')
            .map(column => ({
                name: column === 'system_costs_aggregated' ? 'aggregierte Kosten' : 'Systemkosten',
                data: result.results.data.map(row => {
                    const columnIndex = result.results.columns.indexOf(column);
                    const value = row[columnIndex];
                    return typeof value === 'number' ? value : 0;
                }),
            }));

        return {
            animation: false,
            tooltip: {trigger: 'axis'},
            legend: {top: 0},
            grid: {top: 44, right: 24, bottom: 40, left: 64},
            xAxis: {
                type: 'category',
                data: result.results.index,
                axisLabel: {formatter: value => value.replace('T', ' ').slice(0, 16)},
            },
            yAxis: {
                type: 'value',
                name: '€',
            },
            series: costSeries.map(series => ({
                name: series.name,
                type: 'line',
                smooth: true,
                symbol: 'none',
                data: series.data,
            })),
        };
    };

    const toggleResultSelection = (id: string) => {
        setSelectedResultIds(current => {
            if (current.includes(id)) {
                return current.filter(entryId => entryId !== id);
            }

            return [...current, id];
        });
    };

    const updateCalculationName = (id: string, rawName: string) => {
        const nextName = rawName.trim();

        setResultsHistory(current => current.map((entry) => {
            if (entry.id !== id) {
                return entry;
            }

            const historyIndex = current.findIndex(item => item.id === id);
            return {
                ...entry,
                name: nextName || defaultCalculationName(historyIndex >= 0 ? historyIndex : 0),
            };
        }));
    };

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
                            {(['Ausbauplanung', 'Zeitreihen', 'Wirtschaftlichkeit', 'Vergleich'] as ResultsTab[]).map(tab => (
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
                        {activeResultsTab === 'Vergleich' && (
                            <div className="ResultTabPanel">
                                <div className="ComparisonList">
                                    {resultsHistory.map((entry) => (
                                        <div className="ComparisonItem" key={entry.id}>
                                            <label className="ComparisonSelect">
                                                <input
                                                    type="checkbox"
                                                    checked={selectedResultIds.includes(entry.id)}
                                                    onChange={() => toggleResultSelection(entry.id)}
                                                />
                                                <span>Auswählen</span>
                                            </label>
                                            <label className="ComparisonNameField">
                                                <span>Name</span>
                                                <input
                                                    type="text"
                                                    value={entry.name}
                                                    onChange={(event) => updateCalculationName(entry.id, event.target.value)}
                                                />
                                            </label>
                                        </div>
                                    ))}
                                </div>

                                {selectedResults.length > 0 ? (
                                    <div className="ComparisonSummary">
                                        {selectedResults.map((entry) => (
                                            <article key={entry.id} className="ComparisonCard">
                                                <h3>{entry.name}</h3>
                                                <div className="ComparisonChartGrid">
                                                    <div className="ComparisonChartBlock">
                                                        <h4>Ausbauplanung</h4>
                                                        <ReactECharts option={getAusbauChartOption(entry.result)} style={{height: '260px', width: '100%'}} notMerge />
                                                    </div>
                                                    <div className="ComparisonChartBlock">
                                                        <h4>Systemkosten</h4>
                                                        <ReactECharts option={getSystemCostTimeChartOption(entry.result)} style={{height: '260px', width: '100%'}} notMerge />
                                                    </div>
                                                    <div className="ComparisonChartBlock ComparisonChartBlockWide">
                                                        <h4>Initiale CAPEX</h4>
                                                        <ReactECharts option={getCapexChartOption(entry.result)} style={{height: '260px', width: '100%'}} notMerge />
                                                    </div>
                                                </div>
                                            </article>
                                        ))}
                                    </div>
                                ) : (
                                    <p className="ResultsEmpty">Wähle mindestens eine Rechnung zum Vergleichen aus.</p>
                                )}
                            </div>
                        )}
                    </>
                ) : (
                    <p className="ResultsEmpty">Keine Ergebnisdaten vom Backend erhalten.</p>
                )
            )}
        </section>
    );
}

export default Results;
