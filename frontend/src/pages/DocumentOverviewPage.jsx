// src/pages/DocumentOverviewPage.jsx (Updated)
import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import NERDisplay from '../components/analysis_displays/NERDisplay';
import KeywordsDisplay from '../components/analysis_displays/KeywordsDisplay';
import SummaryDisplay from '../components/analysis_displays/SummaryDisplay';

function DocumentOverviewPage() {
  const { filename } = useParams();
  const [status, setStatus] = useState('loading');
  const [analysis, setAnalysis] = useState(null);

  // ... (useEffect hook for polling remains unchanged) ...
  useEffect(() => {
    const pollStatus = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/document/${filename}/status`);
        const { status: newStatus, analysis_results } = response.data;
        if (newStatus === 'complete' || newStatus === 'failed') {
          setStatus(newStatus);
          if (analysis_results) setAnalysis(analysis_results);
          return true; // Stop polling
        } else {
          setStatus('processing');
          return false; // Continue polling
        }
      } catch (err) {
        console.error("Polling failed:", err);
        setStatus('failed');
        return true; // Stop polling
      }
    };

    pollStatus().then(done => {
      if (!done) {
        const intervalId = setInterval(async () => {
          if (await pollStatus()) {
            clearInterval(intervalId);
          }
        }, 7000);
        return () => clearInterval(intervalId);
      }
    });
  }, [filename]);


  return (
    <div className="w-full">
      {/* ... (Loading and Failed status JSX remains unchanged) ... */}
      {(status === 'loading' || status === 'processing') && (
        <div className="flex flex-col items-center justify-center text-center p-8 bg-slate-700/50 rounded-lg">
          <svg className="animate-spin h-10 w-10 text-cyan-400 mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <h2 className="text-2xl font-bold text-white">Analysis in Progress</h2>
          <p className="text-slate-400 mt-2">Your document is being analyzed by our Search Engine. This may take a few minutes for large files. Please wait...</p>
        </div>
      )}

      {status === 'failed' && (
        <div className="text-center p-8 bg-red-500/20 rounded-lg">
          <h2 className="text-2xl font-bold text-red-400">Analysis Failed</h2>
          <p className="text-slate-400 mt-2">There was an error during the full-document analysis. Please try uploading and processing the document again.</p>
        </div>
      )}


      {status === 'complete' && analysis && (
        <div className="space-y-8">
          <div className="p-6 bg-slate-900/50 rounded-lg">
            <h3 className="text-xl font-bold text-cyan-400 mb-4">Summaries</h3>
            <SummaryDisplay summary={analysis.summary} />
          </div>
          <div className="p-6 bg-slate-900/50 rounded-lg">
            <h3 className="text-xl font-bold text-cyan-400 mb-4">Keywords & Keyphrases</h3>
            
            {/* THIS IS THE ONLY LINE THAT CHANGES */}
            <KeywordsDisplay keywords={analysis.keywords} keybertKeywords={analysis.keybert_keywords} />

          </div>
          <div className="p-6 bg-slate-900/50 rounded-lg">
            <h3 className="text-xl font-bold text-cyan-400 mb-4">Named Entities</h3>
            <NERDisplay entities={analysis.ner} />
          </div>
        </div>
      )}
    </div>
  );
}

export default DocumentOverviewPage;