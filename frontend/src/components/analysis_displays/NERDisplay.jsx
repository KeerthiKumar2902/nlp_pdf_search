// src/components/analysis_displays/NERDisplay.jsx
const NER_COLORS = {
  PERSON: 'bg-blue-500/30 text-blue-300 border border-blue-500',
  ORG: 'bg-green-500/30 text-green-300 border border-green-500',
  GPE: 'bg-red-500/30 text-red-300 border border-red-500',
  DATE: 'bg-yellow-500/30 text-yellow-300 border border-yellow-500',
  MONEY: 'bg-emerald-500/30 text-emerald-300 border border-emerald-500',
  DEFAULT: 'bg-gray-500/30 text-gray-300 border border-gray-500',
};

function NERDisplay({ entities }) {
  if (!entities || entities.length === 0) {
    return <p className="text-slate-400 text-sm">No entities found.</p>;
  }
  return (
    <div className="flex flex-wrap gap-2">
      {entities.map((ent, i) => (
        <span key={i} className={`px-2 py-1 text-xs rounded-md ${NER_COLORS[ent.label] || NER_COLORS.DEFAULT}`}>
          {ent.text} <span className="font-semibold">{ent.label}</span>
        </span>
      ))}
    </div>
  );
}
export default NERDisplay;