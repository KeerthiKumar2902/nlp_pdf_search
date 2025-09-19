// src/pages/HomePage.jsx (Final Version)
import { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

function HomePage() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [statusMessage, setStatusMessage] = useState('Select a PDF file to begin.');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file && file.type === "application/pdf") {
      setSelectedFile(file);
      setStatusMessage(`File selected: ${file.name}`);
    } else {
      setSelectedFile(null);
      setStatusMessage('Please select a valid PDF file.');
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setStatusMessage('No file selected to upload.');
      return;
    }

    setIsLoading(true);
    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      // Step 1: Upload the file
      setStatusMessage('Step 1/2: Uploading file...');
      const uploadResponse = await axios.post('http://localhost:8000/upload/', formData);
      const filename = uploadResponse.data.filename;

      // Step 2: Process the file
      setStatusMessage('Step 2/2: Processing document... (This may take a moment)');
      await axios.post(`http://localhost:8000/process/${filename}`);

      // Step 3: Success and navigate
      setStatusMessage('Processing complete! Redirecting...');

      setTimeout(() => {
        navigate(`/document/${filename}`);
      }, 1500); // Wait 1.5s to let user read the message

    } catch (error) {
      console.error('Error during file processing:', error);
      setStatusMessage('An error occurred. Please try again.');
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full max-w-2xl">
      <div className="bg-slate-800/80 backdrop-blur-sm shadow-2xl rounded-2xl p-8 space-y-6">
        <h2 className="text-center text-3xl font-extrabold text-white">
          Upload Your Document
        </h2>
        <p className="text-center text-slate-400">
          Upload a PDF to start asking questions.
        </p>

        <div className="space-y-4">
          <input
            type="file"
            accept=".pdf"
            onChange={handleFileChange}
            className="block w-full text-sm text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-cyan-50 file:text-cyan-700 hover:file:bg-cyan-100"
          />

          <button
            onClick={handleUpload}
            disabled={isLoading || !selectedFile}
            className="w-full bg-cyan-600 hover:bg-cyan-700 disabled:bg-slate-500 disabled:cursor-not-allowed text-white font-bold py-3 px-4 rounded-lg transition duration-300"
          >
            {isLoading ? 'Processing...' : 'Upload & Process'}
          </button>
        </div>

        <div className="text-center text-slate-300 pt-4">
          <p>{statusMessage}</p>
        </div>
      </div>
    </div>
  );
}

export default HomePage;