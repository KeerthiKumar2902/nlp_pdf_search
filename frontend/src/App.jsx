// src/App.jsx
import { Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage';

function App() {
  return (
    <div className="bg-slate-900 text-white min-h-screen flex items-center justify-center">
      <Routes>
        <Route path="/" element={<HomePage />} />
        {/* We will add the document page route later */}
        {/* <Route path="/document/:filename" element={<DocumentPage />} /> */}
      </Routes>
    </div>
  );
}

export default App;