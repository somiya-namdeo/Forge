import React, { useState, Component, ErrorInfo, ReactNode } from 'react';
import { AnimatePresence } from 'framer-motion';
import { MainLayout } from './layouts/MainLayout';
import { NavPage } from './components/navigation';
import {
  Home,
  NewArchitecture,
  DecisionEngine,
  Evaluation,
  Benchmark,
  Comparison,
  KnowledgeBase,
  Reports
} from './pages';
import { GeneratedArchitecture } from './types';
import { ErrorState } from './components/common';

// Simple Error Boundary to ensure enterprise UI resilience
class ErrorBoundary extends Component<{ children: ReactNode }, { hasError: boolean; errorMsg: string }> {
  constructor(props: { children: ReactNode }) {
    super(props);
    this.state = { hasError: false, errorMsg: '' };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, errorMsg: error.message };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('[Forge UI Error Boundary caught an error]:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '4rem', display: 'flex', justifyContent: 'center' }}>
          <ErrorState
            title="UI Renderer Anomaly"
            message={`A fatal display exception occurred: ${this.state.errorMsg}`}
            onRetry={() => window.location.reload()}
          />
        </div>
      );
    }
    return this.props.children;
  }
}

export function App() {
  const [activePage, setActivePage] = useState<NavPage>('home');
  const [selectedArchitecture, setSelectedArchitecture] = useState<GeneratedArchitecture | null>(null);

  const handleNavigate = (page: NavPage, arch?: GeneratedArchitecture) => {
    if (arch !== undefined) {
      setSelectedArchitecture(arch);
    }
    setActivePage(page);
    // Smooth scroll to top when changing views
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const renderActivePage = () => {
    switch (activePage) {
      case 'home':
        return <Home onNavigate={handleNavigate} />;
      case 'new-architecture':
        return (
          <NewArchitecture
            initialArchitecture={selectedArchitecture}
            onNavigateToReports={(arch) => handleNavigate('reports', arch)}
          />
        );
      case 'decision-engine':
        return <DecisionEngine />;
      case 'evaluation':
        return <Evaluation />;
      case 'benchmark':
        return <Benchmark />;
      case 'comparison':
        return <Comparison />;
      case 'knowledge-base':
        return <KnowledgeBase />;
      case 'reports':
        return (
          <Reports
            selectedArch={selectedArchitecture}
            onNavigateToArch={(arch) => handleNavigate('new-architecture', arch)}
          />
        );
      default:
        return <Home onNavigate={handleNavigate} />;
    }
  };

  return (
    <ErrorBoundary>
      <MainLayout activePage={activePage} onSelectPage={(p) => handleNavigate(p)}>
        <AnimatePresence mode="wait">
          <div key={activePage} style={{ width: '100%' }}>
            {renderActivePage()}
          </div>
        </AnimatePresence>
      </MainLayout>
    </ErrorBoundary>
  );
}

export default App;
