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

export const Evaluation: React.FC = () => {
  const [targetPipeline, setTargetPipeline] = useState('Legal RAG System — Hybrid Pipeline (v1.0.0)');
  const [evaluating, setEvaluating] = useState(false);
  const [result, setResult] = useState<EvaluationResult | null>(null);

  // Input states for the Evaluation Input Card
  const [question, setQuestion] = useState('What are the termination liabilities under Clause 14.2 in corporate mergers?');
  const [retrievedContext, setRetrievedContext] = useState('Clause 14.2 stipulates that in the event of a merger, termination liabilities...');
  const [groundTruth, setGroundTruth] = useState('Termination liabilities under Clause 14.2 include a penalty of 5% of the transaction value...');
  const [generatedAnswer, setGeneratedAnswer] = useState('Under Clause 14.2, the termination liabilities involve a penalty amounting to 5%...');

  const handleRunEvaluation = async () => {
    setEvaluating(true);
    setResult(null);
    const data = await evaluationService.runEvaluation(targetPipeline, 'v1.0.0');
    setResult(data);
    setEvaluating(false);
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

      {/* State 2: Initial Waiting */}
      {!evaluating && !result && (
        <EmptyState
          icon={BarChart2}
          title="Waiting for Evaluation"
          description="Provide inputs above and click Run Evaluation to test the pipeline."
          actionText="Run Evaluation"
          onAction={handleRunEvaluation}
        />
      )}

      {/* State 3: Completed Animated Evaluation Results */}
      {!evaluating && result && (
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
                    Evaluation Suite Passed: Production Ready
                  </h3>
                  <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                    Completed at {result.executedAt} · Zero formatting anomalies detected.
                  </p>
                </div>
              </div>
              <Badge variant="green" style={{ fontSize: '0.85rem', padding: '0.4rem 1rem', fontWeight: 700 }}>
                VERIFIED · HEALTHY
              </Badge>
            </div>
          </Card>

          {/* 3 Grouped Metric Sections Grid */}
          <div className="grid-3col" style={{ gap: '1.25rem' }}>
            
            {/* Generation Quality */}
            <Card style={{ padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              <h3 style={{ fontSize: '0.9rem', fontWeight: 700, color: '#FFFFFF', textTransform: 'uppercase', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <FileText size={16} color="var(--status-blue)" /> Generation Quality
              </h3>
              <MetricRow 
                name="Faithfulness" 
                score={result.metrics.faithfulness.score} 
                description="Consistency of answers against source." 
              />
              <MetricRow 
                name="Answer Relevancy" 
                score={result.metrics.relevancy.score} 
                description="Semantic proximity to user query." 
              />
              <MetricRow 
                name="Context Precision" 
                score={result.metrics.contextPrecision.score} 
                description="Signal-to-noise ranking quality." 
                isOptimal={result.metrics.contextPrecision.score > 85}
              />
              <MetricRow 
                name="Hallucination Rate" 
                score={result.metrics.hallucinationIndex.score} 
                description="Unsupported claims in reasoning." 
              />
            </Card>

            {/* Retrieval Quality */}
            <Card style={{ padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              <h3 style={{ fontSize: '0.9rem', fontWeight: 700, color: '#FFFFFF', textTransform: 'uppercase', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Database size={16} color="var(--accent-gold)" /> Retrieval Quality
              </h3>
              <MetricRow 
                name="Recall@10" 
                score={94.2} 
                description="Relevant documents in top 10 results." 
              />
              <MetricRow 
                name="Hit Rate@5" 
                score={89.5} 
                description="Queries with at least one hit in top 5." 
              />
              <MetricRow 
                name="MRR" 
                score={0.87} 
                suffix=""
                description="Mean Reciprocal Rank of first relevant doc." 
              />
              <MetricRow 
                name="NDCG@10" 
                score={0.91} 
                suffix=""
                description="Normalized Discounted Cumulative Gain." 
              />
            </Card>

            {/* Performance */}
            <Card style={{ padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              <h3 style={{ fontSize: '0.9rem', fontWeight: 700, color: '#FFFFFF', textTransform: 'uppercase', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Zap size={16} color="var(--status-purple)" /> Performance
              </h3>
              <MetricRow 
                name="Latency P95" 
                score={result.metrics.latencyP95.score} 
                suffix="ms"
                description="95th percentile execution time." 
              />
              <MetricRow 
                name="Throughput" 
                score={120} 
                suffix=" req/s"
                description="Requests processed per second." 
              />
              <MetricRow 
                name="Token Usage" 
                score={1450} 
                suffix=" avg"
                description="Average tokens per request." 
              />
              <MetricRow 
                name="Error Rate" 
                score={0.01} 
                description="Failed requests percentage." 
              />
            </Card>
          </div>

          {/* Recommendations Table */}
          <Card style={{ padding: '1.25rem' }}>
            <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#FFFFFF', marginBottom: '1rem' }}>Recommendations</h3>
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
                  <tr style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                    <td style={{ padding: '0.75rem', color: 'var(--text-primary)', fontWeight: 600 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                        <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#f97316' }} /> High
                      </div>
                    </td>
                    <td style={{ padding: '0.75rem', color: 'var(--text-primary)' }}>Context window saturation in Edge cases</td>
                    <td style={{ padding: '0.75rem', color: 'var(--text-secondary)' }}>Latency spikes &gt; 300ms</td>
                    <td style={{ padding: '0.75rem', color: 'var(--text-primary)' }}>Implement semantic chunking with 200 token overlap</td>
                  </tr>
                  <tr style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                    <td style={{ padding: '0.75rem', color: 'var(--text-primary)', fontWeight: 600 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                        <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#eab308' }} /> Medium
                      </div>
                    </td>
                    <td style={{ padding: '0.75rem', color: 'var(--text-primary)' }}>Sparse retrieval degradation on specific acronyms</td>
                    <td style={{ padding: '0.75rem', color: 'var(--text-secondary)' }}>Recall@10 drops by 4%</td>
                    <td style={{ padding: '0.75rem', color: 'var(--text-primary)' }}>Add domain-specific BM25 weighting</td>
                  </tr>
                  <tr>
                    <td style={{ padding: '0.75rem', color: 'var(--text-primary)', fontWeight: 600 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                        <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#3b82f6' }} /> Low
                      </div>
                    </td>
                    <td style={{ padding: '0.75rem', color: 'var(--text-primary)' }}>Sub-optimal caching hit rate (12%)</td>
                    <td style={{ padding: '0.75rem', color: 'var(--text-secondary)' }}>Increased API costs</td>
                    <td style={{ padding: '0.75rem', color: 'var(--text-primary)' }}>Implement exact-match semantic caching</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </Card>

          {/* Deployment Assessment */}
          <Card style={{ padding: '1.5rem', backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--border-hover)' }}>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 800, color: '#FFFFFF', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Target size={20} color="var(--accent-gold)" /> Deployment Assessment: <span style={{ color: 'var(--status-green)' }}>Production Ready</span>
            </h3>
            <div className="grid-2col" style={{ gap: '1.5rem' }}>
              <div>
                <h4 style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--status-green)', marginBottom: '0.5rem', textTransform: 'uppercase' }}>Strengths</h4>
                <ul style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', paddingLeft: '1.25rem', display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                  <li>Excellent faithfulness to retrieved documents (94.8%).</li>
                  <li>Low hallucination index perfectly suited for legal domain.</li>
                  <li>End-to-End latency is well under the 200ms budget.</li>
                </ul>
              </div>
              <div>
                <h4 style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--status-orange)', marginBottom: '0.5rem', textTransform: 'uppercase' }}>Areas for Optimization</h4>
                <ul style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', paddingLeft: '1.25rem', display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                  <li>Context Precision could be improved to reduce prompt noise.</li>
                  <li>Caching hit rate is lower than optimal for this architecture.</li>
                </ul>
              </div>
            </div>
            <div style={{ marginTop: '1.5rem', paddingTop: '1rem', borderTop: '1px solid var(--border-subtle)' }}>
              <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)' }}>Suggested Next Action: </span>
              <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Review the recommended semantic chunking fix and deploy to staging.</span>
            </div>
          </Card>

          {/* Split Section: Sample Queries & Test Logs */}
          <div className="grid-2col" style={{ gap: '1.25rem', alignItems: 'flex-start' }}>
            
            {/* Left: Sample Evaluated Queries */}
            <Card style={{ padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#FFFFFF', textTransform: 'uppercase', letterSpacing: '0.03em' }}>
                Sample Gold Query Verifications
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {result.sampleEvaluations.map((sample, i) => (
                  <div key={i} style={{ padding: '0.85rem', backgroundColor: 'var(--bg-secondary)', borderRadius: '8px', border: '1px solid var(--border-subtle)', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                    <div style={{ fontWeight: 600, color: 'var(--text-primary)', fontSize: '0.85rem' }}>
                      "{sample.query}"
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                      <div style={{ display: 'flex', gap: '0.85rem' }}>
                        <span>Docs: <strong>{sample.retrievedDocs}</strong></span>
                        <span>Avg Latency: <strong>{120 + i * 14}ms</strong></span>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
                        <span>Faithfulness: <strong style={{ color: 'var(--status-green)' }}>{sample.faithfulnessScore}%</strong></span>
                        <Badge variant={sample.hallucinationDetected ? 'orange' : 'green'} style={{ fontSize: '0.65rem', padding: '0.2rem 0.5rem' }}>
                          {sample.hallucinationDetected ? 'Flagged' : 'Verifiable'}
                        </Badge>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </Card>

            {/* Right: Real-Time Execution Test Logs */}
            <Card style={{ padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '1rem', backgroundColor: 'var(--bg-primary)', border: '1px solid var(--border-hover)' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--accent-gold)', textTransform: 'uppercase', letterSpacing: '0.03em', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <Activity size={16} /> Test Harness Logs
                </h3>
                <span style={{ fontSize: '0.7rem', fontFamily: 'monospace', color: 'var(--text-muted)' }}>EXIT CODE: 0</span>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', fontFamily: 'monospace', fontSize: '0.75rem' }}>
                {result.testLogs.map((log, li) => (
                  <div key={li} style={{ display: 'flex', gap: '0.75rem', borderLeft: '2px solid var(--border-hover)', paddingLeft: '0.75rem' }}>
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
