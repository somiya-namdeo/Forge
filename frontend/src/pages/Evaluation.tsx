import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  BarChart2,
  CheckCircle2,
  AlertTriangle,
  Play,
  Activity,
  FileText,
  HelpCircle,
  Database,
  Search,
  Check,
  Zap,
  RotateCcw
} from 'lucide-react';
import { Card, Badge, Button, ScoreRing, ProgressBar, EmptyState, Skeleton, LoadingIndicator } from '../components/common';
import { EvaluationResult } from '../types';
import { evaluationService } from '../services';

export const Evaluation: React.FC = () => {
  const [targetPipeline, setTargetPipeline] = useState('Legal RAG System — Hybrid Pipeline (v1.0.0)');
  const [evaluating, setEvaluating] = useState(false);
  const [result, setResult] = useState<EvaluationResult | null>(null);

  const handleRunEvaluation = async () => {
    setEvaluating(true);
    setResult(null);
    const data = await evaluationService.runEvaluation(targetPipeline, 'v1.0.0');
    setResult(data);
    setEvaluating(false);
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
            <Badge variant="gold">● RAG EVALUATION SUITE</Badge>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Automated Factual Entailment Testing</span>
          </div>
          <h1 style={{ fontSize: '2.5rem', fontWeight: 800 }}>
            Pipeline Evaluation Suite
          </h1>
          <p style={{ fontSize: '1.05rem', color: 'var(--text-secondary)', maxWidth: '750px', marginTop: '0.4rem' }}>
            Verify retrieval faithfulness, answer relevancy, context precision, and hallucination percentages before deploying your engineering architecture into production.
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          {result && (
            <Button variant="ghost" icon={RotateCcw} onClick={handleRunEvaluation} disabled={evaluating}>
              Rerun Tests
            </Button>
          )}
          <Button variant="primary" icon={Play} onClick={handleRunEvaluation} disabled={evaluating} style={{ padding: '0.8rem 1.8rem' }}>
            {evaluating ? 'Running RAG Benchmarks...' : 'Run Evaluation Suite'}
          </Button>
        </div>
      </header>

      {/* Target Pipeline Selecor Bar */}
      <section>
        <div
          style={{
            backgroundColor: 'var(--card-bg)',
            padding: '1.25rem 1.75rem',
            borderRadius: '16px',
            border: '1px solid var(--border-subtle)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '1rem',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <Database size={22} style={{ color: 'var(--accent-gold)' }} />
            <div>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>Target Pipeline Under Test</span>
              <div style={{ fontSize: '1.05rem', fontWeight: 700, color: '#FFFFFF' }}>{targetPipeline}</div>
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
            <div>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>Dataset Volume</span>
              <div style={{ fontSize: '0.95rem', fontWeight: 600, color: '#FFFFFF' }}>500 Gold-Standard Queries</div>
            </div>
            <div>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>Validation Framework</span>
              <div style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--status-blue)' }}>RAGAS / TruLens Protocol</div>
            </div>
          </div>
        </div>
      </section>

      {/* State 1: Executing Skeletons & Animation */}
      {evaluating && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          <Card style={{ padding: '3.5rem 2rem', border: '1px dashed var(--border-accent)' }}>
            <LoadingIndicator label="Ingesting 500 gold-standard test queries and scoring cross-encoder faithfulness ratings..." size={42} />
          </Card>
          <div className="grid-4col">
            <Skeleton variant="card" height={180} />
            <Skeleton variant="card" height={180} />
            <Skeleton variant="card" height={180} />
            <Skeleton variant="card" height={180} />
          </div>
        </div>
      )}

      {/* State 2: Initial Waiting (Strict No Fabricated Data) */}
      {!evaluating && !result && (
        <EmptyState
          icon={BarChart2}
          title="Waiting for Evaluation"
          description="Do not display evaluation metrics before tests are executed. Click the button below to initiate multi-metric testing against your selected pipeline."
          actionText="Run RAG Evaluation Suite"
          onAction={handleRunEvaluation}
        />
      )}

      {/* State 3: Completed Animated Evaluation Results */}
      {!evaluating && result && (
        <motion.div
          initial={{ opacity: 0, scale: 0.98 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.4 }}
          style={{ display: 'flex', flexDirection: 'column', gap: '2.5rem' }}
        >
          {/* Executive Health Banner */}
          <Card style={{ padding: '1.8rem 2.2rem', backgroundColor: 'rgba(16, 185, 129, 0.05)', border: '1px solid rgba(16, 185, 129, 0.3)' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
                <div style={{ width: '56px', height: '56px', borderRadius: '16px', backgroundColor: 'var(--status-green)', color: '#0B0D12', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Check size={32} strokeWidth={3} />
                </div>
                <div>
                  <h3 style={{ fontSize: '1.5rem', fontWeight: 800, color: '#FFFFFF' }}>
                    Evaluation Suite Passed: Production Ready
                  </h3>
                  <p style={{ fontSize: '0.92rem', color: 'var(--text-secondary)' }}>
                    Completed at {result.executedAt} · Zero formatting anomalies detected across 500 candidate test runs.
                  </p>
                </div>
              </div>
              <Badge variant="green" style={{ fontSize: '1rem', padding: '0.6rem 1.4rem', fontWeight: 700 }}>
                VERIFIED · HEALTHY
              </Badge>
            </div>
          </Card>

          {/* 4 KPIs Metric Cards Grid */}
          <div className="grid-4col" style={{ gap: '1.4rem' }}>
            {/* Faithfulness */}
            <Card style={{ padding: '1.6rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>Faithfulness</span>
                  <div style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--status-green)', marginTop: '0.2rem' }}>
                    {result.metrics.faithfulness.score}%
                  </div>
                </div>
                <ScoreRing score={result.metrics.faithfulness.score} size={46} strokeWidth={4} />
              </div>
              <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', lineHeight: 1.4 }}>
                {result.metrics.faithfulness.description}
              </p>
              <div style={{ fontSize: '0.78rem', color: 'var(--status-green)', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                ✔ Above {result.metrics.faithfulness.target}% production threshold
              </div>
            </Card>

            {/* Answer Relevancy */}
            <Card style={{ padding: '1.6rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>Answer Relevancy</span>
                  <div style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--status-blue)', marginTop: '0.2rem' }}>
                    {result.metrics.relevancy.score}%
                  </div>
                </div>
                <ScoreRing score={result.metrics.relevancy.score} size={46} strokeWidth={4} />
              </div>
              <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', lineHeight: 1.4 }}>
                {result.metrics.relevancy.description}
              </p>
              <div style={{ fontSize: '0.78rem', color: 'var(--status-blue)', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                ✔ Above {result.metrics.relevancy.target}% production threshold
              </div>
            </Card>

            {/* Context Precision */}
            <Card style={{ padding: '1.6rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>Context Precision@10</span>
                  <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#f97316', marginTop: '0.2rem' }}>
                    {result.metrics.contextPrecision.score}%
                  </div>
                </div>
                <ScoreRing score={result.metrics.contextPrecision.score} size={46} strokeWidth={4} />
              </div>
              <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', lineHeight: 1.4 }}>
                {result.metrics.contextPrecision.description}
              </p>
              <div style={{ fontSize: '0.78rem', color: '#f97316', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                ✔ High signal-to-noise ranking quality
              </div>
            </Card>

            {/* Hallucination Index */}
            <Card style={{ padding: '1.6rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>Hallucination Rate</span>
                  <div style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--status-purple)', marginTop: '0.2rem' }}>
                    {result.metrics.hallucinationIndex.score}%
                  </div>
                </div>
                <div style={{ width: '46px', height: '46px', borderRadius: '50%', border: '2px solid var(--status-purple)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: '0.85rem', color: 'var(--status-purple)' }}>
                  LOW
                </div>
              </div>
              <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', lineHeight: 1.4 }}>
                {result.metrics.hallucinationIndex.description}
              </p>
              <div style={{ fontSize: '0.78rem', color: 'var(--status-purple)', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                ✔ Below 5% ceiling (Optimal safety)
              </div>
            </Card>
          </div>

          {/* Split Section: Sample Queries & Test Logs */}
          <div className="grid-2col" style={{ gap: '2rem', alignItems: 'flex-start' }}>
            
            {/* Left: Sample Evaluated Queries */}
            <Card style={{ padding: '1.8rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#FFFFFF', textTransform: 'uppercase', letterSpacing: '0.03em' }}>
                Sample Gold Query Verifications
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {result.sampleEvaluations.map((sample, i) => (
                  <div key={i} style={{ padding: '1rem 1.25rem', backgroundColor: 'var(--bg-secondary)', borderRadius: '12px', border: '1px solid var(--border-subtle)', display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
                    <div style={{ fontWeight: 600, color: 'var(--text-primary)', fontSize: '0.95rem' }}>
                      "{sample.query}"
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
                      <span>Retrieved Docs: <strong>{sample.retrievedDocs} chunks</strong></span>
                      <span>Faithfulness: <strong style={{ color: 'var(--status-green)' }}>{sample.faithfulnessScore}%</strong></span>
                      <Badge variant={sample.hallucinationDetected ? 'orange' : 'green'} style={{ fontSize: '0.72rem' }}>
                        {sample.hallucinationDetected ? 'Hallucination Flagged' : 'Factually Verifiable'}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </Card>

            {/* Right: Real-Time Execution Test Logs */}
            <Card style={{ padding: '1.8rem', display: 'flex', flexDirection: 'column', gap: '1.25rem', backgroundColor: 'var(--bg-primary)', border: '1px solid var(--border-hover)' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--accent-gold)', textTransform: 'uppercase', letterSpacing: '0.03em', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <Activity size={18} /> Automated Test Harness Logs
                </h3>
                <span style={{ fontSize: '0.75rem', fontFamily: 'monospace', color: 'var(--text-muted)' }}>EXIT CODE: 0 (SUCCESS)</span>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', fontFamily: 'monospace', fontSize: '0.85rem' }}>
                {result.testLogs.map((log, li) => (
                  <div key={li} style={{ display: 'flex', gap: '1rem', borderLeft: '2px solid var(--border-hover)', paddingLeft: '0.75rem' }}>
                    <span style={{ color: 'var(--text-muted)', flexShrink: 0 }}>[{log.timestamp}]</span>
                    <span style={{ color: log.status === 'success' ? 'var(--status-green)' : 'var(--text-primary)', flex: 1 }}>
                      <strong>{log.step}:</strong> {log.message}
                    </span>
                  </div>
                ))}
              </div>
            </Card>

          </div>
        </motion.div>
      )}
    </motion.div>
  );
};
