// src/pages/HomePage.jsx
import { useState, useEffect } from 'react';
import axios from 'axios';

function HomePage() {
  const [message, setMessage] = useState('Connecting to backend...');

  useEffect(() => {
    // This effect runs once when the component mounts
    axios.get('http://localhost:8000/')
      .then(response => {
        setMessage(response.data.message);
      })
      .catch(error => {
        console.error("Error connecting to backend:", error);
        setMessage('Could not connect to backend.');
      });
  }, []); // The empty array means this effect runs only once

  return (
    <div className="text-center">
        <h1 className="text-4xl font-bold text-cyan-400 mb-4">NLP PDF Search Engine</h1>
        <p className="text-xl text-slate-300">Backend Status: <span className="font-bold text-green-400">{message}</span></p>
    </div>
  );
}

export default HomePage;