import { ArchitectureReport, GeneratedArchitecture } from '../types';

class ReportsService {
  async generateReport(arch: GeneratedArchitecture): Promise<ArchitectureReport> {
    throw new Error('Backend Not Available');
  }

  async exportReportAsJson(report: ArchitectureReport): Promise<string> {
    throw new Error('Backend Not Available');
  }

  async triggerPrintablePdf(reportTitle: string): Promise<void> {
    throw new Error('Backend Not Available');
  }
}

export const reportsService = new ReportsService();
