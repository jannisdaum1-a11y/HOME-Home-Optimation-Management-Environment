import ReactECharts from 'echarts-for-react';
import type {EChartsOption} from 'echarts';
import type {CalculationResult} from './ResultTypes';

type WirtschaftlichkeitProps = {
    calculationResult: CalculationResult;
};

function Wirtschaftlichkeit({calculationResult}: WirtschaftlichkeitProps) {
    const {results, initial_capex} = calculationResult;

    const costSeries = results.columns
        .filter(column => column === 'system_costs' || column === 'system_costs_aggregated')
        .map(column => {
            const columnIndex = results.columns.indexOf(column);
            return {
                name: column === 'system_costs_aggregated' ? 'aggregierte Kosten' : 'system_costs',
                data: results.data.map(row => {
                    const value = row[columnIndex];
                    return typeof value === 'number' ? value : 0;
                }),
            };
        });

    const capexEntries = Object.entries(initial_capex ?? {}).filter(
        ([key, value]) => key !== 'total_capex' && typeof value === 'number'
    );

    const lineOption: EChartsOption = {
        animation: false,
        tooltip: {trigger: 'axis'},
        legend: {top: 0},
        grid: {top: 44, right: 24, bottom: 40, left: 64},
        xAxis: {
            type: 'category',
            data: results.index,
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

    const capexOption: EChartsOption = {
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

    return (
        <div className="ResultTabPanel">
            <p className="Eyebrow">Wirtschaftlichkeit</p>
            <p className="ObjectiveValue">
                Zielfunktionswert: <strong>{calculationResult.objective_value ?? 'n/a'}</strong>
            </p>

            <h3>Systemkosten über die Zeit</h3>
            <ReactECharts option={lineOption} style={{height: '320px', width: '100%'}} notMerge />

            <h3>Initiale CAPEX nach Komponente</h3>
            <ReactECharts option={capexOption} style={{height: '320px', width: '100%'}} notMerge />
        </div>
    );
}

export default Wirtschaftlichkeit;
