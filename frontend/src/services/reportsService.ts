import { ArchitectureReport } from '../types';
import { request } from './apiClient';

export interface ReportGenerationRequest {
  decision_result?: any;
  evaluation_result?: any;
}

class ReportsService {
  async generateReport(payload: ReportGenerationRequest): Promise<ArchitectureReport> {
    return request<ArchitectureReport>('/reports/generate', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  }

  async exportReportAsJson(payload: ReportGenerationRequest): Promise<string> {
    const report = await this.generateReport(payload);
    return JSON.stringify(report, null, 2);
  }

  async triggerPrintablePdf(payload: ReportGenerationRequest, filename: string = 'forge_report.pdf'): Promise<void> {
    const response = await fetch('http://localhost:8000/api/v1/reports/pdf', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      throw new Error(`Failed to generate PDF: ${response.statusText}`);
    }

    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }
}

export const reportsService = new ReportsService();
