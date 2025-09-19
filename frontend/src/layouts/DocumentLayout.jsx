// src/layouts/DocumentLayout.jsx
import { useParams, NavLink, Outlet } from 'react-router-dom';

function DocumentLayout() {
  const { filename } = useParams();

  const activeLinkStyle = {
    borderBottom: '2px solid #22d3ee', // A cyan-400 border
    color: '#22d3ee'
  };

  return (
    <div className="w-full max-w-6xl flex flex-col h-full space-y-4">
      {/* Header for this specific workspace */}
      <div className="text-center p-4 bg-slate-800 rounded-lg">
        <h1 className="text-2xl font-bold text-white">Document Workspace</h1>
        <p className="text-slate-400 mt-1">
          Analyzing: <span className="font-mono bg-slate-700 px-2 py-1 rounded">{filename}</span>
        </p>
      </div>

      {/* Navigation Tabs using NavLink */}
      <nav className="flex space-x-4 border-b border-slate-700 px-4">
        <NavLink 
          to={`/document/${filename}`} 
          end // This 'end' prop is important for the base path to not always be active
          style={({ isActive }) => isActive ? activeLinkStyle : undefined}
          className="py-2 px-3 font-medium text-slate-300 hover:text-cyan-400"
        >
          Interactive Search
        </NavLink>
        <NavLink 
          to={`/document/${filename}/overview`}
          style={({ isActive }) => isActive ? activeLinkStyle : undefined}
          className="py-2 px-3 font-medium text-slate-300 hover:text-cyan-400"
        >
          Full Analysis
        </NavLink>
      </nav>

      {/* The magic happens here: Child pages will be rendered inside this Outlet */}
      <div className="flex-grow p-4 bg-slate-800/50 rounded-lg">
        <Outlet />
      </div>
    </div>
  );
}

export default DocumentLayout;