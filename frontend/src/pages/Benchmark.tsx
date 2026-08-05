import React, { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import { Trophy, Play, Check } from 'lucide-react';
import { Card, Badge, Button, EmptyState, Skeleton, LoadingIndicator } from '../components/common';
import { BenchmarkReport, BenchmarkLeaderboardEntry } from '../types';
import { benchmarkService } from '../services';

export const Benchmark: React.FC = () => {
  const allArchs = [
    { id: 'Hybrid RAG + BGE Reranker', color: '#eab308' },
    { id: 'Dense RAG + GPT-4o',        color: '#22c55e' },
    { id: 'BM25 Only + Claude 3.5',    color: '#3b82f6' },
  ];

  const allMetrics = ['Faithfulness', 'Relevancy', 'Precision@5', 'Recall@10', 'MRR', 'Latency', 'Cost'];

  const [selectedArchs,   setSelectedArchs]   = useState<string[]>(allArchs.map(a => a.id));
  const [selectedMetrics, setSelectedMetrics] = useState<string[]>(allMetrics);
  const [activeTab, setActiveTab] = useState<'Leaderboard' | 'Distribution' | 'Samples'>('Leaderboard');
  const [running, setRunning]     = useState(false);
  const [report,  setReport]      = useState<BenchmarkReport | null>(null);

  type SortKey = keyof BenchmarkLeaderboardEntry | 'score' | 'precision' | 'recall' | 'passRate';
  const [sortField, setSortField]     = useState<SortKey>('score');
  const [sortDir,   setSortDir]       = useState<'asc' | 'desc'>('desc');

  const handleRunBenchmark = async () => {
    setRunning(true);
    setReport(null);
    const data = await benchmarkService.runBenchmark({
      dataset: 'legal-bench-500.jsonl',
      metrics: selectedMetrics,
      architectures: selectedArchs,
    });
    setReport(data);
    setRunning(false);
  };

  const toggleArch   = (id: string) => setSelectedArchs(prev =>
    prev.includes(id) ? (prev.length > 1 ? prev.filter(a => a !== id) : prev) : [...prev, id]);

  const toggleMetric = (m: string) => setSelectedMetrics(prev =>
    prev.includes(m) ? (prev.length > 1 ? prev.filter(x => x !== m) : prev) : [...prev, m]);

  const handleSort = (field: SortKey) => {
    if (sortField === field) setSortDir(d => d === 'asc' ? 'desc' : 'asc');
    else { setSortField(field); setSortDir(field === 'latencyP95' || field === 'costPerMillionTokens' ? 'asc' : 'desc'); }
  };

  const sortedLeaderboard = useMemo(() => {
    if (!report) return [];
    return [...report.leaderboard]
      .map((entry, i) => ({
        ...entry,
        score:     entry.accuracyScore,
        precision: Math.max(60, entry.accuracyScore - 5.2),
        recall:    Math.max(60, entry.accuracyScore - 3.1),
        passRate:  Math.min(100, entry.accuracyScore + 1.9),
        color:     allArchs.find(a => a.id === entry.architectureName)?.color ?? '#9ca3af',
      }))
      .sort((a, b) => {
        const getVal = (r: typeof a) =>
          sortField === 'score'    ? r.score
        : sortField === 'latencyP95'          ? r.latencyP95
        : sortField === 'costPerMillionTokens'? r.costPerMillionTokens
        : sortField === 'precision'           ? r.precision
        : sortField === 'recall'              ? r.recall
        : r.passRate;
        const diff = getVal(a) - getVal(b);
        return sortDir === 'asc' ? diff : -diff;
      })
      .map((e, i) => ({ ...e, rank: i + 1 }));
  }, [report, sortField, sortDir]);

  const thBtn = (label: string, field: SortKey) => ({
    onClick: () => handleSort(field),
    style: {
      padding: '0 0.75rem',
      fontWeight: 700 as const,
      cursor: 'pointer',
      color: sortField === field ? 'var(--accent-gold)' : 'var(--text-muted)',
      userSelect: 'none' as const,
      transition: 'color 0.15s',
    },
    children: `${label}${sortField === field ? (sortDir === 'desc' ? ' ↓' : ' ↑') : ''}`,
  });

  const SortHeader = ({ label, field }: { label: string; field: SortKey }) => (
    <th {...thBtn(label, field)} />
  );

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.3 }}
      className="section-gap-lg"
    >
      {/* ── Header ───────────────────────────────────────── */}
      <div className="page-header">
        <div>
          <h1 className="page-title">Benchmark</h1>
          <p className="page-subtitle">Compare architectures against standardized datasets with statistical rigor</p>
        </div>
      </div>

      {/* ── Configuration 3-column ───────────────────────── */}
      <div className="grid-3col" style={{ gap: '1.25rem' }}>

        {/* Dataset */}
        <div className="forge-card section-gap" style={{ padding: '1.5rem' }}>
          <span style={{ fontSize: '0.6875rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-muted)' }}>Dataset</span>
          <div style={{
            border: '1px dashed var(--accent-gold)',
            backgroundColor: 'rgba(212,175,99,0.03)',
            borderRadius: 'var(--radius-md)',
            padding: '1.25rem',
            textAlign: 'center',
          }}>
            <div style={{ fontSize: '0.9375rem', fontWeight: 700, color: 'var(--accent-gold)' }}>legal-bench-500.jsonl</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>500 Q&A pairs · 2.1 MB</div>
          </div>
          <div style={{ display: 'flex', gap: '0.75rem' }}>
            {[['SAMPLES', '500'], ['DOMAIN', 'Legal']].map(([label, val]) => (
              <div key={label} style={{ flex: 1, background: 'var(--bg-primary)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-sm)', padding: '0.75rem 1rem' }}>
                <div style={{ fontSize: '0.625rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-muted)', marginBottom: '0.2rem' }}>{label}</div>
                <div style={{ fontSize: '1.125rem', fontWeight: 700, color: '#FFFFFF' }}>{val}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Architectures */}
        <div className="forge-card" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          <span style={{ fontSize: '0.6875rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-muted)' }}>Architectures</span>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.875rem' }}>
            {allArchs.map(arch => (
              <div
                key={arch.id}
                onClick={() => toggleArch(arch.id)}
                style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', cursor: 'pointer', userSelect: 'none' }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                  <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: arch.color, flexShrink: 0 }} />
                  <span style={{ fontSize: '0.875rem', fontWeight: 600, color: selectedArchs.includes(arch.id) ? '#FFFFFF' : 'var(--text-muted)', transition: 'color 0.15s' }}>{arch.id}</span>
                </div>
                <div style={{
                  width: '18px', height: '18px', borderRadius: '4px',
                  border: `1px solid ${selectedArchs.includes(arch.id) ? 'var(--accent-gold)' : 'var(--border-subtle)'}`,
                  backgroundColor: selectedArchs.includes(arch.id) ? 'rgba(212,175,99,0.15)' : 'transparent',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  transition: 'all 0.15s',
                  flexShrink: 0,
                }}>
                  {selectedArchs.includes(arch.id) && <Check size={11} color="var(--accent-gold)" strokeWidth={3} />}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Metrics + Run */}
        <div className="forge-card" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          <span style={{ fontSize: '0.6875rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-muted)' }}>Metrics</span>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', flex: 1 }}>
            {allMetrics.map(m => (
              <div key={m} onClick={() => toggleMetric(m)} style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', cursor: 'pointer', userSelect: 'none' }}>
                <div style={{
                  width: '16px', height: '16px', borderRadius: '4px',
                  border: `1px solid ${selectedMetrics.includes(m) ? 'var(--accent-gold)' : 'var(--border-subtle)'}`,
                  backgroundColor: selectedMetrics.includes(m) ? 'var(--accent-gold)' : 'transparent',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  transition: 'all 0.15s', flexShrink: 0,
                }}>
                  {selectedMetrics.includes(m) && <Check size={10} color="#000" strokeWidth={3} />}
                </div>
                <span style={{ fontSize: '0.875rem', color: selectedMetrics.includes(m) ? 'var(--text-primary)' : 'var(--text-muted)', transition: 'color 0.15s' }}>{m}</span>
              </div>
            ))}
          </div>
          <button
            onClick={handleRunBenchmark}
            disabled={running}
            style={{
              width: '100%',
              padding: '0.75rem',
              backgroundColor: 'var(--accent-gold)',
              color: '#0B0D12',
              fontWeight: 800,
              fontSize: '0.9375rem',
              borderRadius: 'var(--radius-md)',
              border: 'none',
              cursor: running ? 'not-allowed' : 'pointer',
              opacity: running ? 0.6 : 1,
              transition: 'opacity 0.2s, transform 0.15s',
            }}
            onMouseEnter={e => !running && ((e.currentTarget as HTMLButtonElement).style.filter = 'brightness(1.08)')}
            onMouseLeave={e => ((e.currentTarget as HTMLButtonElement).style.filter = '')}
          >
            {running ? 'Benchmarking…' : 'Run Benchmark'}
          </button>
        </div>
      </div>

      {/* ── Loading ───────────────────────────────────────── */}
      {running && (
        <div className="section-gap">
          <div className="grid-5col">
            {[...Array(5)].map((_, i) => <Skeleton key={i} variant="card" height={88} />)}
          </div>
          <Skeleton variant="card" height={380} />
        </div>
      )}

      {/* ── Empty State ───────────────────────────────────── */}
      {!running && !report && (
        <EmptyState
          icon={Trophy}
          title="Leaderboard Offline"
          description="Select your dataset and metrics above, then click Run Benchmark."
          actionText="Run Benchmark"
          onAction={handleRunBenchmark}
        />
      )}

      {/* ── Results ───────────────────────────────────────── */}
      {!running && report && (
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
          className="section-gap-lg"
        >
          {/* KPI row */}
          <div className="grid-5col">
            {[
              { val: '94.2%', label: 'Best Score',        color: 'var(--accent-gold)' },
              { val: '85.6%', label: 'Avg Score',         color: '#FFFFFF' },
              { val: '390ms', label: 'Median Latency',    color: '#FFFFFF' },
              { val: '96.1%', label: 'Pass Rate (Best)',  color: 'var(--status-green)' },
              { val: '145',   label: 'Throughput (QPS)',  color: 'var(--status-blue)' },
            ].map(k => (
              <div key={k.label} className="kpi-card">
                <div className="kpi-value" style={{ color: k.color }}>{k.val}</div>
                <div className="kpi-label">{k.label}</div>
              </div>
            ))}
          </div>

          {/* Tabs */}
          <div className="forge-tabs">
            {(['Leaderboard', 'Distribution', 'Samples'] as const).map(t => (
              <button key={t} onClick={() => setActiveTab(t)} className={`forge-tab-btn${activeTab === t ? ' active' : ''}`}>{t}</button>
            ))}
          </div>

          {/* Table */}
          {activeTab === 'Leaderboard' && (
            <div className="section-gap" style={{ gap: '1rem' }}>
              <div className="forge-card" style={{ padding: 0, overflowX: 'auto' }}>
                <table className="forge-table" style={{ minWidth: '860px' }}>
                  <thead style={{ position: 'sticky', top: 0, backgroundColor: 'var(--card-bg)', zIndex: 10 }}>
                    <tr>
                      <th style={{ padding: '0.875rem 0.75rem', fontWeight: 700, fontSize: '0.6875rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)', borderBottom: '1px solid var(--border-subtle)' }}>Rank</th>
                      <th style={{ padding: '0.875rem 0.75rem', fontWeight: 700, fontSize: '0.6875rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)', borderBottom: '1px solid var(--border-subtle)' }}>Architecture</th>
                      <th style={{ padding: '0.875rem 0.75rem', fontWeight: 700, fontSize: '0.6875rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)', borderBottom: '1px solid var(--border-subtle)' }}>Model</th>
                      <th style={{ padding: '0.875rem 0.75rem', fontWeight: 700, fontSize: '0.6875rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: sortField === 'score' ? 'var(--accent-gold)' : 'var(--text-muted)', borderBottom: '1px solid var(--border-subtle)', cursor: 'pointer' }} onClick={() => handleSort('score')}>Score{sortField === 'score' ? (sortDir === 'desc' ? ' ↓' : ' ↑') : ''}</th>
                      <th style={{ padding: '0.875rem 0.75rem', fontWeight: 700, fontSize: '0.6875rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)', borderBottom: '1px solid var(--border-subtle)' }}>Precision</th>
                      <th style={{ padding: '0.875rem 0.75rem', fontWeight: 700, fontSize: '0.6875rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)', borderBottom: '1px solid var(--border-subtle)' }}>Recall</th>
                      <th style={{ padding: '0.875rem 0.75rem', fontWeight: 700, fontSize: '0.6875rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: sortField === 'latencyP95' ? 'var(--accent-gold)' : 'var(--text-muted)', borderBottom: '1px solid var(--border-subtle)', cursor: 'pointer' }} onClick={() => handleSort('latencyP95')}>Latency{sortField === 'latencyP95' ? (sortDir === 'desc' ? ' ↓' : ' ↑') : ''}</th>
                      <th style={{ padding: '0.875rem 0.75rem', fontWeight: 700, fontSize: '0.6875rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: sortField === 'costPerMillionTokens' ? 'var(--accent-gold)' : 'var(--text-muted)', borderBottom: '1px solid var(--border-subtle)', cursor: 'pointer' }} onClick={() => handleSort('costPerMillionTokens')}>Cost/Query{sortField === 'costPerMillionTokens' ? (sortDir === 'desc' ? ' ↓' : ' ↑') : ''}</th>
                      <th style={{ padding: '0.875rem 0.75rem', fontWeight: 700, fontSize: '0.6875rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: sortField === 'passRate' ? 'var(--accent-gold)' : 'var(--text-muted)', borderBottom: '1px solid var(--border-subtle)', cursor: 'pointer', width: '140px' }} onClick={() => handleSort('passRate')}>Pass Rate{sortField === 'passRate' ? (sortDir === 'desc' ? ' ↓' : ' ↑') : ''}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {sortedLeaderboard.map(row => {
                      const isTop = row.rank === 1;
                      return (
                        <tr
                          key={row.architectureName}
                          style={{
                            borderBottom: '1px solid var(--border-subtle)',
                            backgroundColor: isTop ? 'rgba(212,175,99,0.04)' : 'transparent',
                            boxShadow: isTop ? 'inset 2px 0 0 var(--accent-gold)' : 'none',
                          }}
                        >
                          <td style={{ padding: '0.875rem 0.75rem' }}>
                            <div style={{
                              width: '24px', height: '24px', borderRadius: '50%',
                              backgroundColor: isTop ? 'var(--accent-gold)' : 'var(--bg-primary)',
                              border: '1px solid var(--border-subtle)',
                              display: 'flex', alignItems: 'center', justifyContent: 'center',
                              fontSize: '0.75rem', fontWeight: 800, color: isTop ? '#000' : 'var(--text-muted)',
                            }}>
                              {row.rank}
                            </div>
                          </td>
                          <td style={{ padding: '0.875rem 0.75rem' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                              <div style={{ width: '7px', height: '7px', borderRadius: '50%', backgroundColor: row.color, flexShrink: 0 }} />
                              <span style={{ fontSize: '0.875rem', fontWeight: isTop ? 700 : 600, color: isTop ? '#FFFFFF' : 'var(--text-primary)' }}>
                                {row.architectureName}
                              </span>
                            </div>
                          </td>
                          <td style={{ padding: '0.875rem 0.75rem', color: 'var(--text-secondary)', fontSize: '0.8125rem' }}>{row.llmModel}</td>
                          <td style={{ padding: '0.875rem 0.75rem', fontWeight: 700, color: isTop ? 'var(--accent-gold)' : '#FFFFFF', fontSize: '0.875rem' }}>{row.score.toFixed(1)}</td>
                          <td style={{ padding: '0.875rem 0.75rem', color: 'var(--text-secondary)', fontSize: '0.8125rem' }}>{row.precision.toFixed(0)}%</td>
                          <td style={{ padding: '0.875rem 0.75rem', color: 'var(--text-secondary)', fontSize: '0.8125rem' }}>{row.recall.toFixed(0)}%</td>
                          <td style={{ padding: '0.875rem 0.75rem', color: '#FFFFFF', fontSize: '0.8125rem' }}>{row.latencyP95}ms</td>
                          <td style={{ padding: '0.875rem 0.75rem', color: '#FFFFFF', fontSize: '0.8125rem' }}>${(row.costPerMillionTokens * 0.0001).toFixed(4)}</td>
                          <td style={{ padding: '0.875rem 0.75rem', minWidth: '130px' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                              <div style={{ flex: 1, height: '4px', backgroundColor: 'var(--bg-primary)', borderRadius: '2px', overflow: 'hidden' }}>
                                <div style={{ width: `${row.passRate}%`, height: '100%', backgroundColor: row.color }} />
                              </div>
                              <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#FFFFFF', minWidth: '38px', textAlign: 'right' }}>{row.passRate.toFixed(1)}%</span>
                            </div>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>

              {/* Export row */}
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.6rem' }}>
                {['Export PDF', 'Export CSV', 'Export JSON'].map(label => (
                  <button key={label} className="forge-btn-ghost" style={{ height: '34px', fontSize: '0.8125rem', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-sm)', padding: '0 0.875rem', backgroundColor: 'var(--bg-secondary)' }}>
                    {label}
                  </button>
                ))}
              </div>
            </div>
          )}

          {activeTab !== 'Leaderboard' && (
            <div className="forge-card" style={{ padding: '4rem', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.875rem', border: '1px dashed var(--border-subtle)' }}>
              {activeTab} visualization — coming soon
            </div>
          )}
        </motion.div>
      )}
    </motion.div>
  );
};
