// src/App.jsx (Updated with New Nested Routes)
import { Routes, Route } from 'react-router-dom';

// Import Layouts
import Layout from './components/Layout';
import DocumentLayout from './layouts/DocumentLayout';

// Import Pages
import HomePage from './pages/HomePage';
import InteractiveSearchPage from './pages/InteractiveSearchPage'; // Our renamed component
import DocumentOverviewPage from './pages/DocumentOverviewPage';  // Our new placeholder page

function App() {
  return (
    <Routes>
      {/* This is the main layout with the header/footer */}
      <Route path="/" element={<Layout />}>

        {/* The default page is the HomePage */}
        <Route index element={<HomePage />} />

        {/* This is the new parent route for our document workspace */}
        <Route path="document/:filename" element={<DocumentLayout />}>

          {/* This is the default CHILD page, shown at "/document/:filename" */}
          <Route index element={<InteractiveSearchPage />} />

          {/* This is the second CHILD page, shown at "/document/:filename/overview" */}
          <Route path="overview" element={<DocumentOverviewPage />} />
        </Route>

      </Route>
    </Routes>
  );
}

export default App;