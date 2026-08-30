import React, { createContext, useContext, useState, ReactNode } from 'react';
import { DecisionResponse, EvaluationResult } from '../types';

export interface ForgeContextState {
  decisionResult: DecisionResponse | null;
  sessionArchitectures: DecisionResponse[];
  evaluationResult: EvaluationResult | null;
  comparisonSelection: {
    archA: DecisionResponse | null;
    archB: DecisionResponse | null;
  };
}

export interface ForgeContextType extends ForgeContextState {
  setDecisionResult: (result: DecisionResponse | null) => void;
  addSessionArchitecture: (result: DecisionResponse) => void;
  setEvaluationResult: (result: EvaluationResult | null) => void;
  setComparisonSelection: (archA: DecisionResponse | null, archB: DecisionResponse | null) => void;
}

const ForgeContext = createContext<ForgeContextType | undefined>(undefined);

export const ForgeProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [decisionResult, setDecisionResultState] = useState<DecisionResponse | null>(null);
  const [sessionArchitectures, setSessionArchitectures] = useState<DecisionResponse[]>([]);
  const [evaluationResult, setEvaluationResult] = useState<EvaluationResult | null>(null);
  const [comparisonSelection, setComparisonSelectionState] = useState<{ archA: DecisionResponse | null, archB: DecisionResponse | null }>({ archA: null, archB: null });

  const setDecisionResult = (result: DecisionResponse | null) => {
    setDecisionResultState(result);
  };

  const addSessionArchitecture = (result: DecisionResponse) => {
    // Ensure every architecture has a stable, unique ID
    const archWithId = {
      ...result,
      id: result.id || `forge_custom-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    };

    setSessionArchitectures(prev => {
      // Avoid duplicate references
      console.log('[SESSION ARCHITECTURE ADD]', archWithId);
      if (prev.find(r => r === result || r.id === archWithId.id)) {
        console.log('[SESSION ARCHITECTURE DUPLICATE REJECTED]', archWithId);
        return prev;
      }
      const next = [...prev, archWithId];
      console.log('[SESSION ARCHITECTURES]', next);
      return next;
      return [...prev, archWithId];
    });
    
    // Also update decisionResult if it's the exact same reference being added
    setDecisionResultState(prev => prev === result ? archWithId : prev);
  };

  const setComparisonSelection = (archA: DecisionResponse | null, archB: DecisionResponse | null) => {
    setComparisonSelectionState({ archA, archB });
  };

  return (
    <ForgeContext.Provider
      value={{
        decisionResult,
        setDecisionResult,
        sessionArchitectures,
        addSessionArchitecture,
        evaluationResult,
        setEvaluationResult,
        comparisonSelection,
        setComparisonSelection,
      }}
    >
      {children}
    </ForgeContext.Provider>
  );
};

export const useForgeContext = (): ForgeContextType => {
  const context = useContext(ForgeContext);
  if (context === undefined) {
    throw new Error('useForgeContext must be used within a ForgeProvider');
  }
  return context;
};
