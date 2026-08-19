export const formatLatency = (val?: number): string => {
  if (val === undefined || val === null) return '-';
  return `${val.toFixed(2)} ms`;
};

export const formatPercentage = (val?: number): string => {
  if (val === undefined || val === null) return '-';
  return `${val.toFixed(1)}%`;
};

export const formatCost = (val?: number): string => {
  if (val === undefined || val === null) return '-';
  if (val === 0) return '$0.00';
  return `$${val.toFixed(4)}`;
};

export const formatThroughput = (latencyMs?: number): string => {
  if (!latencyMs) return '-';
  return (1000 / latencyMs).toFixed(0);
};

export const generateArchitectureName = (arch: any, index: number): string => {
  const projectName = arch.metadata?.project_name;
  if (projectName && projectName !== 'Forge UI Configured Architecture') {
    return projectName;
  }
  
  // Attempt to derive from config (deployment_target and priority)
  // Check typical places the backend might echo the request
  const target = arch.metadata?.deployment_target || arch.deployment_target || arch.metadata?.request?.deployment_target;
  const priority = arch.metadata?.priority || arch.priority || arch.metadata?.request?.priority;
  
  if (target && priority) {
    const targetMap: Record<string, string> = {
      aws: 'AWS', gcp: 'GCP', azure: 'Azure', on_prem: 'On-Prem', local: 'Local'
    };
    const priorityMap: Record<string, string> = {
      cost: 'Cost-Optimized', quality: 'Quality', latency: 'Performance', balanced: 'Balanced'
    };
    const tName = targetMap[target.toLowerCase()] || target;
    const pName = priorityMap[priority.toLowerCase()] || priority;
    return `${tName} ${pName} Stack`;
  }

  return `Forge Custom Arch ${index + 1}`;
};
