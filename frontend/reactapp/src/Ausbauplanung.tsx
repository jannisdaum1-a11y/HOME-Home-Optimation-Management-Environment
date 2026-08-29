import ReactECharts from 'echarts-for-react';
import type {EChartsOption} from 'echarts';
import type {CalculationResult} from './ResultTypes';

type AusbauplanungProps = {
    calculationResult: CalculationResult;
};

type CapacityEntry = {
    label: string;
    value: number;
    unit: string;
};

function Ausbauplanung({calculationResult}: AusbauplanungProps) {
    const {results} = calculationResult;

    const capacityEntries: CapacityEntry[] = results.columns
        .map((column, columnIndex) => {
            if (!/^(P_rated_|e_capacity_)/.test(column)) {
                return null;
            }

            const values = results.data
                .map(row => Number(row[columnIndex] ?? 0))
                .filter(value => Number.isFinite(value));

            const finalValue = values.length > 0 ? values[values.length - 1] : 0;
            const label = column
                .replace(/^P_rated_/, '')
                .replace(/^e_capacity_/, '')
                .replace(/_[0-9]+$/, '');
            const unit = column.startsWith('e_capacity_') ? 'Wh' : 'W';

            return {
                label,
                value: finalValue,
                unit,
            };
        })
        .filter((entry): entry is CapacityEntry => entry !== null)
        .sort((a, b) => b.value - a.value);

    const chartOption: EChartsOption = {
        animation: false,
        tooltip: {trigger: 'axis', axisPointer: {type: 'shadow'}},
        grid: {top: 24, right: 24, bottom: 56, left: 64},
        xAxis: {
            type: 'category',
            data: capacityEntries.map(entry => entry.label),
            axisLabel: {rotate: 20, interval: 0},
        },
        yAxis: {
            type: 'value',
            name: 'Kapazität',
        },
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

    return (
        <div className="ResultTabPanel">
            <p className="Eyebrow">Ausbauplanung</p>

            {capacityEntries.length === 0 ? (
                <>
                    <p className="ResultsEmpty">Noch keine Ausbaukennzahlen verfügbar.</p>
                    <span>{calculationResult.results.columns.length} Ergebnisgrößen verfügbar</span>
                </>
            ) : (
                <div style={{display: 'grid', gridTemplateColumns: '1.3fr 0.7fr', gap: '1rem', alignItems: 'start'}}>
                    <div>
                        <h3>Ausgebaute Kapazität je Anlage</h3>
                        <ReactECharts option={chartOption} style={{height: '340px', width: '100%'}} notMerge />
                    </div>

                    <div>
                        <h3>Kapazitätstabelle</h3>
                        <div style={{overflowX: 'auto'}}>
                            <table style={{width: '100%', borderCollapse: 'collapse'}}>
                                <thead>
                                    <tr>
                                        <th style={{textAlign: 'left', padding: '0.5rem 0.75rem', borderBottom: '1px solid #d9e2df'}}>Anlage</th>
                                        <th style={{textAlign: 'right', padding: '0.5rem 0.75rem', borderBottom: '1px solid #d9e2df'}}>Kapazität</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {capacityEntries.map(entry => (
                                        <tr key={entry.label}>
                                            <td style={{padding: '0.5rem 0.75rem', borderBottom: '1px solid #edf1ef'}}>{entry.label}</td>
                                            <td style={{padding: '0.5rem 0.75rem', borderBottom: '1px solid #edf1ef', textAlign: 'right'}}>
                                                {entry.value.toLocaleString(undefined, {maximumFractionDigits: 2})} {entry.unit}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

export default Ausbauplanung;
