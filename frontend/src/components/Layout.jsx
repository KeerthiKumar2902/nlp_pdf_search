// src/components/Layout.jsx
import { Outlet } from 'react-router-dom';

function Layout() {
  return (
    <div className="bg-slate-900 text-white min-h-screen flex flex-col">
      {/* Header */}
      <header className="bg-slate-800 shadow-md">
        <nav className="container mx-auto px-6 py-4">
          <h1 className="text-2xl font-bold text-cyan-400">NLP Document Query Engine</h1>
        </nav>
      </header>

      {/* Main Content Area */}
      <main className="flex-grow container mx-auto px-6 py-8 flex items-center justify-center">
        {/* The Outlet will render the specific page component (e.g., HomePage) */}
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="bg-slate-800 text-center py-4 text-sm text-slate-400">
        <p>&copy; 2025 NLP Search Engine. All Rights Reserved.</p>
      </footer>
    </div>
  );
}

export default Layout;