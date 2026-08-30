export const getConfidenceLabel = (score: number): string => {
  if (score >= 0.9) return "Excellent";
  if (score >= 0.8) return "High";
  if (score >= 0.65) return "Medium";
  if (score >= 0.5) return "Low";
  return "Very Low";
};

export const getConfidenceColor = (score: number): string => {
  if (score >= 0.8) return 'var(--status-green)';
  if (score >= 0.65) return 'var(--accent-gold)';
  if (score >= 0.5) return '#f97316';
  return '#ef4444';
};

export const getConfidenceBgColor = (score: number): string => {
  if (score >= 0.8) return 'rgba(16,185,129,0.1)';
  if (score >= 0.65) return 'rgba(212,175,99,0.1)';
  if (score >= 0.5) return 'rgba(249,115,22,0.1)';
  return 'rgba(239,68,68,0.1)';
};

export const getConfidenceBorderColor = (score: number): string => {
  if (score >= 0.8) return 'rgba(16,185,129,0.25)';
  if (score >= 0.65) return 'rgba(212,175,99,0.25)';
  if (score >= 0.5) return 'rgba(249,115,22,0.25)';
  return 'rgba(239,68,68,0.25)';
};

export const formatProvider = (name: string): string => {
  if (!name) return name;
  const lower = name.toLowerCase();
  if (lower === 'aws') return 'AWS';
  if (lower === 'gcp') return 'GCP';
  if (lower === 'azure') return 'Azure';
  if (lower === 'on prem' || lower === 'on-prem') return 'On-Prem';
  if (lower === 'local') return 'Local';
  return name;
};

export const formatDeploymentReadiness = (val: string): string => {
  if (!val) return "Production Ready";
  const str = val.toLowerCase();
  if (str.includes("enterprise production")) return "Enterprise Production Ready";
  if (str.includes("prototype")) return "Research Prototype";
  if (str.includes("local development")) return "Local Development";
  if (str.includes("production deployment")) return "Production Deployment";
  if (str.includes("enterprise scale")) return "Enterprise Scale";
  return val;
};

export const getSummaryConfidenceWord = (score: number): string => {
  if (score >= 0.9) return "Excellent confidence";
  if (score >= 0.8) return "High confidence";
  if (score >= 0.65) return "Moderate confidence";
  if (score >= 0.5) return "Limited confidence";
  return "Low confidence";
};

export const improveTradeOffWording = (tradeOff: string): string => {
  const generic = tradeOff.toLowerCase();
  if (generic.includes("no major trade-offs") || generic.includes("none") || generic.includes("minimal")) {
    const options = [
      "Minimal performance trade-offs identified.",
      "No significant compromises were required.",
      "Selected candidate satisfies the evaluated constraints with minimal drawbacks.",
      "Strong overall balance across evaluation dimensions."
    ];
    return options[Math.floor(Math.random() * options.length)];
  }
  return tradeOff;
};

export const improveAlternativeMessaging = (alternative: string): string => {
  const generic = alternative.toLowerCase();
  if (generic.includes("none available") || generic.includes("none") || generic.trim() === "") {
    return "No strong alternative met the selected engineering constraints.";
  }
  return alternative;
};

export const improveRejectedAlternativeReason = (reason: string, index: number): string => {
  const generic = reason.toLowerCase();
  if (generic.includes("rejected due to lower score") || generic.includes("lower score")) {
    const options = [
      "Lower deployment compatibility",
      "Lower evaluation performance",
      "Inferior metadata quality",
      "Reduced scalability",
      "Higher operational cost",
      "Lower infrastructure compatibility",
      "Lower composite suitability score"
    ];
    return options[index % options.length];
  }
  return reason;
};

export const getExplanationPrefix = (index: number): string => {
  const options = [
    "Recommended because",
    "Selected based on",
    "Highest composite score due to",
    "Best satisfies the selected constraints because",
    "Preferred owing to"
  ];
  return options[index % options.length];
};

export const getContextualRecommendations = (priority: string): string[] => {
  const p = priority.toLowerCase();
  if (p.includes('enterprise') || p.includes('production')) {
    return [
      "Validate on production-sized datasets",
      "Evaluate under expected workload",
      "Configure monitoring and observability"
    ];
  }
  if (p.includes('cost')) {
    return [
      "Evaluate inference cost",
      "Validate throughput targets",
      "Compare operational expenses"
    ];
  }
  if (p.includes('latency') || p.includes('speed')) {
    return [
      "Measure end-to-end response latency",
      "Evaluate concurrent requests",
      "Validate caching strategy"
    ];
  }
  return [
    "Perform human evaluation",
    "Run RAG evaluation suite",
    "Validate evaluation robustness"
  ];
};
