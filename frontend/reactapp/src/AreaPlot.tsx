
import ReactECharts from 'echarts-for-react';
import type { EChartsOption } from 'echarts';
import type { ComponentType } from 'react';

type EChartsComponentProps = {
    option: EChartsOption;
    style: {height: string; width: string};
    notMerge?: boolean;
};

const EChartsComponent = ReactECharts as unknown as ComponentType<EChartsComponentProps>;

type AreaPlotProps = {
    CalculationResults: {
        objective_value: number | null;
        results: {
            columns: string[];
            index: string[];
            data: (number | string | null)[][];
        };
    } | null;
    ColumnFilter: RegExp;
    Unit: string;
};

const negativeSeriesPattern = /_load|_charge|_export/i;

function AreaPlot({CalculationResults, ColumnFilter, Unit}: AreaPlotProps) {
    if (!CalculationResults?.results) {
        return null;
    }

    const {columns, index, data} = CalculationResults.results;
    const maxVisiblePoints = 2000;
    const lastVisibleIndex = Math.min(data.length - 1, maxVisiblePoints - 1);
    const filtered_columns = columns.filter(column => ColumnFilter.test(column));
    const series = filtered_columns.map(column => {
        const columnIndex = columns.indexOf(column);
        const isNegative = negativeSeriesPattern.test(column);
        
        return {
            name: column,
            type: 'line' as const,
            stack: isNegative ? 'negative' : 'positive',
            smooth: false,
            symbol: 'none',
            sampling: 'lttb' as const,
            progressive: 500,
            progressiveThreshold: 2000,
            areaStyle: {opacity: 0.72},
            emphasis: {focus: 'series' as const},
            data: data.map(row => {
                const value = row[columnIndex];
                if (typeof value !== 'number') {
                    return 0;
                }
                return isNegative ? -Math.abs(value) : Math.max(value, 0);
            }),
        };
    });

    const option: EChartsOption = {
        animation: false,
        color: ['#087f78', '#e8874d', '#4f78a8', '#d25c72', '#8b6faf', '#c4a24c', '#4d9b68'],
        grid: {top: 58, right: 24, bottom: 72, left: 64},
        dataZoom: [
            {
                type: 'inside',
                xAxisIndex: 0,
                zoomOnMouseWheel: true,
                moveOnMouseMove: true,
                moveOnMouseWheel: true,
                throttle: 50,
                maxValueSpan: maxVisiblePoints - 1,
                startValue: 0,
                endValue: lastVisibleIndex,
            },
            {
                type: 'slider',
                xAxisIndex: 0,
                maxValueSpan: maxVisiblePoints - 1,
                startValue: 0,
                endValue: lastVisibleIndex,
                bottom: 42,
                height: 18,
                borderColor: '#d9e2df',
                fillerColor: 'rgba(8, 127, 120, 0.18)',
                handleStyle: {color: '#087f78'},
                textStyle: {color: '#64747a'},
                throttle: 50,
            },
        ],
        legend: {
            selectedMode: 'multiple',
            top: 8,
            left: 12,
            type: 'scroll',
            textStyle: {color: '#64747a'},
        },
        tooltip: {
            trigger: 'axis',
            axisPointer: {type: 'line'},
            valueFormatter: value => `${Number(value).toFixed(0)} ${Unit}`,
        },
        xAxis: {
            type: 'category',
            boundaryGap: false,
            data: index,
            axisLabel: {
                color: '#64747a',
                formatter: value => value.replace('T', ' ').slice(0, 16),
            },
            axisLine: {lineStyle: {color: '#d9e2df'}},
        },
        yAxis: {
            type: 'value',
            name: Unit === 'W' ? 'Leistung (W)' : Unit === 'Wh' ? 'Energie (Wh)' : undefined,
            nameTextStyle: {color: '#64747a'},
            axisLabel: {color: '#64747a'},
            splitLine: {lineStyle: {color: '#e8efec'}},
        },
        series,
    };

    return (
        <div className="AreaPlot" aria-label="Leistungsverlauf nach Technologie">
            <EChartsComponent option={option} style={{height: '390px', width: '100%'}} notMerge />
        </div>
    );
}

export default AreaPlot;