import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  FileText,
  Download,
  Printer,
  CheckCircle2,
  Square,
  AlertCircle,
  DollarSign,
  Layers,
  ArrowRight,
  ShieldCheck,
  CheckSquare
} from 'lucide-react';
import { Card, Badge, Button, ScoreRing, ProgressBar, EmptyState, Skeleton } from '../components/common';
import { ArchitectureReport, GeneratedArchitecture } from '../types';
import { decisionService, reportsService } from '../services';

interface ReportsProps {
  selectedArch?: GeneratedArchitecture | null;
  onNavigateToArch: (arch: GeneratedArchitecture) => void;
}

export const Reports: React.FC<ReportsProps> = ({ selectedArch, onNavigateToArch }) => {
  const [report, setReport] = useState<ArchitectureReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [exportingJson, setExportingJson] = useState(false);

  useEffect(() => {
    async function loadReport() {
      setLoading(true);
      let target: GeneratedArchitecture | null = selectedArch || null;
      if (!target) {
        const archs = await decisionService.getSessionArchitectures();
        if (archs.length > 0) {
          target = archs[0];
        } else {
          // Generate sample pipeline seamless default
          target = await decisionService.generateFromPrompt(
            'Hybrid RAG architecture for Enterprise Legal compliance',
            'Legal RAG System'
          );
        }
      }
      if (target) {
        const generatedReport = await reportsService.generateReport(target);
        setReport(generatedReport);
      }
      setLoading(false);
    }
    loadReport();
  }, [selectedArch]);

  const toggleChecklist = (taskId: string) => {
    if (!report) return;
    const updated = report.deploymentChecklist.map(item => {
      if (item.id === taskId) return { ...item, completed: !item.completed };
      return item;
    });
    setReport({ ...report, deploymentChecklist: updated });
  };

  const handleExportJson = async () => {
    if (!report) return;
    setExportingJson(true);
    const jsonStr = await reportsService.exportReportAsJson(report);
    const blob = new Blob([jsonStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `forge_report_${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    setExportingJson(false);
  };

  if (loading || !report) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
        <Skeleton variant="title" width={320} />
        <Skeleton variant="card" height={220} />
        <div className="grid-2col">
          <Skeleton variant="card" height={340} />
          <Skeleton variant="card" height={340} />
        </div>
      </div>
    );
  }

  const completedCount = report.deploymentChecklist.filter(c => c.completed).length;

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.35 }}
      style={{ display: 'flex', flexDirection: 'column', gap: '2.5rem' }}
    >
      {/* Header */}
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1.5rem', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '1.5rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
            <Badge variant="gold">● PRODUCTION DEPLOYMENT REPORT</Badge>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Generated {report.generatedAt}</span>
          </div>
          <h1 style={{ fontSize: '2.5rem', fontWeight: 800 }}>
            {report.title}
          </h1>
          <p style={{ fontSize: '1.05rem', color: 'var(--text-secondary)', maxWidth: '750px', marginTop: '0.4rem' }}>
            Comprehensive deployment audit report including infrastructure provisioning steps, token economics breakdown, and verifiable evaluation readiness status.
          </p>
        </div>

        {/* Action Controls */}
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <Button variant="secondary" icon={Download} onClick={handleExportJson} disabled={exportingJson}>
            Export JSON Report
          </Button>
          <Button variant="primary" icon={Printer} onClick={() => reportsService.triggerPrintablePdf(report.title)}>
            Print / Export PDF
          </Button>
        </div>
      </header>

      {/* Production Readiness Audit Banner */}
      <section>
        <Card style={{ padding: '2rem', backgroundColor: 'rgba(16, 185, 129, 0.05)', border: '1px solid rgba(16, 185, 129, 0.3)', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
            <ScoreRing score={report.architecture.summary.overallScore} size={68} strokeWidth={6} />
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <Badge variant="green" style={{ fontSize: '0.8rem' }}>✔ DEPLOYMENT READY</Badge>
                <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{report.productionReadinessSummary.passCount} automated checks passed</span>
              </div>
              <h3 style={{ fontSize: '1.4rem', fontWeight: 800, color: '#FFFFFF', marginTop: '0.35rem' }}>
                {report.productionReadinessSummary.riskSummary}
              </h3>
            </div>
          </div>

          <Button variant="secondary" onClick={() => onNavigateToArch(report.architecture)}>
            View Diagram & Components →
          </Button>
        </Card>
      </section>

      {/* 2-Column Section: Interactive Deployment Checklist | Cost Breakdown */}
      <section className="grid-2col" style={{ gap: '2rem', alignItems: 'stretch' }}>
        
        {/* Left: Interactive Deployment Checklist */}
        <Card style={{ padding: '2rem', display: 'flex', flexDirection: 'column', gap: '1.4rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '1rem' }}>
            <div>
              <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#FFFFFF', display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                <CheckSquare style={{ color: 'var(--accent-gold)' }} size={22} /> Pre-Deployment Checklist
              </h3>
              <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>Click checkbox to update verification state</span>
            </div>
            <Badge variant="neutral">{completedCount} / {report.deploymentChecklist.length} Completed</Badge>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem', flex: 1 }}>
            {report.deploymentChecklist.map((chk) => (
              <div
                key={chk.id}
                onClick={() => toggleChecklist(chk.id)}
                style={{
                  padding: '1.1rem',
                  backgroundColor: chk.completed ? 'rgba(16, 185, 129, 0.08)' : 'var(--bg-secondary)',
                  border: chk.completed ? '1px solid rgba(16, 185, 129, 0.3)' : '1px solid var(--border-subtle)',
                  borderRadius: '12px',
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '1rem',
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                }}
              >
                <div style={{ marginTop: '0.15rem', color: chk.completed ? 'var(--status-green)' : 'var(--text-muted)' }}>
                  {chk.completed ? <CheckCircle2 size={20} /> : <Square size={20} />}
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.25rem' }}>
                    <span style={{ fontSize: '0.78rem', color: 'var(--accent-gold)', fontWeight: 700, textTransform: 'uppercase' }}>
                      {chk.category}
                    </span>
                    <Badge variant={chk.criticality === 'Required' ? 'orange' : 'neutral'} style={{ fontSize: '0.68rem' }}>
                      {chk.criticality}
                    </Badge>
                  </div>
                  <div style={{ fontSize: '0.98rem', fontWeight: chk.completed ? 700 : 600, color: chk.completed ? 'var(--status-green)' : '#FFFFFF', textDecoration: chk.completed ? 'line-through' : 'none' }}>
                    {chk.task}
                  </div>
                  <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
                    {chk.description}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </Card>

        {/* Right: Estimated Monthly Cost Breakdown */}
        <Card style={{ padding: '2rem', display: 'flex', flexDirection: 'column', gap: '1.4rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '1rem' }}>
            <div>
              <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#FFFFFF', display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                <DollarSign style={{ color: 'var(--status-blue)' }} size={22} /> Token & Infrastructure Cost Profile
              </h3>
              <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>Estimated operational expenditure</span>
            </div>
            <div style={{ textAlign: 'right' }}>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>Total Monthly Cap</span>
              <div style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--status-blue)' }}>{report.architecture.summary.estimatedMonthlyCost}</div>
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', flex: 1 }}>
            {report.costBreakdown.map((item, idx) => (
              <div key={idx} style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.92rem', fontWeight: 600 }}>
                  <span style={{ color: '#FFFFFF' }}>{item.item}</span>
                  <span style={{ color: 'var(--text-primary)' }}>${item.monthlyCostUsd} / mo ({item.share}%)</span>
                </div>
                <div style={{ width: '100%', height: '8px', backgroundColor: 'rgba(255,255,255,0.06)', borderRadius: '99px', overflow: 'hidden' }}>
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${item.share}%` }}
                    transition={{ duration: 0.8, ease: 'easeOut', delay: idx * 0.1 }}
                    style={{
                      height: '100%',
                      backgroundColor: idx === 0 ? 'var(--status-blue)' : idx === 1 ? 'var(--accent-gold)' : idx === 2 ? 'var(--status-green)' : 'var(--status-purple)',
                      borderRadius: '99px',
                    }}
                  />
                </div>
              </div>
            ))}

            <div style={{ marginTop: 'auto', padding: '1.25rem', backgroundColor: 'var(--bg-primary)', borderRadius: '14px', border: '1px solid var(--border-subtle)', fontSize: '0.88rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
              <strong style={{ color: 'var(--accent-gold)' }}>Cost Efficiency Recommendation:</strong> Deploying open weights on local tensors or reserved endpoints reduces variable inference overhead by up to 65% under persistent loads.
            </div>
          </div>
        </Card>

      </section>
    </motion.div>
  );
};
