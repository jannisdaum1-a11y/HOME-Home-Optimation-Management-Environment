import * as XLSX from 'xlsx';
import AreaPlot from './AreaPlot';
import type {CalculationResult} from './ResultTypes';

type ZeitreihenProps = {
    calculationResult: CalculationResult;
};

const previewRowCount = 10;

function downloadResults(results: CalculationResult['results']) {
    const worksheetRows = results.data.map((row, rowIndex) => [
        results.index[rowIndex],
        ...row,
    ]);
    const worksheet = XLSX.utils.aoa_to_sheet([
        ['Zeitpunkt', ...results.columns],
        ...worksheetRows,
    ]);
    const workbook = XLSX.utils.book_new();

    XLSX.utils.book_append_sheet(workbook, worksheet, 'Ergebnisse');
    XLSX.writeFile(workbook, 'optimierungsergebnisse.xlsx');
}

function Zeitreihen({calculationResult}: ZeitreihenProps) {
    return (
        <>
            <h3>Power-Timeseries</h3>
            <AreaPlot CalculationResults={calculationResult} ColumnFilter={/p_|ens|dump/} Unit="W"></AreaPlot>
            <h3>SOC-Timeseries</h3>
            <AreaPlot CalculationResults={calculationResult} ColumnFilter={/soc_/i} Unit="Wh"></AreaPlot>
            <div className="ResultTableHeader">
                <div>
                    <h2>Ergebnisvorschau</h2>
                    <p>{previewRowCount} von {calculationResult.results.data.length} Zeitpunkten angezeigt</p>
                </div>
                <button
                    type="button"
                    className="DownloadButton"
                    onClick={() => downloadResults(calculationResult.results)}
                >
                    <span aria-hidden="true">↓</span>
                    Excel herunterladen
                </button>
            </div>
            <div className="ResultTableWrapper">
                <table className="ResultTable">
                    <thead>
                        <tr>
                            <th>Zeitpunkt</th>
                            {calculationResult.results.columns.map(column => <th key={column}>{column}</th>)}
                        </tr>
                    </thead>
                    <tbody>
                        {calculationResult.results.data.slice(0, previewRowCount).map((row, rowIndex) => (
                            <tr key={calculationResult.results.index[rowIndex]}>
                                <th>{calculationResult.results.index[rowIndex]}</th>
                                {row.map((value, columnIndex) => <td key={`${rowIndex}-${columnIndex}`}>{String(value ?? '-')}</td>)}
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </>
    );
}

export default Zeitreihen;
