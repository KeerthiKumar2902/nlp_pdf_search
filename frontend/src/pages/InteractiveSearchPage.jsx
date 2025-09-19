// src/pages/InteractiveSearchPage.jsx (Final Version)
import { useState } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import AnalysisModal from '../components/AnalysisModal';


function InteractiveSearchPage() {
  const { filename } = useParams();
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false); // --- NEW STATE ---
  const [selectedText, setSelectedText] = useState('');   // --- NEW STATE ---

  const handleAnalyzeClick = (chunkText) => {
    setSelectedText(chunkText);
    setIsModalOpen(true);
  };

  const handleSearch = async (event) => {
    event.preventDefault(); // Prevent form from refreshing the page
    if (!query.trim()) {
      setError('Please enter a query.');
      return;
    }

    setIsLoading(true);
    setError('');
    setResults([]);

    try {
      const response = await axios.get(`http://localhost:8000/search/${filename}`, {
        params: { query: query }
      });
      setResults(response.data.results);
    } catch (err) {
      console.error("Search failed:", err);
      setError(err.response?.data?.detail || 'An error occurred during search.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full p-8 flex flex-col space-y-8">
      {/* Header Section */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-cyan-400">Document Workspace</h1>
        <p className="text-slate-400 mt-2">
          Currently querying: <span className="font-mono bg-slate-700 px-2 py-1 rounded">{filename}</span>
        </p>
      </div>

      {/* Search Bar Section */}
      <form onSubmit={handleSearch} className="flex space-x-2">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask a question about your document..."
          className="flex-grow bg-slate-700 text-white placeholder-slate-400 p-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500"
        />
        <button
          type="submit"
          disabled={isLoading}
          className="bg-cyan-600 hover:bg-cyan-700 disabled:bg-slate-500 text-white font-bold py-3 px-4 rounded-lg transition"
        >
          {isLoading ? 'Searching...' : 'Search'}
        </button>
      </form>

      {/* Results Section */}
      <div className="bg-slate-800/80 backdrop-blur-sm shadow-lg rounded-lg p-6 min-h-[400px]">
        {/* ... (error, initial message, and loading message logic remains the same) ... */}

        <div className="space-y-4">
          {results.map((result, index) => (
            <div key={index} className="bg-slate-700 p-4 rounded-lg shadow">
              <p className="text-slate-300">{result.chunk}</p>
              <div className="flex justify-between items-center mt-3">
                <p className="text-xs text-cyan-400 font-mono">
                  Relevance: {result.score.toFixed(4)}
                </p>
                {/* --- NEW BUTTON --- */}
                <button 
                  onClick={() => handleAnalyzeClick(result.chunk)}
                  className="bg-cyan-700 hover:bg-cyan-600 text-white text-xs font-bold py-1 px-3 rounded-full transition"
                >
                  Analyze Chunk
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* --- RENDER THE MODAL --- */}
      <AnalysisModal 
        isOpen={isModalOpen} 
        onClose={() => setIsModalOpen(false)} 
        textToAnalyze={selectedText}
      />
    </div>
  );
}

export default InteractiveSearchPage;