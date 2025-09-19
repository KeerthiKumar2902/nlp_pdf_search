// src/components/analysis_displays/SummaryDisplay.jsx
function SummaryDisplay({ summary }) {
  return (
    <div className="space-y-4">
      <div>
        <h5 className="text-md font-semibold text-slate-300 mb-1">Extractive Summary</h5>
        <p className="bg-slate-700 p-3 rounded-lg text-slate-300 text-sm">{summary.extractive}</p>
      </div>
      <div>
        <h5 className="text-md font-semibold text-slate-300 mb-1">Abstractive Summary</h5>
        <p className="bg-slate-700 p-3 rounded-lg text-slate-300 text-sm">{summary.abstractive}</p>
      </div>
    </div>
  );
}
export default SummaryDisplay;