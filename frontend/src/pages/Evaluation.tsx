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
            <Badge variant="gold">● RAG EVALUATION SUITE</Badge>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Automated Factual Entailment Testing</span>
          </div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 800 }}>
            Pipeline Evaluation Suite
          </h1>
          <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', maxWidth: '750px', marginTop: '0.4rem' }}>
            Verify retrieval faithfulness, answer relevancy, context precision, and hallucination percentages before deploying your engineering architecture into production.
          </p>
        </div>
      </header>

      {/* Inputs Section */}
      <Card style={{ padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        <h3 style={{ fontSize: '1rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Search size={18} /> Evaluation Input
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
            <LoadingIndicator label="Ingesting test queries and scoring cross-encoder faithfulness ratings..." size={32} />
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
        let displayRecs: { text: string; priority: string; color: string }[] = [];
        let displayStrengths: string[] = [];
        let displayWeaknesses: string[] = [];
        
        const fScore = result.generation?.faithfulness ?? 1.0;
        const rScore = result.generation?.answer_relevancy ?? 1.0;
        const hRate = Math.max(0, 1 - fScore);
        const overall = (result.overall_score ?? (result.summary?.overall_score ?? 1.0)) * 100; 

        const isNeedsImprovement = fScore < 0.85 || rScore < 0.85 || hRate > 0.15;
        const isExcellent = fScore >= 0.95 && rScore >= 0.95 && hRate <= 0.05;
        const isGood = !isNeedsImprovement && !isExcellent;

        // Strengths
        if (fScore >= 0.95) displayStrengths.push("Excellent factual grounding.");
        else if (fScore >= 0.85) displayStrengths.push("Good factual consistency.");
        
        if (rScore >= 0.95) displayStrengths.push("Highly relevant response.");
        else if (rScore >= 0.85) displayStrengths.push("Response addresses the user's intent effectively.");

        // Weaknesses / Minor issues
        if (isNeedsImprovement) {
            if (fScore < 0.85) displayWeaknesses.push("Generated answer contains unsupported claims.");
            if (rScore < 0.85) displayWeaknesses.push("Generated answer only partially addresses the user question.");
        } else if (isGood) {
            if (fScore < 0.95) displayWeaknesses.push("Factual completeness could be improved.");
            if (rScore < 0.95) displayWeaknesses.push("Response could be more complete.");
        }

        // Recommendations pool
        if (fScore < 0.85) {
            displayRecs.push({ text: "Improve factual grounding and reduce unsupported claims.", priority: "High", color: "#f97316" });
        } else if (fScore < 0.95) {
            displayRecs.push({ text: "Provide a more complete response.", priority: "Minor", color: "#3b82f6" });
        }

        if (rScore < 0.85) {
            displayRecs.push({ text: "Address the user's question more directly.", priority: "High", color: "#f97316" });
            displayRecs.push({ text: "Refine the prompt to encourage more complete responses.", priority: "Normal", color: "#eab308" });
            displayRecs.push({ text: "Expand the response with additional relevant information.", priority: "Normal", color: "#eab308" });
        } else if (rScore < 0.95) {
            displayRecs.push({ text: "Expand the response with additional relevant information from the retrieved context.", priority: "Minor", color: "#3b82f6" });
            displayRecs.push({ text: "Provide a more complete response.", priority: "Minor", color: "#3b82f6" });
        }

        if (hRate > 0.15) {
            displayRecs.push({ text: "Enforce stricter context grounding to reduce hallucinations.", priority: "High", color: "#ef4444" });
        }

        // Deduplicate based on text
        displayRecs = displayRecs.filter((v, i, a) => a.findIndex(t => (t.text === v.text)) === i);

        // If excellent evaluations
        if (isExcellent) {
            displayRecs = [];
        }

        return (
        <motion.div
          initial={{ opacity: 0, scale: 0.98 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.4 }}
          style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}
        >
          {/* Executive Health Banner */}
          <Card style={{ padding: '1.25rem', backgroundColor: 'rgba(16, 185, 129, 0.05)', border: '1px solid rgba(16, 185, 129, 0.3)' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                <div style={{ width: '42px', height: '42px', borderRadius: '10px', backgroundColor: 'var(--status-green)', color: '#0B0D12', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Check size={24} strokeWidth={3} />
                </div>
                <div>
                  <h3 style={{ fontSize: '1.1rem', fontWeight: 800, color: '#FFFFFF' }}>
                    Evaluation Status: {result.status?.toLowerCase() === 'pass' ? 'Passed' : result.status?.toLowerCase() === 'fail' ? 'Failed' : result.status}
                  </h3>
                  <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', display: 'flex', flexDirection: 'column', gap: '0.2rem', marginTop: '0.3rem' }}>
                    <div>Grade: {result.quality_grade || 'A'}</div>
                    <div>Overall Score: {Math.round(overall)}</div>
                    <div>Deployment Readiness: {result.deployment_readiness || 'Production Ready'}</div>
                  </div>
                </div>
              </div>
              <Badge variant="green" style={{ fontSize: '0.85rem', padding: '0.4rem 1rem', fontWeight: 700 }}>
                Evaluation Completed
              </Badge>
            </div>
          </Card>

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
              <MetricRow 
                name="Hallucination Rate" 
                score={formatPercent(1 - (result.generation?.faithfulness || 1))} 
                description="Unsupported claims in reasoning (derived)." 
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
                score={String(result.provider || 'ragas')} 
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
          <Card style={{ padding: '1.25rem' }}>
            {displayRecs.length > 0 ? (
              <>
                <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#FFFFFF', marginBottom: '1rem' }}>
                  {isGood ? 'Minor Improvements' : 'Recommendations'}
                </h3>
                {isGood && <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>The evaluated response is accurate overall with minor opportunities for improvement.</p>}
                <div style={{ overflowX: 'auto' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem', textAlign: 'left' }}>
                    <thead>
                      <tr style={{ borderBottom: '1px solid var(--border-subtle)', color: 'var(--text-muted)' }}>
                        <th style={{ padding: '0.75rem', fontWeight: 600 }}>Priority</th>
                        <th style={{ padding: '0.75rem', fontWeight: 600 }}>Issue</th>
                        <th style={{ padding: '0.75rem', fontWeight: 600 }}>Impact</th>
                        <th style={{ padding: '0.75rem', fontWeight: 600 }}>Recommended Fix</th>
                      </tr>
                    </thead>
                    <tbody>
                      {displayRecs.map((rec, i) => (
                        <tr key={i} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                          <td style={{ padding: '0.75rem', color: 'var(--text-primary)', fontWeight: 600 }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                              <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: rec.color }} /> 
                              {rec.priority}
                            </div>
                          </td>
                          <td style={{ padding: '0.75rem', color: 'var(--text-primary)' }}>Optimization Opportunity</td>
                          <td style={{ padding: '0.75rem', color: 'var(--text-secondary)' }}>Response Quality</td>
                          <td style={{ padding: '0.75rem', color: 'var(--text-primary)' }}>{rec.text}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </>
            ) : (
              <div style={{ padding: '1.5rem', textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.75rem' }}>
                <div style={{ width: '48px', height: '48px', borderRadius: '50%', backgroundColor: 'rgba(16, 185, 129, 0.1)', color: 'var(--status-green)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <CheckCircle2 size={28} />
                </div>
                <h4 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#FFFFFF', margin: 0 }}>
                  No recommendations available.
                </h4>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', margin: 0, maxWidth: '400px' }}>
                  {isExcellent ? 'The evaluated response demonstrates excellent overall quality and requires no further optimization.' : 'The evaluated response is accurate overall with minor opportunities for improvement.'}
                </p>
              </div>
            )}
          </Card>

          {/* Deployment Assessment */}
          <Card style={{ padding: '1.5rem', backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--border-hover)' }}>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 800, color: '#FFFFFF', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Target size={20} color="var(--accent-gold)" /> Evaluation Framework Status
            </h3>
            <div className="grid-2col" style={{ gap: '1.5rem' }}>
              <div>
                <h4 style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--status-green)', marginBottom: '0.5rem', textTransform: 'uppercase' }}>Strengths</h4>
                <ul style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', paddingLeft: '1.25rem', display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                  {displayStrengths.map((s, i) => (
                    <li key={i}>{s}</li>
                  ))}
                  {displayStrengths.length === 0 && (
                    <li>No major strengths identified.</li>
                  )}
                </ul>
              </div>
              <div>
                {isNeedsImprovement ? (
                  <>
                    <h4 style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--status-orange)', marginBottom: '0.5rem', textTransform: 'uppercase' }}>Areas for Optimization</h4>
                    <ul style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', paddingLeft: '1.25rem', display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                      {displayWeaknesses.map((w, i) => (
                        <li key={i}>{w}</li>
                      ))}
                    </ul>
                  </>
                ) : (
                  <>
                    <h4 style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--status-green)', marginBottom: '0.5rem', textTransform: 'uppercase' }}>Evaluation Summary</h4>
                    {isExcellent ? (
                      <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <Check size={16} color="var(--status-green)" /> No significant weaknesses detected.
                      </div>
                    ) : (
                      <ul style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', paddingLeft: '1.25rem', display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                        {displayWeaknesses.map((w, i) => (
                          <li key={i}>{w}</li>
                        ))}
                      </ul>
                    )}
                  </>
                )}
              </div>
            </div>
          </Card>
        </motion.div>
      )})()}
    </motion.div>
  );
};
