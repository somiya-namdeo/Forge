import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Download,
  Printer,
} from 'lucide-react';
import { Card, Badge, Button, Skeleton } from '../components/common';
import { ArchitectureReport } from '../types';
import { useForgeContext } from '../context';
import { reportsService } from '../services/reportsService';

interface ReportsProps {
  onNavigateToArch: (arch: any) => void;
}

export const Reports: React.FC<ReportsProps> = ({ onNavigateToArch }) => {
  const { decisionResult, benchmarkResult, evaluationResult } = useForgeContext();
  const [report,       setReport]       = useState<ArchitectureReport | null>(null);
  const [loading,      setLoading]      = useState(true);
  const [exportingJson, setExportingJson] = useState(false);
  const [exportingPdf,  setExportingPdf]  = useState(false);
  const [backendUnavailable, setBackendUnavailable] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadReport() {
      setLoading(true);
      setBackendUnavailable(false);
      setError(null);
      
      if (!decisionResult) {
        setBackendUnavailable(true);
        setLoading(false);
        return;
      }

      try {
        const payload = {
          decision_result: decisionResult,
          benchmark_result: benchmarkResult,
          evaluation_result: evaluationResult,
        };
        const generatedReport = await reportsService.generateReport(payload);
        setReport(generatedReport);
      } catch (err: any) {
        console.error('Failed to generate report:', err);
        setError(err.message || 'An error occurred while generating the report.');
        setBackendUnavailable(true);
      } finally {
        setLoading(false);
      }
    }
    loadReport();
  }, [decisionResult, benchmarkResult, evaluationResult]);

  const handleExportJson = async () => {
    if (!report) return;
    setExportingJson(true);
    const jsonStr = JSON.stringify(report, null, 2);
    const blob    = new Blob([jsonStr], { type: 'application/json' });
    const url     = URL.createObjectURL(blob);
    const a       = document.createElement('a');
    a.href = url; a.download = `forge_report_${Date.now()}.json`;
    document.body.appendChild(a); a.click(); document.body.removeChild(a);
    URL.revokeObjectURL(url);
    setExportingJson(false);
  };

  const handleExportPdf = async () => {
    if (!report) return;
    setExportingPdf(true);
    try {
      const payload = {
        decision_result: decisionResult,
        benchmark_result: benchmarkResult,
        evaluation_result: evaluationResult,
      };
      await reportsService.triggerPrintablePdf(payload, `forge_report_${Date.now()}.pdf`);
    } catch (err) {
      console.error(err);
      alert('Failed to generate PDF');
    } finally {
      setExportingPdf(false);
    }
  };

  if (backendUnavailable || error) {
    return (
      <div style={{ padding: '4rem 2rem', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem', textAlign: 'center' }}>
        <div style={{ width: '48px', height: '48px', borderRadius: '12px', backgroundColor: 'var(--accent-gold-dim)', color: 'var(--accent-gold)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.5rem' }}>📄</div>
        <div style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-primary)' }}>
          {error ? 'Report Generation Failed' : 'No Data Available'}
        </div>
        <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', maxWidth: '460px' }}>
          {error ? error : 'Generate an architecture from the Decision Engine first, then navigate here to view the full decision report.'}
        </div>
      </div>
    );
  }

  if (loading || !report) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
        <Skeleton variant="title" width={320} />
        <Skeleton variant="card"  height={120} />
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '24px' }}>
          <Skeleton variant="card" height={600} />
          <Skeleton variant="card" height={600} />
        </div>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.3 }}
      style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}
    >
      {/* ── Header ────────────────────────────────────────── */}
      <div style={{ display: 'flex', flexDirection: 'column' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem' }}>
          <Badge variant="gold" style={{ fontSize: '0.6875rem' }}>● ARCHITECTURE DECISION REPORT</Badge>
          <span style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>Generated {report.generated_at}</span>
        </div>
        <h1 style={{ fontSize: '2.25rem', fontWeight: 800, color: '#FFFFFF', lineHeight: 1.2, marginBottom: '0.5rem' }}>
          Architecture Decision Report
        </h1>
        <p style={{ fontSize: '1rem', color: 'var(--text-secondary)', lineHeight: 1.6, maxWidth: '700px' }}>
          Comprehensive architecture recommendation, decision signals, and technical rationale.
        </p>
        
        <div style={{ display: 'flex', gap: '16px', alignItems: 'center', marginTop: '24px' }}>
          <Button variant="secondary" icon={Download} onClick={handleExportJson} disabled={exportingJson} style={{ height: '42px', fontSize: '0.875rem', padding: '0 1.25rem' }}>
            Export JSON
          </Button>
          <Button variant="secondary" icon={Printer} onClick={handleExportPdf} disabled={exportingPdf} style={{ height: '42px', fontSize: '0.875rem', padding: '0 1.25rem' }}>
            Download PDF
          </Button>
        </div>
      </div>

      {/* ── Architecture Decision ────────────────────────────── */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
        {/* Decision Signals */}
        <div className="forge-card" style={{ padding: '30px', borderRadius: '14px' }}>
          <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#FFFFFF', marginBottom: '16px' }}>Decision Signals</h3>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '12px' }}>
            {Object.entries(report.architecture.decision_signals).map(([k, v]) => (
              <div key={k} style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '8px 16px', backgroundColor: 'var(--bg-secondary)', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700 }}>{k.replace(/_/g, ' ')}:</span>
                <span style={{ fontSize: '0.875rem', color: '#FFFFFF', fontWeight: 600 }}>{String(v)}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Components Grid */}
        <div className="forge-card" style={{ padding: '30px', borderRadius: '14px' }}>
          <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#FFFFFF', marginBottom: '20px' }}>Architecture Components</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
            {Object.entries(report.architecture.components).map(([key, value]) => (
              <div key={key} style={{ padding: '16px', backgroundColor: 'var(--bg-secondary)', borderRadius: '10px', border: '1px solid var(--border-subtle)' }}>
                <div style={{ fontSize: '0.75rem', color: 'var(--accent-gold)', fontWeight: 700, textTransform: 'uppercase', marginBottom: '8px' }}>
                  {key.replace(/_/g, ' ')}
                </div>
                <div style={{ fontSize: '0.9375rem', color: '#FFFFFF', fontWeight: 600 }}>{String(value)}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Why This Architecture */}
        <div className="forge-card" style={{ padding: '30px', borderRadius: '14px' }}>
          <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#FFFFFF', marginBottom: '20px' }}>Why This Architecture</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {report.architecture.rationale.map((r, i) => (
              <div key={i} style={{ padding: '16px', backgroundColor: 'var(--bg-secondary)', borderRadius: '10px', border: '1px solid var(--border-subtle)' }}>
                <div style={{ fontSize: '0.9rem', color: '#FFFFFF', fontWeight: 700, marginBottom: '6px' }}>
                  {r.category.replace(/_/g, ' ').toUpperCase()}: <span style={{ color: 'var(--accent-gold)' }}>{r.recommended}</span>
                </div>
                <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                  {r.reason}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </motion.div>
  );
};
