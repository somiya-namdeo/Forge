import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Scale,
  Check,
  Zap,
  DollarSign,
  Layers,
  ArrowRight,
  Sparkles,
  ShieldAlert,
  Sliders
} from 'lucide-react';
import { Card, Badge, Button, ScoreRing, ProgressBar, EmptyState, Skeleton } from '../components/common';
import { GeneratedArchitecture } from '../types';
import { decisionService, comparisonService, ArchitectureComparisonResult } from '../services';

export const Comparison: React.FC = () => {
  const [archA, setArchA] = useState<GeneratedArchitecture | null>(null);
  const [archB, setArchB] = useState<GeneratedArchitecture | null>(null);
  const [comparison, setComparison] = useState<ArchitectureComparisonResult | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function initComparison() {
      setLoading(true);
      // Construct two realistic candidate architectures to demonstrate side-by-side differentials
      const stackA = await decisionService.generateFromPrompt(
        'Open Weights Fast Pipeline with Qdrant Rust and Llama 3.3 70B',
        'Forge Optimized Stack'
      );
      
      // Customize stack B to act as Proprietary Cloud Baseline
      const stackB: GeneratedArchitecture = {
        ...stackA,
        id: 'arch-baseline-cloud',
        title: 'Proprietary Cloud Baseline (GPT-4o + Pinecone)',
        summary: {
          ...stackA.summary,
          overallScore: 88,
          estimatedMonthlyCost: '$1,450 / mo',
          estimatedLatency: '~420ms (p95)',
          complexity: 'Low',
          reasoningConfidence: '96.2% High'
        }
      };

      setArchA(stackA);
      setArchB(stackB);

      const result = await comparisonService.compareArchitectures(stackA, stackB);
      setComparison(result);
      setLoading(false);
    }
    initComparison();
  }, []);

  if (loading || !comparison || !archA || !archB) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
        <Skeleton variant="title" width={340} />
        <div className="grid-2col">
          <Skeleton variant="card" height={320} />
          <Skeleton variant="card" height={320} />
        </div>
        <Skeleton variant="chart" height={400} />
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.35 }}
      style={{ display: 'flex', flexDirection: 'column', gap: '2.5rem' }}
    >
      {/* Header */}
      <header style={{ borderBottom: '1px solid var(--border-subtle)', paddingBottom: '1.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
          <Badge variant="gold">● A/B COMPARISON ENGINE</Badge>
          <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Side-by-Side Trade-off Analysis</span>
        </div>
        <h1 style={{ fontSize: '2.5rem', fontWeight: 800 }}>
          Architecture Comparison Matrix
        </h1>
        <p style={{ fontSize: '1.05rem', color: 'var(--text-secondary)', maxWidth: '750px', marginTop: '0.4rem' }}>
          Compare open-weights infrastructure against proprietary cloud baselines. Analyze latency differentials, token operational costs, and data sovereignty trade-offs side by side.
        </p>
      </header>

      {/* Candidate Selector Cards (Side by Side) */}
      <section className="grid-2col" style={{ gap: '2rem' }}>
        
        {/* Architecture A */}
        <Card style={{ padding: '2rem', border: '1px solid var(--border-accent)', background: 'linear-gradient(135deg, rgba(212,175,99,0.05) 0%, rgba(19,23,32,1) 100%)', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div>
              <Badge variant="gold">CANDIDATE A (RECOMMENDED)</Badge>
              <h2 style={{ fontSize: '1.5rem', fontWeight: 800, color: '#FFFFFF', marginTop: '0.5rem' }}>
                {archA.title}
              </h2>
            </div>
            <ScoreRing score={archA.summary.overallScore} size={60} strokeWidth={5} />
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.6rem' }}>
            <Badge variant="green">{archA.summary.productionReadiness}</Badge>
            <Badge variant="neutral">{archA.summary.estimatedMonthlyCost}</Badge>
            <Badge variant="neutral">{archA.summary.estimatedLatency}</Badge>
          </div>
        </Card>

        {/* Architecture B */}
        <Card style={{ padding: '2rem', border: '1px solid var(--border-subtle)', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div>
              <Badge variant="blue">CANDIDATE B (BASELINE)</Badge>
              <h2 style={{ fontSize: '1.5rem', fontWeight: 800, color: '#FFFFFF', marginTop: '0.5rem' }}>
                {archB.title}
              </h2>
            </div>
            <ScoreRing score={archB.summary.overallScore} size={60} strokeWidth={5} />
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.6rem' }}>
            <Badge variant="blue">Cloud SaaS Baseline</Badge>
            <Badge variant="neutral">{archB.summary.estimatedMonthlyCost}</Badge>
            <Badge variant="neutral">{archB.summary.estimatedLatency}</Badge>
          </div>
        </Card>
      </section>

      {/* Metric Comparison Table */}
      <section>
        <Card style={{ padding: '2rem', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <h3 style={{ fontSize: '1.3rem', fontWeight: 800, color: '#FFFFFF', textTransform: 'uppercase', letterSpacing: '0.03em' }}>
            Key Performance Metrics Comparison
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {comparison.metricComparison.map((item, index) => (
              <div
                key={index}
                style={{
                  padding: '1.25rem',
                  backgroundColor: 'var(--bg-secondary)',
                  borderRadius: '14px',
                  border: '1px solid var(--border-subtle)',
                  display: 'grid',
                  gridTemplateColumns: '1.5fr 1fr 1fr 2fr',
                  alignItems: 'center',
                  gap: '1.5rem',
                }}
              >
                <div>
                  <div style={{ fontSize: '1.02rem', fontWeight: 700, color: '#FFFFFF' }}>{item.metricName}</div>
                  <Badge variant={item.winner === 'A' ? 'gold' : item.winner === 'B' ? 'blue' : 'neutral'} style={{ fontSize: '0.7rem', marginTop: '0.3rem' }}>
                    {item.winner === 'TIE' ? 'EQUAL RATING' : `WINNER: CANDIDATE ${item.winner}`}
                  </Badge>
                </div>

                <div>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Candidate A</span>
                  <div style={{ fontSize: '1.25rem', fontWeight: 800, color: item.winner === 'A' || item.winner === 'TIE' ? 'var(--status-green)' : 'var(--text-primary)' }}>
                    {item.valueA}
                  </div>
                </div>

                <div>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Candidate B</span>
                  <div style={{ fontSize: '1.25rem', fontWeight: 800, color: item.winner === 'B' ? 'var(--status-blue)' : 'var(--text-secondary)' }}>
                    {item.valueB}
                  </div>
                </div>

                <div style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', lineHeight: 1.4, borderLeft: '1px solid var(--border-hover)', paddingLeft: '1.2rem' }}>
                  <strong style={{ color: 'var(--text-primary)' }}>Engineering Insight:</strong> {item.insight}
                </div>
              </div>
            ))}
          </div>
        </Card>
      </section>

      {/* Component Diff Trade-off Matrix */}
      <section>
        <Card style={{ padding: '2rem', display: 'flex', flexDirection: 'column', gap: '1.5rem', backgroundColor: 'var(--bg-primary)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <Sliders size={22} style={{ color: 'var(--accent-gold)' }} />
            <h3 style={{ fontSize: '1.3rem', fontWeight: 800, color: '#FFFFFF', textTransform: 'uppercase', letterSpacing: '0.03em' }}>
              Component Stack Trade-off Matrix
            </h3>
          </div>

          <div className="grid-3col" style={{ gap: '1.5rem' }}>
            {comparison.componentDiffs.map((diff, idx) => (
              <div key={idx} style={{ backgroundColor: 'var(--card-bg)', padding: '1.5rem', borderRadius: '16px', border: '1px solid var(--border-hover)', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <span style={{ fontSize: '0.8rem', color: 'var(--accent-gold)', fontWeight: 700, textTransform: 'uppercase' }}>
                  {diff.category}
                </span>
                
                <div style={{ backgroundColor: 'rgba(212,175,99,0.08)', padding: '0.8rem 1rem', borderRadius: '10px', border: '1px solid var(--border-accent)' }}>
                  <span style={{ fontSize: '0.72rem', color: 'var(--accent-gold)', fontWeight: 700 }}>CANDIDATE A</span>
                  <div style={{ fontWeight: 700, color: '#FFFFFF', marginTop: '0.15rem' }}>{diff.compA}</div>
                </div>

                <div style={{ backgroundColor: 'rgba(59,130,246,0.08)', padding: '0.8rem 1rem', borderRadius: '10px', border: '1px solid rgba(59,130,246,0.3)' }}>
                  <span style={{ fontSize: '0.72rem', color: 'var(--status-blue)', fontWeight: 700 }}>CANDIDATE B</span>
                  <div style={{ fontWeight: 700, color: '#FFFFFF', marginTop: '0.15rem' }}>{diff.compB}</div>
                </div>

                <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.5, marginTop: 'auto' }}>
                  {diff.tradeoffSummary}
                </p>
              </div>
            ))}
          </div>
        </Card>
      </section>
    </motion.div>
  );
};
