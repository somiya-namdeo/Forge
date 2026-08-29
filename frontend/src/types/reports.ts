export interface ProjectInfo {
  project_name: string;
  domain: string;
  scale: string;
  budget: string;
  deployment_target: string;
  optimization_priority: string;
}

export interface ArchitectureRationale {
  category: string;
  recommended: string;
  reason: string;
}

export interface ArchitectureDetails {
  components: Record<string, string>;
  decision_signals: Record<string, string>;
  rationale: ArchitectureRationale[];
}

export interface ArchitectureReport {
  id: string;
  title: string;
  generated_at: string;
  project_profile: ProjectInfo;
  architecture: ArchitectureDetails;
}
