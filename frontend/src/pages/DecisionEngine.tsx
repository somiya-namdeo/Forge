import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Brain, Sliders, CheckCircle2, ChevronDown, ChevronRight,
  Award, Sparkles, Target, FileJson, FileText, XCircle,
} from 'lucide-react';
import { Card, Badge, Button, ScoreRing, LoadingIndicator, EmptyState } from '../components/common';
import { DecisionRequest, DecisionResponse, DecisionPriority, DeploymentTarget } from '../types';
import { decisionService } from '../services';

export const DecisionEngine: React.FC = () => {
  const [priority, setPriority] = useState<DecisionPriority>('balanced');
  const [deploymentTarget, setDeploymentTarget] = useState<DeploymentTarget>('aws');
  const [budgetUsd, setBudgetUsd] = useState<number>(500);
  const [documentCount, setDocumentCount] = useState<number>(5000000);
  const [preferredLlm] = useState<string>('Llama 3.3 70B Instruct');
  const [executing, setExecuting] = useState<boolean>(false);
  const [response, setResponse] = useState<DecisionResponse | null>(null);
  const [expandedAlts, setExpandedAlts] = useState<Record<number, boolean>>({});

  const handleRunDecisionEngine = async () => {
    setExecuting(true);
    setResponse(null);
    setExpandedAlts({});
    const result = await decisionService.runDecisionEngine({
      projectName: 'Forge UI Configured Architecture',
      projectDescription: `${priority} optimized pipeline targeting ${deploymentTarget} infrastructure`,
      priority,
      deploymentTarget,
      budgetUsd,
      documentCount,
      preferredLlm,
    } as DecisionRequest);
    setResponse(result);
    setExecuting(false);
  };

  const toggleAlt = (idx: number) =>
    setExpandedAlts(prev => ({ ...prev, [idx]: !prev[idx] }));

  const llmRec = response?.recommendations.find(r =>
    r.category.toLowerCase().includes('llm')
  );

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.3 }}
      style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}
    >
      {/* ── Header ─────────────────────────────────────────────── */}
      <header style={{ borderBottom: '1px solid var(--border-subtle)', paddingBottom: '0.875rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
          <Badge variant="gold">● REASONING MATRIX</Badge>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Multi-Constraint Optimization</span>
        </div>
        <h1 style={{ fontSize: '1.5rem', fontWeight: 800 }}>AI Engineering Decision Engine</h1>
        <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', maxWidth: '680px', marginTop: '0.2rem', lineHeight: 1.55 }}>
          Configure operational constraints. Forge evaluates candidates against real benchmark
          telemetry to explain component selection and alternative rejection.
        </p>
      </header>

      {/* ── Constraint Controls ────────────────────────────────── */}
      <Card style={{
        padding: '1.1rem 1.25rem',
        background: 'linear-gradient(135deg, rgba(19,23,32,1) 0%, rgba(26,32,46,0.8) 100%)',
        border: '1px solid var(--border-hover)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '0.75rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <div style={{ width: '28px', height: '28px', borderRadius: '7px', backgroundColor: 'var(--accent-gold-dim)', color: 'var(--accent-gold)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Sliders size={14} />
            </div>
            <div>
              <div style={{ fontSize: '0.875rem', fontWeight: 700, color: '#FFFFFF' }}>Engineering Constraint Controls</div>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)' }}>Set architectural boundaries for deterministic tradeoff scoring</div>
            </div>
          </div>
          <Button variant="primary" icon={Brain} onClick={handleRunDecisionEngine} disabled={executing}>
            {executing ? 'Evaluating...' : 'Run Decision Engine'}
          </Button>
        </div>

        <div className="grid-3col" style={{ gap: '1.25rem' }}>
          {/* Optimization Priority */}
          <div>
            <div style={{ fontSize: '0.68rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '0.5rem' }}>
              Optimization Priority
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.35rem' }}>
              {(['cost', 'quality', 'latency', 'balanced'] as DecisionPriority[]).map(p => (
                <button
                  key={p}
                  type="button"
                  onClick={() => setPriority(p)}
                  style={{
                    padding: '0.45rem 0.5rem',
                    borderRadius: '7px',
                    fontSize: '0.78rem',
                    fontWeight: priority === p ? 700 : 500,
                    textTransform: 'capitalize',
                    backgroundColor: priority === p ? 'rgba(212, 175, 99, 0.2)' : 'var(--bg-secondary)',
                    color: priority === p ? 'var(--accent-gold)' : 'var(--text-secondary)',
                    border: priority === p ? '1px solid var(--border-accent)' : '1px solid var(--border-subtle)',
                    transition: 'all 0.15s',
                    cursor: 'pointer',
                  }}
                >
                  {p}
                </button>
              ))}
            </div>
          </div>

          {/* Target Infrastructure */}
          <div>
            <div style={{ fontSize: '0.68rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '0.5rem' }}>
              Target Infrastructure
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.3rem' }}>
              {(['aws', 'gcp', 'azure', 'on-prem', 'local'] as DeploymentTarget[]).map(t => (
                <button
                  key={t}
                  type="button"
                  onClick={() => setDeploymentTarget(t)}
                  style={{
                    padding: '0.4rem 0.2rem',
                    borderRadius: '6px',
                    fontSize: '0.7rem',
                    fontWeight: deploymentTarget === t ? 700 : 500,
                    textTransform: 'uppercase',
                    backgroundColor: deploymentTarget === t ? 'rgba(59, 130, 246, 0.2)' : 'var(--bg-secondary)',
                    color: deploymentTarget === t ? 'var(--status-blue)' : 'var(--text-secondary)',
                    border: deploymentTarget === t ? '1px solid var(--status-blue)' : '1px solid var(--border-subtle)',
                    transition: 'all 0.15s',
                    cursor: 'pointer',
                  }}
                >
                  {t}
                </button>
              ))}
            </div>
          </div>

          {/* Budget + Scale Sliders */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.3rem', fontSize: '0.72rem', fontWeight: 600 }}>
                <span style={{ textTransform: 'uppercase', color: 'var(--text-muted)', letterSpacing: '0.04em' }}>Monthly Budget</span>
                <span style={{ color: 'var(--accent-gold)', fontWeight: 700 }}>${budgetUsd}/mo</span>
              </div>
              <input type="range" min={100} max={3000} step={50} value={budgetUsd}
                onChange={e => setBudgetUsd(Number(e.target.value))}
                style={{ width: '100%', accentColor: 'var(--accent-gold)' }} />
            </div>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.3rem', fontSize: '0.72rem', fontWeight: 600 }}>
                <span style={{ textTransform: 'uppercase', color: 'var(--text-muted)', letterSpacing: '0.04em' }}>Document Scale</span>
                <span style={{ color: 'var(--status-green)', fontWeight: 700 }}>{(documentCount / 1000000).toFixed(1)}M Docs</span>
              </div>
              <input type="range" min={500000} max={20000000} step={500000} value={documentCount}
                onChange={e => setDocumentCount(Number(e.target.value))}
                style={{ width: '100%', accentColor: 'var(--status-green)' }} />
            </div>
          </div>
        </div>
      </Card>

      {/* ── Loading ────────────────────────────────────────────── */}
      {executing && (
        <Card style={{ padding: '3rem 2rem', border: '1px dashed var(--border-accent)' }}>
          <LoadingIndicator
            label={`Evaluating 84 candidate permutations against ${priority.toUpperCase()} on ${deploymentTarget.toUpperCase()}...`}
            size={40}
          />
        </Card>
      )}

      {/* ── Empty ─────────────────────────────────────────────── */}
      {!executing && !response && (
        <EmptyState
          icon={Brain}
          title="Ready for Decision Reasoning"
          description="Configure your constraints above and click 'Run Decision Engine' to initiate the architectural deduction trace."
          actionText="Run Decision Engine Now"
          onAction={handleRunDecisionEngine}
        />
      )}

      {/* ── Results: 2-column layout ───────────────────────────── */}
      {!executing && response && (
        <motion.div
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
          style={{ display: 'grid', gridTemplateColumns: '1fr 288px', gap: '1.25rem', alignItems: 'flex-start' }}
        >
          {/* ─── LEFT: Recommendation Cards ─── */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.9rem' }}>

            {/* Executive Summary Bar */}
            <Card style={{ padding: '0.875rem 1.1rem', border: '1px solid var(--border-accent)', backgroundColor: 'rgba(212, 175, 99, 0.03)' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.75rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <ScoreRing score={response.overallConfidence * 100} size={42} strokeWidth={3.5} />
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', marginBottom: '0.15rem' }}>
                      <Badge variant="green">✔ DEDUCTION COMPLETE</Badge>
                      <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                        {response.pipelineStatistics.evaluatedCandidates} candidates · {response.pipelineStatistics.durationMs}ms
                      </span>
                    </div>
                    <div style={{ fontSize: '0.9rem', fontWeight: 700, color: '#FFFFFF' }}>{response.summary}</div>
                  </div>
                </div>
                <div style={{ display: 'flex', gap: '0.35rem' }}>
                  <button style={{ padding: '0.3rem 0.6rem', borderRadius: '6px', backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--border-subtle)', color: 'var(--text-secondary)', fontSize: '0.7rem', fontWeight: 600, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                    <FileJson size={11} /> JSON
                  </button>
                  <button style={{ padding: '0.3rem 0.6rem', borderRadius: '6px', backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--border-subtle)', color: 'var(--text-secondary)', fontSize: '0.7rem', fontWeight: 600, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                    <FileText size={11} /> Markdown
                  </button>
                </div>
              </div>
            </Card>

            {/* Section label */}
            <div style={{ fontSize: '0.68rem', fontWeight: 700, letterSpacing: '0.07em', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
              Component Recommendations · {response.recommendations.length} selected
            </div>

            {/* Per-Component Recommendation Cards */}
            {response.recommendations.map((rec, index) => (
              <Card key={index} style={{ padding: '0.95rem 1.1rem', display: 'flex', flexDirection: 'column', gap: '0.65rem' }}>

                {/* Header row */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', paddingBottom: '0.6rem', borderBottom: '1px solid var(--border-subtle)' }}>
                  <div>
                    <div style={{ fontSize: '0.62rem', color: 'var(--accent-gold)', fontWeight: 700, letterSpacing: '0.07em', textTransform: 'uppercase', marginBottom: '0.18rem' }}>
                      {rec.category} · WINNER
                    </div>
                    <div style={{ fontSize: '0.95rem', fontWeight: 800, color: '#FFFFFF', display: 'flex', alignItems: 'center', gap: '0.45rem', flexWrap: 'wrap' }}>
                      <CheckCircle2 size={14} style={{ color: 'var(--status-green)', flexShrink: 0 }} />
                      {rec.recommended}
                      <span style={{
                        fontSize: '0.67rem', fontWeight: 700,
                        color: rec.confidence >= 90 ? 'var(--status-green)' : rec.confidence >= 80 ? 'var(--accent-gold)' : '#f97316',
                        backgroundColor: rec.confidence >= 90 ? 'rgba(16,185,129,0.1)' : rec.confidence >= 80 ? 'rgba(212,175,99,0.1)' : 'rgba(249,115,22,0.1)',
                        padding: '0.1rem 0.4rem', borderRadius: '4px',
                        border: `1px solid ${rec.confidence >= 90 ? 'rgba(16,185,129,0.25)' : rec.confidence >= 80 ? 'rgba(212,175,99,0.25)' : 'rgba(249,115,22,0.25)'}`,
                      }}>
                        {rec.confidence}% · {rec.confidenceLevel}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Engineering Stats Chips */}
                <div style={{ display: 'flex', gap: '0.35rem', flexWrap: 'wrap' }}>
                  {[
                    { label: 'P95', value: `${rec.latencyVsAccuracy.latencyMs}ms`, color: 'var(--status-green)' },
                    { label: 'Accuracy', value: `${rec.latencyVsAccuracy.accuracyPct}%`, color: 'var(--accent-gold)' },
                    { label: 'Benchmark', value: rec.benchmarkEvidence.score, color: 'var(--status-purple)' },
                    { label: 'Cost Idx', value: `${rec.costVsPerformance.costIndex}`, color: 'var(--status-blue)' },
                  ].map(stat => (
                    <div key={stat.label} style={{ display: 'flex', alignItems: 'center', gap: '0.2rem', backgroundColor: 'var(--bg-secondary)', padding: '0.2rem 0.5rem', borderRadius: '5px', border: '1px solid var(--border-subtle)' }}>
                      <span style={{ fontSize: '0.6rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>{stat.label}</span>
                      <span style={{ fontSize: '0.75rem', fontWeight: 700, color: stat.color }}>{stat.value}</span>
                    </div>
                  ))}
                </div>

                {/* Why Selected */}
                <div style={{ backgroundColor: 'rgba(16, 185, 129, 0.04)', border: '1px solid rgba(16, 185, 129, 0.18)', borderRadius: '8px', padding: '0.65rem 0.8rem' }}>
                  <div style={{ fontSize: '0.62rem', color: 'var(--status-green)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.3rem', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                    <Award size={10} /> Why Selected
                  </div>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-primary)', lineHeight: 1.5, margin: 0 }}>
                    {rec.reason}
                  </p>
                  {rec.decisionTrace.length > 0 && (
                    <div style={{ marginTop: '0.45rem', display: 'flex', flexDirection: 'column', gap: '0.1rem' }}>
                      {rec.decisionTrace.slice(0, 2).map((trace, ti) => (
                        <div key={ti} style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', display: 'flex', alignItems: 'flex-start', gap: '0.25rem' }}>
                          <ChevronRight size={10} style={{ color: 'var(--status-green)', flexShrink: 0, marginTop: '0.1rem' }} />
                          {trace}
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Collapsible: Why Not Alternatives */}
                {rec.alternativeAnalysis.length > 0 && (
                  <div>
                    <button
                      onClick={() => toggleAlt(index)}
                      style={{ display: 'flex', alignItems: 'center', gap: '0.3rem', fontSize: '0.67rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', background: 'none', border: 'none', cursor: 'pointer', padding: 0, transition: 'color 0.15s' }}
                    >
                      {expandedAlts[index] ? <ChevronDown size={11} /> : <ChevronRight size={11} />}
                      <XCircle size={10} style={{ color: '#ef4444' }} />
                      Why Not · {rec.alternativeAnalysis.length} alternatives rejected
                    </button>
                    <AnimatePresence>
                      {expandedAlts[index] && (
                        <motion.div
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: 'auto' }}
                          exit={{ opacity: 0, height: 0 }}
                          transition={{ duration: 0.2 }}
                          style={{ overflow: 'hidden', marginTop: '0.5rem' }}
                        >
                          <div style={{ backgroundColor: 'rgba(239, 68, 68, 0.03)', border: '1px solid rgba(239, 68, 68, 0.15)', borderRadius: '8px', padding: '0.7rem 0.8rem', display: 'flex', flexDirection: 'column' }}>
                            {rec.alternativeAnalysis.map((alt, ai) => (
                              <div
                                key={ai}
                                style={{
                                  display: 'flex',
                                  justifyContent: 'space-between',
                                  alignItems: 'flex-start',
                                  gap: '0.75rem',
                                  paddingBottom: ai < rec.alternativeAnalysis.length - 1 ? '0.5rem' : 0,
                                  marginBottom: ai < rec.alternativeAnalysis.length - 1 ? '0.5rem' : 0,
                                  borderBottom: ai < rec.alternativeAnalysis.length - 1 ? '1px solid rgba(239,68,68,0.08)' : 'none',
                                }}
                              >
                                <div style={{ flex: 1 }}>
                                  <div style={{ fontSize: '0.78rem', fontWeight: 700, color: '#FFFFFF', marginBottom: '0.12rem' }}>{alt.name}</div>
                                  <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', lineHeight: 1.4 }}>{alt.reason}</div>
                                </div>
                                <span style={{ fontSize: '0.65rem', color: '#f87171', fontWeight: 700, backgroundColor: 'rgba(239,68,68,0.12)', padding: '0.12rem 0.4rem', borderRadius: '4px', flexShrink: 0, whiteSpace: 'nowrap' }}>
                                  {alt.scorePenalty}
                                </span>
                              </div>
                            ))}
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>
                )}
              </Card>
            ))}
          </div>

          {/* ─── RIGHT: Decision Summary Sidebar ─── */}
          <div style={{ position: 'sticky', top: '80px', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>

            {/* Overall Decision Summary */}
            <Card style={{
              padding: '1rem 1.1rem',
              background: 'linear-gradient(135deg, rgba(19,23,32,1) 0%, rgba(26,32,46,0.9) 100%)',
              border: '1px solid var(--border-hover)',
            }}>
              <div style={{ fontSize: '0.62rem', fontWeight: 700, letterSpacing: '0.07em', color: 'var(--accent-gold)', textTransform: 'uppercase', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                <Sparkles size={10} /> Decision Summary
              </div>

              {/* Confidence */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem' }}>
                <ScoreRing score={response.overallConfidence * 100} size={48} strokeWidth={4} />
                <div>
                  <div style={{ fontSize: '0.6rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Overall Confidence</div>
                  <div style={{ fontSize: '1.2rem', fontWeight: 800, color: '#FFFFFF' }}>{Math.round(response.overallConfidence * 100)}%</div>
                  <div style={{ fontSize: '0.67rem', color: 'var(--status-green)', fontWeight: 600 }}>Architecture Verified ✓</div>
                </div>
              </div>

              {/* Selected LLM highlight */}
              {llmRec && (
                <div style={{ padding: '0.5rem 0.65rem', backgroundColor: 'rgba(212, 175, 99, 0.06)', borderRadius: '7px', border: '1px solid rgba(212, 175, 99, 0.15)', marginBottom: '0.65rem' }}>
                  <div style={{ fontSize: '0.58rem', color: 'var(--accent-gold)', textTransform: 'uppercase', fontWeight: 700, letterSpacing: '0.05em' }}>Selected LLM</div>
                  <div style={{ fontSize: '0.78rem', fontWeight: 700, color: '#FFFFFF', marginTop: '0.1rem' }}>{llmRec.recommended}</div>
                </div>
              )}

              {/* Key Metrics 2×2 */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.35rem' }}>
                {[
                  { label: 'Budget', value: `$${budgetUsd}/mo`, color: 'var(--status-blue)' },
                  { label: 'Scale', value: `${(documentCount / 1000000).toFixed(1)}M docs`, color: 'var(--status-green)' },
                  { label: 'Infra', value: deploymentTarget.toUpperCase(), color: 'var(--accent-gold)' },
                  { label: 'Mode', value: priority, color: 'var(--text-primary)' },
                ].map(m => (
                  <div key={m.label} style={{ backgroundColor: 'var(--bg-secondary)', padding: '0.4rem 0.5rem', borderRadius: '6px', border: '1px solid var(--border-subtle)' }}>
                    <div style={{ fontSize: '0.58rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>{m.label}</div>
                    <div style={{ fontSize: '0.72rem', fontWeight: 700, color: m.color, marginTop: '0.08rem', textTransform: 'capitalize' }}>{m.value}</div>
                  </div>
                ))}
              </div>
            </Card>

            {/* Component Confidence Chips */}
            <Card style={{ padding: '0.85rem 1rem' }}>
              <div style={{ fontSize: '0.62rem', fontWeight: 700, letterSpacing: '0.07em', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '0.55rem' }}>
                Component Confidence
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.38rem' }}>
                {response.recommendations.map((rec, i) => (
                  <div key={i} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', flex: 1, minWidth: 0 }}>
                      <div style={{
                        width: '5px', height: '5px', borderRadius: '50%', flexShrink: 0,
                        backgroundColor: rec.confidence >= 90 ? 'var(--status-green)' : rec.confidence >= 80 ? 'var(--accent-gold)' : '#f97316',
                      }} />
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-primary)', fontWeight: 600, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {rec.recommended.split(' ').slice(0, 2).join(' ')}
                      </span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.3rem', flexShrink: 0 }}>
                      <span style={{ fontSize: '0.62rem', color: 'var(--text-muted)' }}>{rec.category}</span>
                      <span style={{ fontSize: '0.72rem', fontWeight: 800, color: rec.confidence >= 90 ? 'var(--status-green)' : rec.confidence >= 80 ? 'var(--accent-gold)' : '#f97316' }}>
                        {rec.confidence}%
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </Card>

            {/* Engineering Recommendation */}
            <Card style={{ padding: '0.85rem 1rem', backgroundColor: 'rgba(212, 175, 99, 0.03)', border: '1px solid rgba(212, 175, 99, 0.12)' }}>
              <div style={{ fontSize: '0.62rem', fontWeight: 700, letterSpacing: '0.07em', color: 'var(--accent-gold)', textTransform: 'uppercase', marginBottom: '0.45rem', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                <Target size={10} /> Engineering Recommendation
              </div>
              <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', lineHeight: 1.55, margin: 0 }}>
                {response.summary}
              </p>
              <div style={{ marginTop: '0.6rem', paddingTop: '0.6rem', borderTop: '1px solid rgba(212, 175, 99, 0.1)' }}>
                <div style={{ fontSize: '0.6rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.04em', marginBottom: '0.3rem' }}>
                  Suggested Next Steps
                </div>
                {['Review benchmark evidence', 'Validate on pilot dataset', 'Deploy to staging'].map((step, i) => (
                  <div key={i} style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', display: 'flex', alignItems: 'flex-start', gap: '0.25rem', marginTop: '0.2rem' }}>
                    <ChevronRight size={10} style={{ color: 'var(--accent-gold)', flexShrink: 0, marginTop: '0.12rem' }} />
                    {step}
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
