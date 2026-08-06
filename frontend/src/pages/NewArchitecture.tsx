import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import {
  Sparkles,
  ArrowDown,
  Download,
  Share2,
  CheckCircle,
  Cpu,
  Database,
  Layers,
  ShieldCheck,
  Zap,
  DollarSign,
  Activity,
  FileCode2
} from 'lucide-react';
import { Card, Badge, Button, ScoreRing, ProgressBar, EmptyState, Skeleton } from '../components/common';
import { DecisionResponse, DecisionRecommendationItem } from '../types';
import { decisionService } from '../services';
import {
  getConfidenceLabel, getConfidenceColor, getConfidenceBgColor, getConfidenceBorderColor,
  getSummaryConfidenceWord, improveTradeOffWording, improveAlternativeMessaging, getExplanationPrefix
} from '../utils/decisionUtils';

interface NewArchitectureProps {
  initialArchitecture?: DecisionResponse | null;
  onNavigateToReports: (arch: any) => void;
}

export const NewArchitecture: React.FC<NewArchitectureProps> = ({
  initialArchitecture,
  onNavigateToReports,
}) => {
  const [currentArch, setCurrentArch] = useState<DecisionResponse | null>(initialArchitecture || null);
  const [loading, setLoading] = useState<boolean>(!initialArchitecture);
  const [error, setError] = useState<string | null>(null);
  const [selectedComp, setSelectedComp] = useState<DecisionRecommendationItem | null>(null);
  const [exportingJson, setExportingJson] = useState(false);
  const leftCardRef = useRef<HTMLDivElement>(null);
  const [leftCardHeight, setLeftCardHeight] = useState<number | null>(null);

  useEffect(() => {
    async function loadDefaultOrSession() {
      if (currentArch) {
        setLoading(false);
        return;
      }
      setLoading(true);
      setError(null);
      try {
        const defaultArch = await decisionService.runDecisionEngine({
          project_name: 'Legal RAG System',
          project_description: 'Hybrid RAG pipeline for 5M+ confidential legal documents',
          deployment_target: 'aws',
          priority: 'balanced'
        });
        setCurrentArch(defaultArch);
      } catch (err: any) {
        setError(err.message || 'Failed to fetch architecture recommendations');
      } finally {
        setLoading(false);
      }
    }
    loadDefaultOrSession();
  }, [initialArchitecture]);

  // Measure the left architecture card's rendered height so the right panel matches it exactly
  useEffect(() => {
    const el = leftCardRef.current;
    if (!el) return;
    const observer = new ResizeObserver(() => {
      setLeftCardHeight(el.offsetHeight);
    });
    observer.observe(el);
    setLeftCardHeight(el.offsetHeight);
    return () => observer.disconnect();
  }, [currentArch]);

  const handleExportJson = async () => {
    if (!currentArch) return;
    setExportingJson(true);
    const jsonString = JSON.stringify(currentArch, null, 2);
    const blob = new Blob([jsonString], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `architecture_spec.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    setExportingJson(false);
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
        <Skeleton variant="title" width={320} />
        <Skeleton variant="card" height={150} />
        <div className="grid-2col">
          <Skeleton variant="chart" height={520} />
          <Skeleton variant="chart" height={520} />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <EmptyState
        compact
        icon={Layers}
        title="Architecture Engine Failed"
        description={error}
        actionText="Try Again"
        onAction={() => window.location.reload()}
      />
    );
  }

  if (!currentArch) return null;

  const { recommendations, summary, overall_confidence, generated_at, metadata } = currentArch;


  // Build diagram nodes dynamically based on recommendations
  const diagramNodes = recommendations.map((r, i) => ({
    id: `node-${i}`,
    title: r.recommended,
    subtitle: r.category,
    category: r.category
  }));

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.3 }}
      style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}
    >
      {/* Header Bar */}
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '1rem' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', flexWrap: 'wrap' }}>
            <Badge variant="gold">● ENGINEERED PIPELINE</Badge>
            <Badge variant="green">
              Production Ready
            </Badge>
            <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
              Generated {new Date(generated_at).toLocaleString()}
            </span>
          </div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 800 }}>
            Optimized AI Architecture
          </h1>
          <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', maxWidth: '680px' }}>
            {summary}
          </p>
        </div>

        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
          <Button variant="secondary" icon={Download} onClick={handleExportJson} disabled={exportingJson}>
            Export JSON
          </Button>
          <Button variant="primary" icon={FileCode2} onClick={() => onNavigateToReports(currentArch)}>
            Production Report →
          </Button>
        </div>
      </header>

      {/* Split Layout: Left (8 columns, Cards) | Right (4 columns, Diagram + Summary) */}
      <section style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', alignItems: 'flex-start', gap: '1.5rem' }}>
        
        {/* Left Column: Recommended Components Cards */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <h3 style={{ fontSize: '0.72rem', fontWeight: 700, letterSpacing: '0.06em', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
              Recommended Components ({recommendations.length})
            </h3>
            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Click to highlight on diagram</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {recommendations.map((comp, idx) => {
              const isSelected = selectedComp?.category === comp.category;
              
              let whySelected = comp.reason;
              let tradeOff = "";
              let alternative = "";
              
              if (comp.reason.includes("Why selected: ") && comp.reason.includes("Trade-off: ") && comp.reason.includes("Alternative: ")) {
                 const whyParts = comp.reason.split("Trade-off: ");
                 whySelected = whyParts[0].replace("Why selected: ", "").trim();
                 if (whyParts.length > 1) {
                     const tradeParts = whyParts[1].split("Alternative: ");
                     tradeOff = tradeParts[0].trim();
                     if (tradeParts.length > 1) alternative = tradeParts[1].trim();
                 }
              }

              return (
                <Card
                  key={comp.category}
                  interactive
                  delay={idx * 0.05}
                  accentBorder={isSelected}
                  onClick={() => setSelectedComp(comp)}
                  style={{ padding: '0.9rem 1.1rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}
                >
                  {/* Top row */}
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <div>
                      <span style={{ fontSize: '0.65rem', color: 'var(--accent-gold)', fontWeight: 700, letterSpacing: '0.06em', textTransform: 'uppercase' }}>
                        {comp.category}
                      </span>
                      <h4 style={{ fontSize: '1.05rem', fontWeight: 800, color: '#FFFFFF', marginTop: '0.1rem' }}>
                        {comp.recommended}
                      </h4>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', backgroundColor: getConfidenceBgColor(comp.confidence), padding: '0.2rem 0.5rem', borderRadius: '6px', border: `1px solid ${getConfidenceBorderColor(comp.confidence)}` }}>
                      <ScoreRing score={Math.round(comp.confidence * 100)} size={18} strokeWidth={3} />
                      <span style={{ fontSize: '0.65rem', fontWeight: 700, color: getConfidenceColor(comp.confidence) }}>
                        {getConfidenceLabel(comp.confidence)}
                      </span>
                    </div>
                  </div>

                  {/* Justification snippet */}
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.45, marginTop: '0.2rem' }}>
                    <strong style={{ color: 'var(--status-green)', fontSize: '0.75rem' }}>{getExplanationPrefix(idx)}:</strong> {whySelected}
                  </div>
                  {tradeOff && (
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.45 }}>
                      <strong style={{ color: '#f97316', fontSize: '0.75rem' }}>Trade-off:</strong> {improveTradeOffWording(tradeOff)}
                    </div>
                  )}
                  {alternative && (
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.45 }}>
                      <strong style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>Alternative:</strong> {improveAlternativeMessaging(alternative)}
                    </div>
                  )}
                </Card>
              );
            })}
          </div>
        </div>

        {/* Right Column: Sticky Sidebar with Summary and Diagram */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', position: 'sticky', top: '80px', alignSelf: 'flex-start' }}>
          
          {/* Architecture Executive Summary */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <div style={{ fontSize: '0.65rem', fontWeight: 700, letterSpacing: '0.08em', textTransform: 'uppercase', color: 'var(--accent-gold)', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
              <Sparkles size={12} /> Executive Summary
            </div>
            <Card style={{ padding: '1rem', background: 'linear-gradient(135deg, rgba(19,23,32,1) 0%, rgba(26,33,48,1) 100%)', border: '1px solid var(--border-hover)' }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', rowGap: '1rem', columnGap: '0.75rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                  <ScoreRing score={Math.round(overall_confidence * 100)} size={36} strokeWidth={3} />
                  <div>
                    <div style={{ fontSize: '0.62rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                      Overall Confidence
                    </div>
                    <div style={{ fontSize: '0.9rem', fontWeight: 800, color: '#FFFFFF' }}>{Math.round(overall_confidence * 100)}/100</div>
                  </div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                  <div style={{ width: '32px', height: '32px', borderRadius: '8px', backgroundColor: 'var(--accent-gold-dim)', color: 'var(--accent-gold)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <ShieldCheck size={16} />
                  </div>
                  <div>
                    <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>Confidence</div>
                    <div style={{ fontSize: '0.9rem', fontWeight: 800, color: 'var(--accent-gold)' }}>{getSummaryConfidenceWord(overall_confidence)}</div>
                  </div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                  <div style={{ width: '32px', height: '32px', borderRadius: '8px', backgroundColor: 'var(--status-blue-dim)', color: 'var(--status-blue)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <DollarSign size={16} />
                  </div>
                  <div>
                    <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>Est. Cost</div>
                    <div style={{ fontSize: '0.9rem', fontWeight: 800, color: '#FFFFFF' }}>{metadata?.estimated_cost || 'Unknown'}</div>
                  </div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                  <div style={{ width: '32px', height: '32px', borderRadius: '8px', backgroundColor: 'var(--status-green-dim)', color: 'var(--status-green)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Zap size={16} />
                  </div>
                  <div>
                    <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>Est. Latency</div>
                    <div style={{ fontSize: '0.9rem', fontWeight: 800, color: '#FFFFFF' }}>{metadata?.estimated_latency || 'Unknown'}</div>
                  </div>
                </div>
              </div>
            </Card>
          </div>

          {/* Architecture Diagram */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <h3 style={{ fontSize: '0.65rem', fontWeight: 700, letterSpacing: '0.06em', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                Architecture Diagram
              </h3>
            </div>
            <Card style={{ padding: '1rem', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.2rem', backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--border-subtle)' }}>
              {diagramNodes.map((node, i) => {
                const isLast = i === diagramNodes.length - 1;
                const isSelected = selectedComp && selectedComp.recommended === node.title;

                return (
                  <React.Fragment key={node.id}>
                    <motion.div
                      whileHover={{ scale: 1.015 }}
                      style={{
                        width: '100%',
                        padding: '0.5rem 0.75rem',
                        backgroundColor: isSelected ? 'rgba(212, 175, 99, 0.12)' : 'var(--card-bg)',
                        border: isSelected ? '1px solid var(--accent-gold)' : '1px solid var(--border-hover)',
                        borderRadius: '8px',
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        textAlign: 'center',
                        boxShadow: '0 2px 8px rgba(0,0,0,0.3)',
                        cursor: 'pointer',
                        transition: 'all 0.2s',
                      }}
                      onClick={() => {
                        const found = recommendations.find(r => r.recommended === node.title);
                        if (found) setSelectedComp(found);
                      }}
                    >
                      <span style={{ fontSize: '0.55rem', color: 'var(--accent-gold)', fontWeight: 700, letterSpacing: '0.06em', textTransform: 'uppercase' }}>
                        {node.category}
                      </span>
                      <h4 style={{ fontSize: '0.75rem', fontWeight: 700, color: '#FFFFFF', marginTop: '0.1rem' }}>
                        {node.title}
                      </h4>
                    </motion.div>

                    {!isLast && (
                      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', height: '16px', justifyContent: 'center' }}>
                        <div style={{ width: '1.5px', height: '8px', backgroundColor: 'var(--border-hover)' }} />
                        <ArrowDown size={10} style={{ color: 'var(--accent-gold)' }} />
                      </div>
                    )}
                  </React.Fragment>
                );
              })}
            </Card>
          </div>
        </div>
      </section>
    </motion.div>
  );
};

