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
  RotateCcw,
  Target
} from 'lucide-react';
import { Card, Badge, Button, ScoreRing, ProgressBar, EmptyState, Skeleton, LoadingIndicator } from '../components/common';
import { EvaluationResult } from '../types';
import { evaluationService } from '../services';
import { useForgeContext } from '../context';

const formatPercent = (val: number | undefined) => {
  if (val === undefined || val === null) return '0.0';
  return (val * 100).toFixed(1);
};

export const Evaluation: React.FC = () => {
  const { setEvaluationResult } = useForgeContext();
  const [targetPipeline, setTargetPipeline] = useState('Legal RAG System — Hybrid Pipeline (v1.0.0)');
  const [evaluating, setEvaluating] = useState(false);
  const [result, setResult] = useState<EvaluationResult | null>(null);
  const [evalError, setEvalError] = useState<string | null>(null);

  // Input states for the Evaluation Input Card
  const [question, setQuestion] = useState('What are the termination liabilities under Clause 14.2 in corporate mergers?');
  const [retrievedContext, setRetrievedContext] = useState('Clause 14.2 stipulates that in the event of a merger, termination liabilities...');
  const [groundTruth, setGroundTruth] = useState('Termination liabilities under Clause 14.2 include a penalty of 5% of the transaction value...');
  const [generatedAnswer, setGeneratedAnswer] = useState('Under Clause 14.2, the termination liabilities involve a penalty amounting to 5%...');

  const handleRunEvaluation = async () => {
    setEvaluating(true);
    setResult(null);
    setEvalError(null);
    try {
      const data = await evaluationService.runEvaluation(question, retrievedContext, groundTruth, generatedAnswer);
      setResult(data);
      setEvaluationResult(data);
    } catch (err: any) {
      setEvalError(err.message || 'Evaluation failed');
    } finally {
      setEvaluating(false);
    }
  };

  const MetricRow = ({ name, score, description, isOptimal = true, suffix = '%' }: { name: string, score: number | string, description: string, isOptimal?: boolean, suffix?: string }) => (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.75rem 0', borderBottom: '1px solid var(--border-subtle)' }}>
      <div style={{ flex: 1 }}>
        <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)' }}>{name}</div>
        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{description}</div>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        <div style={{ 
          fontSize: '1rem', 
          fontWeight: 700, 
          color: isOptimal ? 'var(--status-green)' : 'var(--status-orange)',
          minWidth: '60px',
          textAlign: 'right'
        }}>
          {score}{suffix}
        </div>
      </div>
    </div>
  );

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.35 }}
      style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}
    >
      {/* Header */}
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '1.5rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
            <Badge variant="gold">● RAG EVALUATION</Badge>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Manual Semantic Evaluation</span>
          </div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 800 }}>
            RAG Evaluation
          </h1>
          <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', maxWidth: '750px', marginTop: '0.4rem' }}>
            Evaluate the supplied question, context, ground truth, and generated answer.
          </p>
        </div>
      </header>

      {/* Inputs Section */}
      <Card style={{ padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        <h3 style={{ fontSize: '1rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Search size={18} /> Evaluation Input (Example: Clause 14.2)
        </h3>
        <div className="grid-2col" style={{ gap: '1rem' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <label style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)' }}>Question</label>
            <textarea 
              style={{ padding: '0.75rem', borderRadius: '8px', border: '1px solid var(--border-hover)', backgroundColor: 'var(--bg-secondary)', color: 'var(--text-primary)', minHeight: '80px', fontSize: '0.85rem', resize: 'vertical' }}
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
            />
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <label style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)' }}>Retrieved Context</label>
            <textarea 
              style={{ padding: '0.75rem', borderRadius: '8px', border: '1px solid var(--border-hover)', backgroundColor: 'var(--bg-secondary)', color: 'var(--text-primary)', minHeight: '80px', fontSize: '0.85rem', resize: 'vertical' }}
              value={retrievedContext}
              onChange={(e) => setRetrievedContext(e.target.value)}
            />
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <label style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)' }}>Ground Truth</label>
            <textarea 
              style={{ padding: '0.75rem', borderRadius: '8px', border: '1px solid var(--border-hover)', backgroundColor: 'var(--bg-secondary)', color: 'var(--text-primary)', minHeight: '80px', fontSize: '0.85rem', resize: 'vertical' }}
              value={groundTruth}
              onChange={(e) => setGroundTruth(e.target.value)}
            />
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <label style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)' }}>Generated Answer</label>
            <textarea 
              style={{ padding: '0.75rem', borderRadius: '8px', border: '1px solid var(--border-hover)', backgroundColor: 'var(--bg-secondary)', color: 'var(--text-primary)', minHeight: '80px', fontSize: '0.85rem', resize: 'vertical' }}
              value={generatedAnswer}
              onChange={(e) => setGeneratedAnswer(e.target.value)}
            />
          </div>
        </div>
        <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '0.5rem' }}>
          <Button variant="primary" icon={Play} onClick={handleRunEvaluation} disabled={evaluating} style={{ padding: '0.6rem 1.5rem', fontSize: '0.85rem' }}>
            {evaluating ? 'Running...' : 'Run Evaluation'}
          </Button>
        </div>
      </Card>

      {/* State 1: Executing Skeletons & Animation */}
      {evaluating && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <Card style={{ padding: '2.5rem 1.5rem', border: '1px dashed var(--border-accent)' }}>
            <LoadingIndicator label="Evaluating the supplied question, context, ground truth, and generated answer..." size={32} />
          </Card>
          <div className="grid-3col">
            <Skeleton variant="card" height={150} />
            <Skeleton variant="card" height={150} />
            <Skeleton variant="card" height={150} />
          </div>
        </div>
      )}

      {/* State 2: Initial Waiting or Backend Error */}
      {!evaluating && !result && (
        <EmptyState
          icon={BarChart2}
          title={evalError ? 'Backend Not Available' : 'Waiting for Evaluation'}
          description={
            evalError
              ? evalError
              : 'Provide inputs above and click Run Evaluation to test the pipeline.'
          }
          actionText={evalError ? undefined : 'Run Evaluation'}
          onAction={evalError ? undefined : handleRunEvaluation}
        />
      )}

      {/* State 3: Completed Animated Evaluation Results */}
      {!evaluating && result && (() => {
        let displayRecs: any[] = [];
        if (result.summary?.recommendations && result.summary.recommendations.length > 0) {
            displayRecs = result.summary.recommendations;
        }

        return (
        <motion.div
          initial={{ opacity: 0, scale: 0.98 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.4 }}
          style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}
        >
          {/* 2 Grouped Metric Sections Grid */}
          <div className="grid-2col" style={{ gap: '1.25rem' }}>
            
            {/* Generation Quality */}
            <Card style={{ padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              <h3 style={{ fontSize: '0.9rem', fontWeight: 700, color: '#FFFFFF', textTransform: 'uppercase', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <FileText size={16} color="var(--status-blue)" /> Generation Quality
              </h3>
              <MetricRow 
                name="Faithfulness" 
                score={formatPercent(result.generation?.faithfulness)} 
                description="Consistency of answers against source." 
              />
              <MetricRow 
                name="Answer Relevancy" 
                score={formatPercent(result.generation?.answer_relevancy)} 
                description="Semantic proximity to user query." 
              />
            </Card>

            {/* Performance & Provider Information */}
            <Card style={{ padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              <h3 style={{ fontSize: '0.9rem', fontWeight: 700, color: '#FFFFFF', textTransform: 'uppercase', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Activity size={16} color="var(--status-purple)" /> Operational Stats
              </h3>
              <MetricRow 
                name="Evaluation Latency" 
                score={Math.round(result.operational?.total_latency_ms || 0)} 
                suffix=" ms"
                description="Total execution end-to-end delay." 
              />
              <MetricRow 
                name="Provider" 
                score={result.provider?.includes('ragas') ? 'RAGAS · Groq' : 'Deterministic Fallback'} 
                suffix=""
                description="Evaluation backend engine used." 
              />
              <MetricRow 
                name="Version" 
                score={String(result.evaluation_version || '2.0')} 
                suffix=""
                description="Evaluation framework version." 
              />
            </Card>
          </div>

          {/* Recommendations Table */}
          {displayRecs.length > 0 && (
          <Card style={{ padding: '1.25rem' }}>
            <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#FFFFFF', marginBottom: '1rem' }}>
              Recommendations
            </h3>
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem', textAlign: 'left' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--border-subtle)', color: 'var(--text-muted)' }}>
                    <th style={{ padding: '0.75rem', fontWeight: 600 }}>Priority</th>
                    <th style={{ padding: '0.75rem', fontWeight: 600 }}>Recommended Fix</th>
                  </tr>
                </thead>
                <tbody>
                  {displayRecs.map((rec, i) => (
                    <tr key={i} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                      <td style={{ padding: '0.75rem', color: 'var(--text-primary)', fontWeight: 600 }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                          <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: rec.color || '#3b82f6' }} /> 
                          {rec.priority || 'Normal'}
                        </div>
                      </td>
                      <td style={{ padding: '0.75rem', color: 'var(--text-primary)' }}>{rec.text || rec}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
          )}
        </motion.div>
      )})()}
    </motion.div>
  );
};
