// src/components/analysis_displays/KeywordsDisplay.jsx
function KeywordsDisplay({ keywords }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div>
        <h5 className="text-md font-semibold text-slate-300 mb-2">Contextual Phrases (TextRank)</h5>
        <ul className="list-disc list-inside text-slate-400 text-sm space-y-1">
          {keywords.textrank.map((kw, i) => <li key={i}>{kw.text}</li>)}
        </ul>
      </div>
      <div>
        <h5 className="text-md font-semibold text-slate-300 mb-2">Statistical Terms (TF-IDF)</h5>
          <ul className="list-disc list-inside text-slate-400 text-sm space-y-1">
          {keywords.tfidf.map((kw, i) => <li key={i}>{kw.text}</li>)}
        </ul>
      </div>
    </div>
  );
}
export default KeywordsDisplay;