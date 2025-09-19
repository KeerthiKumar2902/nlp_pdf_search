// src/components/AnalysisModal.jsx (Final Version)
import { useState, useEffect } from 'react';
import axios from 'axios';

// A helper for styling NER tags
const NER_COLORS = {
    PERSON: 'bg-blue-500/30 text-blue-300 border border-blue-500',
    ORG: 'bg-green-500/30 text-green-300 border border-green-500',
    GPE: 'bg-red-500/30 text-red-300 border border-red-500',
    DATE: 'bg-yellow-500/30 text-yellow-300 border border-yellow-500',
    MONEY: 'bg-emerald-500/30 text-emerald-300 border border-emerald-500',
    DEFAULT: 'bg-gray-500/30 text-gray-300 border border-gray-500',
};

function AnalysisModal({ isOpen, onClose, textToAnalyze }) {
    const [analysis, setAnalysis] = useState(null);
    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
        // This effect runs whenever the modal is opened with new text
        if (isOpen && textToAnalyze) {
            const performAnalysis = async () => {
                setIsLoading(true);
                setAnalysis(null); // Clear previous results
                try {
                    const response = await axios.post('http://localhost:8000/analyze/', {
                        text: textToAnalyze,
                        tasks: ["ner", "keywords", "summary"]
                    });
                    setAnalysis(response.data);
                } catch (error) {
                    console.error("Analysis failed:", error);
                    // You could add an error state here to show in the UI
                } finally {
                    setIsLoading(false);
                }
            };
            performAnalysis();
        }
    }, [isOpen, textToAnalyze]); // Dependency array: re-run if these change

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
            <div className="absolute inset-0" onClick={onClose}></div>
            <div className="relative bg-slate-800 rounded-2xl shadow-xl w-full max-w-3xl max-h-[90vh] flex flex-col">
                <div className="flex justify-between items-center p-4 border-b border-slate-700">
                    <h3 className="text-xl font-bold text-cyan-400">Detailed Analysis</h3>
                    <button onClick={onClose} className="text-slate-400 hover:text-white text-2xl">&times;</button>
                </div>

                <div className="p-6 overflow-y-auto">
                    <h4 className="font-bold text-lg mb-2 text-white">Original Text</h4>
                    <p className="bg-slate-900 p-3 rounded-lg text-slate-300 mb-6 text-sm">{textToAnalyze}</p>

                    {isLoading && <p className="text-center text-cyan-400">Analyzing...</p>}

                    {analysis && (
                        <div className="space-y-6">
                            <div>
                                <h4 className="font-bold text-lg mb-2 text-white">Named Entities (NER)</h4>
                                <div className="flex flex-wrap gap-2">
                                    {analysis.ner.length > 0 ? analysis.ner.map((ent, i) => (
                                        <span key={i} className={`px-2 py-1 text-xs rounded-md ${NER_COLORS[ent.label] || NER_COLORS.DEFAULT}`}>
                                            {ent.text} <span className="font-semibold">{ent.label}</span>
                                        </span>
                                    )) : <p className="text-slate-400 text-sm">No entities found.</p>}
                                </div>
                            </div>
                            <div>
                                <h4 className="font-bold text-lg mb-2 text-white">Keywords</h4>
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <h5 className="text-sm font-semibold text-slate-300 mb-1">Contextual (TextRank)</h5>
                                        <ul className="list-disc list-inside text-slate-400 text-sm">
                                            {analysis.keywords.textrank.map((kw, i) => <li key={i}>{kw.text}</li>)}
                                        </ul>
                                    </div>
                                    <div>
                                        <h5 className="text-sm font-semibold text-slate-300 mb-1">Statistical (TF-IDF)</h5>
                                         <ul className="list-disc list-inside text-slate-400 text-sm">
                                            {analysis.keywords.tfidf.map((kw, i) => <li key={i}>{kw.text}</li>)}
                                        </ul>
                                    </div>
                                </div>
                            </div>
                            <div>
                                <h4 className="font-bold text-lg mb-2 text-white">Summary</h4>
                                <div>
                                    <h5 className="text-sm font-semibold text-slate-300 mb-1">Extractive</h5>
                                    <p className="bg-slate-700 p-3 rounded-lg text-slate-300 text-sm">{analysis.summary.extractive}</p>
                                </div>
                                <div className="mt-4">
                                    <h5 className="text-sm font-semibold text-slate-300 mb-1">Abstractive</h5>
                                    <p className="bg-slate-700 p-3 rounded-lg text-slate-300 text-sm">{analysis.summary.abstractive}</p>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

export default AnalysisModal;