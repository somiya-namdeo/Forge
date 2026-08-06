import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Download,
  Printer,
  CheckCircle2,
  Square,
  DollarSign,
  CheckSquare,
} from 'lucide-react';
import { Card, Badge, Button, ScoreRing, Skeleton } from '../components/common';
import { ArchitectureReport, GeneratedArchitecture } from '../types';
import { decisionService, reportsService } from '../services';

interface ReportsProps {
  selectedArch?: any | null;
  onNavigateToArch: (arch: any) => void;
}

export const Reports: React.FC<ReportsProps> = ({ selectedArch, onNavigateToArch }) => {
  const [report,       setReport]       = useState<ArchitectureReport | null>(null);
  const [loading,      setLoading]      = useState(true);
  const [exportingJson, setExportingJson] = useState(false);

  const [backendUnavailable, setBackendUnavailable] = useState(false);

  useEffect(() => {
    async function loadReport() {
      setLoading(true);
      setBackendUnavailable(false);
      let target: any | null = selectedArch || null;
      if (!target) {
        // No arch passed — backend session endpoint missing, cannot fabricate
        setBackendUnavailable(true);
        setLoading(false);
        return;
      }
      try {
        setReport(await reportsService.generateReport(target));
      } catch {
        setBackendUnavailable(true);
      }
      setLoading(false);
    }
    loadReport();
  }, [selectedArch]);

  const toggleChecklist = (id: string) => {
    if (!report) return;
    setReport({
      ...report,
      deploymentChecklist: report.deploymentChecklist.map(c => c.id === id ? { ...c, completed: !c.completed } : c),
    });
  };

  const handleExportJson = async () => {
    if (!report) return;
    setExportingJson(true);
    const jsonStr = await reportsService.exportReportAsJson(report);
    const blob    = new Blob([jsonStr], { type: 'application/json' });
    const url     = URL.createObjectURL(blob);
    const a       = document.createElement('a');
    a.href = url; a.download = `forge_report_${Date.now()}.json`;
    document.body.appendChild(a); a.click(); document.body.removeChild(a);
    URL.revokeObjectURL(url);
    setExportingJson(false);
  };

  if (backendUnavailable) {
    return (
      <div style={{ padding: '4rem 2rem', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem', textAlign: 'center' }}>
        <div style={{ width: '48px', height: '48px', borderRadius: '12px', backgroundColor: 'var(--accent-gold-dim)', color: 'var(--accent-gold)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.5rem' }}>📄</div>
        <div style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-primary)' }}>Backend Not Available</div>
        <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', maxWidth: '460px' }}>
          Generate an architecture from the Decision Engine or Home page first, then navigate here to view the full production report.
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

  const completedCount = report.deploymentChecklist.filter(c => c.completed).length;
  const barColors      = ['var(--status-blue)', 'var(--accent-gold)', 'var(--status-green)', 'var(--status-purple)'];

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
          <Badge variant="gold" style={{ fontSize: '0.6875rem' }}>● PRODUCTION REPORT</Badge>
          <span style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>Generated {report.generatedAt}</span>
        </div>
        <h1 style={{ fontSize: '2.25rem', fontWeight: 800, color: '#FFFFFF', lineHeight: 1.2, marginBottom: '0.5rem' }}>
          {report.title}
        </h1>
        <p style={{ fontSize: '1rem', color: 'var(--text-secondary)', lineHeight: 1.6, maxWidth: '700px' }}>
          Deployment audit including infrastructure provisioning, token economics, and evaluation readiness.
        </p>
        
        <div style={{ display: 'flex', gap: '16px', alignItems: 'center', marginTop: '24px' }}>
          <Button variant="secondary" icon={Download} onClick={handleExportJson} disabled={exportingJson} style={{ height: '42px', fontSize: '0.875rem', padding: '0 1.25rem' }}>
            Export JSON
          </Button>
          <Button variant="primary" icon={Printer} onClick={() => reportsService.triggerPrintablePdf(report.title)} style={{ height: '42px', fontSize: '0.875rem', padding: '0 1.25rem' }}>
            Export PDF
          </Button>
        </div>
      </div>

      {/* ── Readiness Banner ──────────────────────────────── */}
      <div
        className="forge-card"
        style={{
          padding: '28px 30px',
          backgroundColor: 'rgba(16,185,129,0.04)',
          border: '1px solid rgba(16,185,129,0.25)',
          borderRadius: '14px',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
          <ScoreRing score={report.architecture.summary.overallScore} size={60} strokeWidth={5} />
          <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.4rem' }}>
              <Badge variant="green" style={{ fontSize: '0.6875rem' }}>✔ DEPLOYMENT READY</Badge>
              <span style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>{report.productionReadinessSummary.passCount} checks passed</span>
            </div>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#FFFFFF', lineHeight: 1.2 }}>
              {report.productionReadinessSummary.riskSummary}
            </h3>
          </div>
        </div>
        <Button variant="secondary" onClick={() => onNavigateToArch(report.architecture)} style={{ height: '42px', fontSize: '0.875rem', padding: '0 1.25rem' }}>
          View Diagram →
        </Button>
      </div>

      {/* ── 2-col body ────────────────────────────────────── */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(480px, 1fr))', gap: '24px', alignItems: 'stretch' }}>

        {/* Deployment Checklist */}
        <div className="forge-card" style={{ padding: '30px', display: 'flex', flexDirection: 'column', gap: '24px', height: '640px', borderRadius: '14px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingBottom: '16px', borderBottom: '1px solid var(--border-subtle)', flexShrink: 0 }}>
            <div>
              <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', fontSize: '1.125rem', fontWeight: 700, color: '#FFFFFF' }}>
                <CheckSquare size={20} style={{ color: 'var(--accent-gold)', flexShrink: 0 }} /> Pre-Deployment Checklist
              </h3>
              <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginTop: '0.4rem' }}>Click checkbox to toggle verification state</p>
            </div>
            <Badge variant="neutral" style={{ fontSize: '0.75rem', flexShrink: 0 }}>{completedCount} / {report.deploymentChecklist.length}</Badge>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', flex: 1, overflowY: 'auto', paddingRight: '16px' }}>
            {report.deploymentChecklist.map(chk => (
              <div
                key={chk.id}
                onClick={() => toggleChecklist(chk.id)}
                style={{
                  padding: '16px 20px',
                  backgroundColor: chk.completed ? 'rgba(16,185,129,0.06)' : 'var(--bg-secondary)',
                  border: `1px solid ${chk.completed ? 'rgba(16,185,129,0.25)' : 'var(--border-subtle)'}`,
                  borderRadius: '10px',
                  display: 'flex', alignItems: 'flex-start', gap: '16px',
                  cursor: 'pointer', transition: 'all 0.15s',
                }}
              >
                <div style={{ marginTop: '0.15rem', color: chk.completed ? 'var(--status-green)' : 'var(--text-muted)', flexShrink: 0 }}>
                  {chk.completed ? <CheckCircle2 size={20} /> : <Square size={20} />}
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem', gap: '0.5rem' }}>
                    <span style={{ fontSize: '0.75rem', color: 'var(--accent-gold)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.04em' }}>{chk.category}</span>
                    <Badge variant={chk.criticality === 'Required' ? 'orange' : 'neutral'} style={{ fontSize: '0.6875rem', flexShrink: 0 }}>{chk.criticality}</Badge>
                  </div>
                  <div style={{ fontSize: '0.9375rem', fontWeight: 600, color: chk.completed ? 'var(--status-green)' : '#FFFFFF', textDecoration: chk.completed ? 'line-through' : 'none', marginBottom: '0.4rem' }}>
                    {chk.task}
                  </div>
                  <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>{chk.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Cost Profile */}
        <div className="forge-card" style={{ padding: '30px', display: 'flex', flexDirection: 'column', gap: '24px', height: '640px', borderRadius: '14px' }}>
          <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', paddingBottom: '16px', borderBottom: '1px solid var(--border-subtle)', flexShrink: 0 }}>
            <div>
              <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', fontSize: '1.125rem', fontWeight: 700, color: '#FFFFFF' }}>
                <DollarSign size={20} style={{ color: 'var(--status-blue)', flexShrink: 0 }} /> Token &amp; Infrastructure Cost
              </h3>
              <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginTop: '0.4rem' }}>Estimated operational expenditure</p>
            </div>
            <div style={{ textAlign: 'right', flexShrink: 0 }}>
              <div style={{ fontSize: '0.6875rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.2rem' }}>Monthly Cap</div>
              <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--status-blue)' }}>{report.architecture.summary.estimatedMonthlyCost}</div>
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', flex: 1, overflowY: 'auto', paddingRight: '12px' }}>
            {report.costBreakdown.map((item, idx) => (
              <div key={idx} style={{ display: 'flex', flexDirection: 'column', gap: '0.625rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.9375rem', fontWeight: 600, color: '#FFFFFF' }}>
                  <span>{item.item}</span>
                  <span style={{ color: 'var(--text-secondary)' }}>${item.monthlyCostUsd}/mo <span style={{ color: 'var(--text-muted)', fontSize: '0.8125rem' }}>({item.share}%)</span></span>
                </div>
                <div style={{ width: '100%', height: '8px', backgroundColor: 'rgba(255,255,255,0.06)', borderRadius: '4px', overflow: 'hidden' }}>
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${item.share}%` }}
                    transition={{ duration: 0.7, ease: 'easeOut', delay: idx * 0.08 }}
                    style={{ height: '100%', backgroundColor: barColors[idx % barColors.length], borderRadius: '4px' }}
                  />
                </div>
              </div>
            ))}
          </div>

          <div style={{ marginTop: 'auto', padding: '20px', backgroundColor: 'var(--bg-primary)', borderRadius: '10px', border: '1px solid var(--border-subtle)', fontSize: '0.875rem', color: 'var(--text-secondary)', lineHeight: 1.6, flexShrink: 0 }}>
            <strong style={{ color: 'var(--accent-gold)' }}>Cost Efficiency:</strong> Deploying open weights on reserved endpoints reduces variable inference overhead by up to 65% under persistent loads.
          </div>
        </div>
      </div>
    </motion.div>
  );
};
