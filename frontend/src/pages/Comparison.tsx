import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle, Sparkles, Layers } from 'lucide-react';
import { Card, Badge, Skeleton } from '../components/common';
import { GeneratedArchitecture } from '../types';
import { decisionService, comparisonService, ArchitectureComparisonResult } from '../services';

export const Comparison: React.FC = () => {
  const [archA, setArchA]           = useState<GeneratedArchitecture | null>(null);
  const [archB, setArchB]           = useState<GeneratedArchitecture | null>(null);
  const [comparison, setComparison] = useState<ArchitectureComparisonResult | null>(null);
  const [loading, setLoading]       = useState(true);
  const [activeTab, setActiveTab]   = useState<'Comparison Matrix' | 'Radar Chart' | 'Migration Guide'>('Comparison Matrix');

  useEffect(() => {
    async function init() {
      setLoading(true);
      const stackA = await decisionService.generateFromPrompt(
        'Open Weights Fast Pipeline with Qdrant Rust and Llama 3.3 70B', 'Forge Optimized Stack');
      const stackB: GeneratedArchitecture = {
        ...stackA,
        id: 'arch-baseline-cloud',
        title: 'Dense RAG v1',
        summary: { ...stackA.summary, overallScore: 87, estimatedMonthlyCost: '$1,450 / mo', estimatedLatency: '~680ms (p95)', complexity: 'Low', reasoningConfidence: '96.2% High' },
      };
      setArchA(stackA);
      setArchB(stackB);
      const result = await comparisonService.compareArchitectures(stackA, stackB);
      setComparison(result);
      setLoading(false);
    }
    init();
  }, []);

  if (loading || !comparison || !archA || !archB) {
    return (
      <div className="section-gap-lg">
        <Skeleton variant="title" width={320} />
        <div style={{ display: 'flex', gap: '2rem' }}>
          <Skeleton variant="card" height={420} />
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', width: '100px' }}>
            <Skeleton variant="text" width={60} />
          </div>
          <Skeleton variant="card" height={420} />
        </div>
        <Skeleton variant="chart" height={340} />
      </div>
    );
  }

  const archBScore = 87.4;
  const archAScore = archA.summary.overallScore;

  // ── Arch card (shared layout) ────────────────────────────────
  const ArchCard = ({
    label, title, score, chips, components, latency, cost, isWinner, accentColor,
  }: {
    label: string; title: string; score: number; chips: string[];
    components: [string, string][]; latency: string; cost: string;
    isWinner?: boolean; accentColor: string;
  }) => (
    <div
      className="forge-card"
      style={{
        flex: 1,
        padding: '1.75rem',
        border: `1px solid ${isWinner ? 'var(--accent-gold)' : 'var(--border-subtle)'}`,
        display: 'flex', flexDirection: 'column', gap: '1.25rem',
        position: 'relative',
      }}
    >
      {isWinner && (
        <div style={{ position: 'absolute', top: '-13px', left: '50%', transform: 'translateX(-50%)', zIndex: 2 }}>
          <Badge variant="gold" style={{ padding: '0.3rem 0.875rem', fontSize: '0.6875rem', fontWeight: 800 }}>★ WINNER</Badge>
        </div>
      )}

      {/* Label + title */}
      <div>
        <Badge variant={isWinner ? 'gold' : 'blue'} style={{ marginBottom: '0.6rem', fontSize: '0.6875rem' }}>{label}</Badge>
        <h2 style={{ fontSize: '1.375rem', fontWeight: 800, color: '#FFFFFF', lineHeight: 1.2 }}>{title}</h2>

        {/* Score */}
        <div style={{ marginTop: '0.4rem', fontSize: '0.875rem', fontWeight: 700, color: accentColor }}>
          Score: {score} / 100
        </div>

        {/* Capability chips */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem', marginTop: '0.75rem' }}>
          {chips.map(c => (
            <span key={c} className="forge-chip">{c}</span>
          ))}
        </div>
      </div>

      {/* Component rows */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem', fontSize: '0.875rem' }}>
        {components.map(([k, v]) => (
          <div key={k} style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '0.4rem' }}>
            <span style={{ color: 'var(--text-muted)' }}>{k}</span>
            <span style={{ color: v === 'None' ? 'var(--text-muted)' : '#FFFFFF', fontWeight: 600, textAlign: 'right', maxWidth: '55%' }}>{v}</span>
          </div>
        ))}
      </div>

      {/* Latency / Cost mini cards */}
      <div style={{ display: 'flex', gap: '0.75rem', marginTop: 'auto' }}>
        {[['LATENCY', latency], ['COST/QUERY', cost]].map(([lbl, val]) => (
          <div key={lbl} style={{ flex: 1, background: 'var(--bg-primary)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-sm)', padding: '0.875rem 1rem' }}>
            <div style={{ fontSize: '0.625rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-muted)', marginBottom: '0.2rem' }}>{lbl}</div>
            <div style={{ fontSize: '1.25rem', fontWeight: 800, color: accentColor }}>{val}</div>
          </div>
        ))}
      </div>
    </div>
  );

  // ── Comparison table rows ────────────────────────────────────
  const rows = [
    { metric: 'Faithfulness',    a: '94%',    b: '86%',    aWin: true },
    { metric: 'Answer Relevancy',a: '91%',    b: '84%',    aWin: true },
    { metric: 'Precision@5',     a: '89%',    b: '80%',    aWin: true },
    { metric: 'Recall@10',       a: '91%',    b: '83%',    aWin: true },
    { metric: 'Latency (avg)',   a: '342ms',  b: '680ms',  aWin: true },
    { metric: 'Cost / Query',    a: '$0.0021',b: '$0.0089',aWin: true },
    { metric: 'Pass Rate',       a: '96.1%',  b: '90.1%',  aWin: true },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.3 }}
      className="section-gap-lg"
    >
      {/* ── Header ────────────────────────────────────────── */}
      <div>
        <h1 className="page-title">Architecture Comparison</h1>
        <p className="page-subtitle">Side-by-side analysis with recommendation</p>
      </div>

      {/* ── Side-by-side cards + VS divider ─────────────── */}
      <div style={{ display: 'flex', alignItems: 'stretch', gap: '1.5rem' }}>
        <ArchCard
          label="Architecture A"
          title="Hybrid RAG v2"
          score={archAScore}
          chips={['Open Source', 'High Performance', 'Production Ready']}
          components={[
            ['LLM', 'Llama 3.3 70B + Groq'],
            ['Embedding', 'text-embedding-3-large'],
            ['Vector DB', 'Qdrant'],
            ['Retriever', 'Hybrid BM25+Dense'],
            ['Reranker', 'BGE-Reranker-v2'],
            ['Framework', 'LlamaIndex'],
          ]}
          latency="342ms"
          cost="$0.0021"
          isWinner
          accentColor="var(--accent-gold)"
        />

        {/* VS column */}
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '1.25rem', width: '96px', flexShrink: 0 }}>
          <div style={{ width: '44px', height: '44px', borderRadius: '50%', backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--border-hover)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 800, color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
            VS
          </div>
          <div style={{ width: '1px', height: '32px', backgroundColor: 'var(--border-subtle)' }} />
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.5rem', textAlign: 'center' }}>
            <span style={{ fontSize: '0.625rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em' }}>Winner</span>
            <span style={{ fontSize: '0.75rem', color: 'var(--accent-gold)', fontWeight: 700, lineHeight: 1.3 }}>Hybrid RAG v2</span>
          </div>
          <div style={{ width: '1px', height: '32px', backgroundColor: 'var(--border-subtle)' }} />
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem', fontSize: '0.75rem', fontWeight: 600, color: 'var(--status-green)', textAlign: 'center', lineHeight: 1.3 }}>
            <span>+{(archAScore - archBScore).toFixed(1)} Score</span>
            <span>−76% Cost</span>
            <span>−338ms Latency</span>
          </div>
        </div>

        <ArchCard
          label="Architecture B"
          title="Dense RAG v1"
          score={archBScore}
          chips={['Proprietary', 'Enterprise', 'Managed']}
          components={[
            ['LLM', 'GPT-4o'],
            ['Embedding', 'text-embedding-3-small'],
            ['Vector DB', 'Pinecone'],
            ['Retriever', 'Dense Only'],
            ['Reranker', 'None'],
            ['Framework', 'LangChain'],
          ]}
          latency="680ms"
          cost="$0.0089"
          accentColor="var(--status-blue)"
        />
      </div>

      {/* ── Tabs ──────────────────────────────────────────── */}
      <div className="forge-tabs">
        {(['Comparison Matrix', 'Radar Chart', 'Migration Guide'] as const).map(t => (
          <button key={t} onClick={() => setActiveTab(t)} className={`forge-tab-btn${activeTab === t ? ' active' : ''}`}>{t}</button>
        ))}
      </div>

      {/* ── Comparison Matrix ─────────────────────────────── */}
      {activeTab === 'Comparison Matrix' && (
        <div className="forge-card" style={{ padding: 0, overflowX: 'auto' }}>
          <table className="forge-table" style={{ minWidth: '600px' }}>
            <thead>
              <tr>
                <th style={{ padding: '0.875rem 1.25rem', color: 'var(--text-muted)', borderBottom: '1px solid var(--border-subtle)' }}>Metric</th>
                <th style={{ padding: '0.875rem 1.25rem', color: 'var(--accent-gold)', borderBottom: '1px solid var(--border-subtle)', fontWeight: 700, fontSize: '0.6875rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Hybrid RAG v2</th>
                <th style={{ padding: '0.875rem 1.25rem', color: 'var(--status-blue)', borderBottom: '1px solid var(--border-subtle)', fontWeight: 700, fontSize: '0.6875rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Dense RAG v1</th>
                <th style={{ padding: '0.875rem 1.25rem', color: 'var(--text-muted)', borderBottom: '1px solid var(--border-subtle)', textAlign: 'right' }}>Winner</th>
              </tr>
            </thead>
            <tbody>
              {rows.map(r => (
                <tr key={r.metric} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                  <td style={{ padding: '1rem 1.25rem', fontWeight: 600, color: 'var(--text-primary)' }}>{r.metric}</td>
                  <td style={{ padding: '1rem 1.25rem', fontWeight: 700, color: r.aWin ? 'var(--accent-gold)' : 'var(--text-secondary)' }}>{r.a}</td>
                  <td style={{ padding: '1rem 1.25rem', color: r.aWin ? 'var(--text-secondary)' : 'var(--status-blue)', fontWeight: r.aWin ? 400 : 700 }}>{r.b}</td>
                  <td style={{ padding: '1rem 1.25rem', textAlign: 'right' }}>
                    <span style={{
                      padding: '0.25rem 0.75rem', borderRadius: 'var(--radius-pill)',
                      border: '1px solid var(--accent-gold)', color: 'var(--accent-gold)',
                      backgroundColor: 'rgba(212,175,99,0.08)', fontSize: '0.75rem', fontWeight: 700,
                    }}>
                      {r.aWin ? 'Hybrid RAG v2' : 'Dense RAG v1'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* ── Migration Guide ───────────────────────────────── */}
      {activeTab === 'Migration Guide' && (
        <div className="forge-card" style={{ padding: '1.75rem', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <h3 style={{ fontSize: '1.125rem', fontWeight: 800, color: '#FFFFFF' }}>Migration Strategy: Dense RAG v1 → Hybrid RAG v2</h3>
          <div className="grid-2col" style={{ gap: '1.5rem' }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.8125rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.04em', marginBottom: '0.875rem' }}>
                <Layers size={14} /> Components to Replace
              </div>
              <ul style={{ paddingLeft: '1.25rem', display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.875rem', color: 'var(--text-primary)' }}>
                <li>Replace <strong style={{ color: 'var(--status-blue)' }}>GPT-4o</strong> → <strong style={{ color: 'var(--accent-gold)' }}>Llama 3.3 70B (Groq)</strong></li>
                <li>Migrate <strong style={{ color: 'var(--status-blue)' }}>Pinecone</strong> → <strong style={{ color: 'var(--accent-gold)' }}>Qdrant</strong></li>
                <li>Add <strong style={{ color: 'var(--accent-gold)' }}>BGE-Reranker-v2</strong> to pipeline</li>
                <li>Refactor <strong style={{ color: 'var(--status-blue)' }}>LangChain</strong> → <strong style={{ color: 'var(--accent-gold)' }}>LlamaIndex</strong></li>
              </ul>
            </div>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.8125rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.04em', marginBottom: '0.875rem' }}>
                <Sparkles size={14} /> Expected Benefits
              </div>
              <ul style={{ paddingLeft: '1.25rem', display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.875rem', color: 'var(--text-primary)' }}>
                <li><strong style={{ color: 'var(--status-green)' }}>76% cost reduction</strong> via open-weights inference</li>
                <li><strong style={{ color: 'var(--status-green)' }}>49% latency improvement</strong> via Groq LPU</li>
                <li>Improved recall from hybrid search + reranking</li>
              </ul>
            </div>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.8125rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.04em', marginBottom: '0.875rem' }}>
                <AlertTriangle size={14} /> Risks & Considerations
              </div>
              <ul style={{ paddingLeft: '1.25rem', display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.875rem', color: 'var(--text-primary)' }}>
                <li>Full corpus re-embedding required during migration</li>
                <li>Prompt adjustment for Llama instruction following</li>
                <li>LlamaIndex learning curve for the engineering team</li>
              </ul>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {[['Migration Complexity', 'Medium – High', 'var(--status-orange)'], ['Estimated Time to Production', '2–3 Weeks', '#FFFFFF']].map(([lbl, val, clr]) => (
                <div key={lbl as string} style={{ background: 'var(--bg-primary)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-sm)', padding: '0.875rem 1rem' }}>
                  <div style={{ fontSize: '0.625rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-muted)', marginBottom: '0.2rem' }}>{lbl}</div>
                  <div style={{ fontSize: '1.0625rem', fontWeight: 800, color: clr as string }}>{val}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {activeTab === 'Radar Chart' && (
        <div className="forge-card" style={{ padding: '4rem', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.875rem', border: '1px dashed var(--border-subtle)' }}>
          Radar chart visualization — coming soon
        </div>
      )}
    </motion.div>
  );
};
