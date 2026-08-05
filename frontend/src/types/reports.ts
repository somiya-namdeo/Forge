import { GeneratedArchitecture } from './architecture';

export interface DeploymentChecklistItem {
  id: string;
  category: 'Infrastructure' | 'Security' | 'Vector DB & Search' | 'Monitoring';
  task: string;
  description: string;
  completed: boolean;
  criticality: 'Required' | 'Recommended' | 'Optional';
}

export interface ArchitectureReport {
  id: string;
  title: string;
  generatedAt: string;
  architecture: GeneratedArchitecture;
  deploymentChecklist: DeploymentChecklistItem[];
  costBreakdown: { item: string; monthlyCostUsd: number; share: number }[];
  productionReadinessSummary: {
    ready: boolean;
    passCount: number;
    warnCount: number;
    riskSummary: string;
  };
}
