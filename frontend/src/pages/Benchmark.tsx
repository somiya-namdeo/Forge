import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Trophy,
  Play,
  CheckCircle2,
  Sliders,
  Award,
  Zap,
  DollarSign,
  TrendingUp,
  RotateCcw,
  Database,
  Cpu
} from 'lucide-react';
import { Card, Badge, Button, ScoreRing, ProgressBar, EmptyState, Skeleton, LoadingIndicator } from '../components/common';
import { BenchmarkReport } from '../types';
import { benchmarkService } from '../services';

export const Benchmark: React.FC = () => {
  // Configuration inputs
  const [selectedDataset, setSelectedDataset] = useState('Legal 5M Corpus');
  const [selectedMetrics, setSelectedMetrics] = useState<string[]>(['Latency p95', 'Throughput', 'Factual Accuracy', 'Cost per 1M tokens']);
  const [selectedArchs, setSelectedArchs] = useState<string[]>([
    'Forge Optimized Hybrid Stack',
    'Proprietary Cloud Baseline',
    'Open Weights Fast Pipeline',
    'Legacy Dense RAG Stack'
  ]);
  
  // Execution State
  const [running, setRunning] = useState(false);
  const [report, setReport] = useState<BenchmarkReport | null>(null);

  const handleRunBenchmark = async () => {
    setRunning(true);
    setReport(null);
    const data = await benchmarkService.runBenchmark({
      dataset: selectedDataset,
      metrics: selectedMetrics,
      architectures: selectedArchs
    });
    setReport(data);
    setRunning(false);
  };

  const toggleMetric = (metric: string) => {
    if (selectedMetrics.includes(metric)) {
      if (selectedMetrics.length > 1) setSelectedMetrics(selectedMetrics.filter(m => m !== metric));
    } else {
      setSelectedMetrics([...selectedMetrics, metric]);
    }
  };

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
            <Badge variant="gold">● COMPARATIVE BENCHMARK</Badge>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Multi-Stack Performance Leaderboard</span>
          </div>
          <h1 style={{ fontSize: '2.5rem', fontWeight: 800 }}>
            Architecture Benchmarking Studio
          </h1>
          <p style={{ fontSize: '1.05rem', color: 'var(--text-secondary)', maxWidth: '750px', marginTop: '0.4rem' }}>
            A/B benchmark candidate LLMs and vector database combinations against real enterprise datasets to uncover p95 latency outliers and token economics before scaling.
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          {report && (
            <Button variant="ghost" icon={RotateCcw} onClick={handleRunBenchmark} disabled={running}>
              Rerun Benchmark
            </Button>
          )}
          <Button variant="primary" icon={Play} onClick={handleRunBenchmark} disabled={running} style={{ padding: '0.8rem 1.8rem' }}>
            {running ? 'Benchmarking Stacks...' : 'Run Benchmark Suite'}
          </Button>
        </div>
      </header>

      {/* Benchmark Configuration Panel */}
      <section>
        <Card style={{ padding: '1.8rem', backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--border-hover)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.4rem', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '1rem' }}>
            <Sliders size={20} style={{ color: 'var(--accent-gold)' }} />
            <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#FFFFFF' }}>Benchmark Configuration Workflow</h3>
          </div>

          <div className="grid-3col" style={{ gap: '2rem' }}>
            {/* Step 1: Dataset Selection */}
            <div>
              <label style={{ display: 'block', fontSize: '0.82rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', marginBottom: '0.65rem' }}>
                1. Select Benchmark Dataset
              </label>
              <select
                value={selectedDataset}
                onChange={(e) => setSelectedDataset(e.target.value)}
                style={{
                  width: '100%',
                  padding: '0.75rem 1rem',
                  borderRadius: '12px',
                  backgroundColor: 'var(--card-bg)',
                  color: '#FFFFFF',
                  border: '1px solid var(--border-subtle)',
                  fontSize: '0.95rem',
                  fontWeight: 600,
                  outline: 'none',
                }}
              >
                <option value="Legal 5M Corpus">Legal 5M RAG Corpus (High Precision)</option>
                <option value="Medical PubMed Benchmark">Medical PubMed Benchmark (Factual Entailment)</option>
                <option value="Financial SEC filings">Financial SEC Filings (Multi-Table Reasoning)</option>
                <option value="Code Repo 50k">Code Repository Analysis (Long Context)</option>
              </select>
            </div>

            {/* Step 2: Target Architectures */}
            <div>
              <label style={{ display: 'block', fontSize: '0.82rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', marginBottom: '0.65rem' }}>
                2. Target Stacks Included ({selectedArchs.length})
              </label>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.45rem', fontSize: '0.88rem', color: 'var(--text-secondary)' }}>
                {selectedArchs.map(a => (
                  <div key={a} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 600 }}>
                    <CheckCircle2 size={16} style={{ color: 'var(--status-green)' }} /> {a}
                  </div>
                ))}
              </div>
            </div>

            {/* Step 3: Choose Metrics */}
            <div>
              <label style={{ display: 'block', fontSize: '0.82rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', marginBottom: '0.65rem' }}>
                3. Active Evaluation Metrics
              </label>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                {['Latency p95', 'Throughput', 'Factual Accuracy', 'Cost per 1M tokens', 'Memory Footprint', 'QPS Max'].map(metric => {
                  const active = selectedMetrics.includes(metric);
                  return (
                    <button
                      key={metric}
                      type="button"
                      onClick={() => toggleMetric(metric)}
                      style={{
                        padding: '0.4rem 0.85rem',
                        borderRadius: 'var(--radius-pill)',
                        fontSize: '0.8rem',
                        fontWeight: active ? 700 : 500,
                        backgroundColor: active ? 'rgba(212, 175, 99, 0.2)' : 'rgba(255,255,255,0.04)',
                        color: active ? 'var(--accent-gold)' : 'var(--text-muted)',
                        border: active ? '1px solid var(--border-accent)' : '1px solid var(--border-subtle)',
                        transition: 'all 0.2s',
                      }}
                    >
                      {active ? '✔ ' : ''}{metric}
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
        </Card>
      </section>

      {/* State 1: Running Benchmark */}
      {running && (
        <Card style={{ padding: '4rem 2rem', border: '1px dashed var(--border-accent)' }}>
          <LoadingIndicator label={`Executing comprehensive benchmarking suite across ${selectedDataset} for ${selectedArchs.length} architecture variants...`} size={46} />
        </Card>
      )}

      {/* State 2: Initial Empty State (Strict Policy: No Leaderboard Data Before Execution) */}
      {!running && !report && (
        <EmptyState
          icon={Trophy}
          title="Leaderboard Offline"
          description="Do not display leaderboard data before a benchmark is executed. Select your desired dataset and metrics above, then click 'Run Benchmark Suite' to generate comparative data."
          actionText="Run Comparative Benchmark"
          onAction={handleRunBenchmark}
        />
      )}

      {/* State 3: Animated Results Leaderboard & Statistics */}
      {!running && report && (
        <motion.section
          initial={{ opacity: 0, scale: 0.98 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.4 }}
          style={{ display: 'flex', flexDirection: 'column', gap: '2.5rem' }}
        >
          {/* Executive Insights Box */}
          <Card style={{ padding: '1.8rem 2rem', backgroundColor: 'rgba(212, 175, 99, 0.04)', border: '1px solid var(--border-accent)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem', color: 'var(--accent-gold)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              <TrendingUp size={20} /> Executive Benchmark Insights ({report.testName})
            </div>
            <div className="grid-3col" style={{ gap: '1.5rem' }}>
              {report.summaryInsights.map((insight, ii) => (
                <div key={ii} style={{ padding: '1rem', backgroundColor: 'var(--bg-primary)', borderRadius: '12px', border: '1px solid var(--border-subtle)', fontSize: '0.92rem', color: 'var(--text-primary)', lineHeight: 1.5 }}>
                  <strong style={{ color: 'var(--accent-gold)' }}>Insight #{ii + 1}:</strong> {insight}
                </div>
              ))}
            </div>
          </Card>

          {/* Comparative Leaderboard Table */}
          <Card style={{ padding: '1.8rem', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <h3 style={{ fontSize: '1.3rem', fontWeight: 800, color: '#FFFFFF', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <Trophy style={{ color: 'var(--accent-gold)' }} size={24} /> Performance Leaderboard
              </h3>
              <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Tested {report.totalQueriesProcessed} concurrent queries in {report.durationSeconds}s</span>
            </div>

            <div style={{ overflowX: 'auto', width: '100%' }}>
              <table style={{ width: '100%', borderCollapse: 'separate', borderSpacing: '0 0.6rem', textAlign: 'left' }}>
                <thead>
                  <tr style={{ color: 'var(--text-muted)', fontSize: '0.78rem', textTransform: 'uppercase', letterSpacing: '0.04em', borderBottom: '1px solid var(--border-subtle)' }}>
                    <th style={{ padding: '0.8rem 1rem' }}>Rank</th>
                    <th style={{ padding: '0.8rem 1rem' }}>Architecture Pipeline</th>
                    <th style={{ padding: '0.8rem 1rem' }}>LLM Engine</th>
                    <th style={{ padding: '0.8rem 1rem' }}>Vector DB Store</th>
                    <th style={{ padding: '0.8rem 1rem' }}>P95 Latency</th>
                    <th style={{ padding: '0.8rem 1rem' }}>Throughput</th>
                    <th style={{ padding: '0.8rem 1rem' }}>Accuracy</th>
                    <th style={{ padding: '0.8rem 1rem' }}>Token Cost</th>
                  </tr>
                </thead>
                <tbody>
                  {report.leaderboard.map((row, index) => {
                    const isWinner = row.rank === 1;
                    return (
                      <motion.tr
                        key={row.architectureName}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.25, delay: index * 0.08 }}
                        style={{
                          backgroundColor: isWinner ? 'rgba(212, 175, 99, 0.12)' : 'var(--bg-secondary)',
                          boxShadow: isWinner ? 'var(--shadow-glow-gold)' : '0 2px 10px rgba(0,0,0,0.3)',
                          borderRadius: '14px',
                          border: isWinner ? '1px solid var(--accent-gold)' : '1px solid var(--border-subtle)',
                          fontWeight: isWinner ? 700 : 500,
                        }}
                      >
                        <td style={{ padding: '1.2rem 1rem', borderTopLeftRadius: '14px', borderBottomLeftRadius: '14px' }}>
                          <span style={{
                            width: '32px',
                            height: '32px',
                            borderRadius: '50%',
                            backgroundColor: isWinner ? 'var(--accent-gold)' : 'rgba(255,255,255,0.1)',
                            color: isWinner ? '#0B0D12' : '#FFFFFF',
                            display: 'inline-flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            fontWeight: 800,
                          }}>
                            #{row.rank}
                          </span>
                        </td>
                        <td style={{ padding: '1.2rem 1rem', color: '#FFFFFF', fontSize: '1.02rem' }}>
                          {row.architectureName}
                          {isWinner && <Badge variant="gold" style={{ marginLeft: '0.6rem', fontSize: '0.7rem' }}>CHAMPION</Badge>}
                        </td>
                        <td style={{ padding: '1.2rem 1rem', color: 'var(--text-secondary)' }}>{row.llmModel}</td>
                        <td style={{ padding: '1.2rem 1rem', color: 'var(--text-secondary)' }}>{row.vectorDb}</td>
                        <td style={{ padding: '1.2rem 1rem', color: isWinner ? 'var(--status-green)' : 'var(--text-primary)', fontWeight: 700 }}>
                          {row.latencyP95}ms
                        </td>
                        <td style={{ padding: '1.2rem 1rem', color: 'var(--status-blue)', fontWeight: 700 }}>
                          {row.throughputTokSec} tok/s
                        </td>
                        <td style={{ padding: '1.2rem 1rem', color: 'var(--accent-gold)', fontWeight: 700 }}>
                          {row.accuracyScore}%
                        </td>
                        <td style={{ padding: '1.2rem 1rem', borderTopRightRadius: '14px', borderBottomRightRadius: '14px', color: '#FFFFFF', fontWeight: 700 }}>
                          ${row.costPerMillionTokens.toFixed(2)} / 1M tok
                        </td>
                      </motion.tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </Card>
        </motion.section>
      )}
    </motion.div>
  );
};
