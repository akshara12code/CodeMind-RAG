import React, { useState } from 'react';
import { Landing } from './pages/Landing';
import { Dashboard } from './pages/Dashboard';
import { EvaluationDashboard } from './pages/EvaluationDashboard';
import { RAGInspector } from './components/RAGInspector';

type Page = 'landing' | 'dashboard' | 'evaluation';

function App() {
  const [currentPage, setCurrentPage] = useState<Page>('landing');
  const [showRAGInspector, setShowRAGInspector] = useState(false);

  return (
    <div className="font-sans">
      {currentPage === 'landing' && (
        <>
          <Landing />
          <div className="fixed bottom-8 right-8 flex gap-4">
            <button
              onClick={() => setCurrentPage('dashboard')}
              className="px-6 py-3 rounded-lg bg-[#00C8FF] text-[#050505] font-bold hover:bg-[#38BDF8] transition shadow-lg"
            >
              Go to Dashboard
            </button>
          </div>
        </>
      )}

      {currentPage === 'dashboard' && (
        <>
          <Dashboard />
          <RAGInspector visible={showRAGInspector} />
          <div className="fixed bottom-8 right-8 flex gap-4">
            <button
              onClick={() => setCurrentPage('evaluation')}
              className="px-6 py-3 rounded-lg bg-[#00AF80] text-white font-bold hover:bg-[#008060] transition shadow-lg"
            >
              Evaluation
            </button>
            <button
              onClick={() => setCurrentPage('landing')}
              className="px-6 py-3 rounded-lg bg-[#8B949E] text-white font-bold hover:bg-[#6B7481] transition shadow-lg"
            >
              Home
            </button>
          </div>
        </>
      )}

      {currentPage === 'evaluation' && (
        <>
          <EvaluationDashboard />
          <div className="fixed bottom-8 right-8 flex gap-4">
            <button
              onClick={() => setCurrentPage('dashboard')}
              className="px-6 py-3 rounded-lg bg-[#00C8FF] text-[#050505] font-bold hover:bg-[#38BDF8] transition shadow-lg"
            >
              Back to Chat
            </button>
          </div>
        </>
      )}
    </div>
  );
}

export default App;
