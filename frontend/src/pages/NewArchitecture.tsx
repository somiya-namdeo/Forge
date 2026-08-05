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
import { GeneratedArchitecture, ArchitectureComponent } from '../types';
import { decisionService, reportsService } from '../services';

interface NewArchitectureProps {
  initialArchitecture?: GeneratedArchitecture | null;
  onNavigateToReports: (arch: GeneratedArchitecture) => void;
}

export const NewArchitecture: React.FC<NewArchitectureProps> = ({
  initialArchitecture,
  onNavigateToReports,
}) => {
  const [currentArch, setCurrentArch] = useState<GeneratedArchitecture | null>(initialArchitecture || null);
  const [loading, setLoading] = useState<boolean>(!initialArchitecture);
  const [selectedComp, setSelectedComp] = useState<ArchitectureComponent | null>(null);
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
      const sessionArchs = await decisionService.getSessionArchitectures();
      if (sessionArchs.length > 0) {
        setCurrentArch(sessionArchs[0]);
      } else {
        // Generate initial report sample seamlessly if none created yet
        const defaultArch = await decisionService.generateFromPrompt(
          'Hybrid RAG pipeline for 5M+ confidential legal documents',
          'Legal RAG System'
        );
        setCurrentArch(defaultArch);
      }
      setLoading(false);
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
    a.download = `${currentArch.title.toLowerCase().replace(/\s+/g, '_')}_spec.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    setExportingJson(false);
  };

  if (loading || !currentArch) {
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

  const { summary, components, diagramNodes } = currentArch;

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
            <Badge variant={summary.productionReadiness === 'Production Ready' ? 'green' : 'orange'}>
              {summary.productionReadiness}
            </Badge>
            <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
              Generated {currentArch.timestamp}
            </span>
          </div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 800 }}>
            {currentArch.title}
          </h1>
          <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', maxWidth: '680px' }}>
            {currentArch.description}
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

      {/* Architecture Executive Summary */}
      <section>
        <div style={{ fontSize: '0.72rem', fontWeight: 700, letterSpacing: '0.08em', textTransform: 'uppercase', color: 'var(--accent-gold)', marginBottom: '0.65rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <Sparkles size={13} /> Architecture Executive Summary
        </div>
        <Card style={{ padding: '1.1rem 1.25rem', background: 'linear-gradient(135deg, rgba(19,23,32,1) 0%, rgba(26,33,48,1) 100%)', border: '1px solid var(--border-hover)' }}>
          <div className="grid-4col" style={{ rowGap: '1rem' }}>
            {/* Overall Score */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', borderRight: '1px solid var(--border-subtle)', paddingRight: '0.75rem' }}>
              <ScoreRing score={summary.overallScore} size={42} strokeWidth={4} />
              <div>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>Overall Score</div>
                <div style={{ fontSize: '1rem', fontWeight: 800, color: '#FFFFFF' }}>{summary.overallScore} / 100</div>
              </div>
            </div>

            {/* Monthly Cost */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', borderRight: '1px solid var(--border-subtle)', paddingRight: '0.75rem' }}>
              <div style={{ width: '36px', height: '36px', borderRadius: '9px', backgroundColor: 'var(--status-blue-dim)', color: 'var(--status-blue)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <DollarSign size={18} />
              </div>
              <div>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>Est. Cost</div>
                <div style={{ fontSize: '1rem', fontWeight: 800, color: '#FFFFFF' }}>{summary.estimatedMonthlyCost}</div>
              </div>
            </div>

            {/* Estimated Latency */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', borderRight: '1px solid var(--border-subtle)', paddingRight: '0.75rem' }}>
              <div style={{ width: '36px', height: '36px', borderRadius: '9px', backgroundColor: 'var(--status-green-dim)', color: 'var(--status-green)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Zap size={18} />
              </div>
              <div>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>Est. Latency</div>
                <div style={{ fontSize: '1rem', fontWeight: 800, color: '#FFFFFF' }}>{summary.estimatedLatency}</div>
              </div>
            </div>

            {/* Reasoning Confidence */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <div style={{ width: '36px', height: '36px', borderRadius: '9px', backgroundColor: 'var(--accent-gold-dim)', color: 'var(--accent-gold)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <ShieldCheck size={18} />
              </div>
              <div>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>Confidence</div>
                <div style={{ fontSize: '1rem', fontWeight: 800, color: 'var(--accent-gold)' }}>{summary.reasoningConfidence}</div>
              </div>
            </div>

            {/* Row 2 Specs */}
            <div>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>Complexity</div>
              <div style={{ fontSize: '0.875rem', fontWeight: 600, color: '#FFFFFF', marginTop: '0.15rem' }}>{summary.complexity}</div>
            </div>

            <div>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>Scalability</div>
              <div style={{ fontSize: '0.875rem', fontWeight: 600, color: '#FFFFFF', marginTop: '0.15rem' }}>{summary.scalability}</div>
            </div>

            <div>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>Production Ready</div>
              <div style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--status-green)', marginTop: '0.15rem' }}>{summary.productionReadiness}</div>
            </div>

            <div>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>Deploy Difficulty</div>
              <div style={{ fontSize: '0.875rem', fontWeight: 600, color: '#FFFFFF', marginTop: '0.15rem' }}>{summary.deploymentDifficulty}</div>
            </div>
          </div>
        </Card>
      </section>

      {/* Split Layout: Left (Architecture Diagram) | Right (Recommended Stack) */}
      <section className="grid-2col" style={{ gridTemplateColumns: '42% 1fr', alignItems: 'flex-start', gap: '1.25rem' }}>
        
        {/* Left Column: Vertical Architecture Flow Diagram — natural height, measured via ref */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', position: 'sticky', top: '80px', alignSelf: 'flex-start' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <h3 style={{ fontSize: '0.72rem', fontWeight: 700, letterSpacing: '0.06em', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
              Architecture Diagram
            </h3>
            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Interactive Data Flow</span>
          </div>

          <div ref={leftCardRef}>
          <Card style={{ padding: '1.25rem 1rem', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.25rem', backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--border-subtle)' }}>
            {diagramNodes.map((node, i) => {
              const isLast = i === diagramNodes.length - 1;
              const isSelected = selectedComp && selectedComp.name.toLowerCase().includes(node.title.toLowerCase().split(' ')[0]);

              return (
                <React.Fragment key={node.id}>
                  <motion.div
                    whileHover={{ scale: 1.015 }}
                    style={{
                      width: '100%',
                      padding: '0.65rem 1rem',
                      backgroundColor: isSelected ? 'rgba(212, 175, 99, 0.12)' : 'var(--card-bg)',
                      border: isSelected ? '1px solid var(--accent-gold)' : '1px solid var(--border-hover)',
                      borderRadius: '10px',
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      textAlign: 'center',
                      boxShadow: '0 3px 10px rgba(0,0,0,0.4)',
                      cursor: 'pointer',
                      transition: 'all 0.2s',
                    }}
                    onClick={() => {
                      const found = components.find(c => node.title.toLowerCase().includes(c.name.toLowerCase().split(' ')[0]));
                      if (found) setSelectedComp(found);
                    }}
                  >
                    <span style={{ fontSize: '0.65rem', color: 'var(--accent-gold)', fontWeight: 700, letterSpacing: '0.06em', textTransform: 'uppercase' }}>
                      {node.category}
                    </span>
                    <h4 style={{ fontSize: '0.875rem', fontWeight: 700, color: '#FFFFFF', marginTop: '0.1rem' }}>
                      {node.title}
                    </h4>
                    <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.1rem' }}>
                      {node.subtitle}
                    </p>
                  </motion.div>

                  {!isLast && (
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', height: '20px', justifyContent: 'center' }}>
                      <div style={{ width: '1.5px', height: '10px', backgroundColor: 'var(--border-hover)' }} />
                      <ArrowDown size={12} style={{ color: 'var(--accent-gold)' }} />
                    </div>
                  )}
                </React.Fragment>
              );
            })}
          </Card>
          </div>
        </div>

        {/* Right Column: Recommended Components Cards — scrollable to match diagram height */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', overflow: 'hidden' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <h3 style={{ fontSize: '0.72rem', fontWeight: 700, letterSpacing: '0.06em', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
              Recommended Components ({components.length})
            </h3>
            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Click to view trade-off analysis</span>
          </div>

          {/* Scrollable panel — height locked to left architecture card's rendered height */}
          <div
            style={{
              backgroundColor: 'var(--card-bg)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-card)',
              boxShadow: 'var(--shadow-soft)',
              overflowY: 'auto',
              overflowX: 'hidden',
              height: leftCardHeight ? `${leftCardHeight}px` : undefined,
              maxHeight: leftCardHeight ? `${leftCardHeight}px` : undefined,
              padding: '0.75rem',
            }}
          >
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {components.map((comp, idx) => {
                const isSelected = selectedComp?.id === comp.id;
                return (
                  <Card
                    key={comp.id}
                    interactive
                    delay={idx * 0.05}
                    accentBorder={isSelected}
                    onClick={() => setSelectedComp(comp)}
                    style={{ padding: '1rem 1.1rem', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}
                  >
                    {/* Top row */}
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <div>
                        <span style={{ fontSize: '0.65rem', color: 'var(--accent-gold)', fontWeight: 700, letterSpacing: '0.06em', textTransform: 'uppercase' }}>
                          {comp.category}
                        </span>
                        <h4 style={{ fontSize: '1.05rem', fontWeight: 800, color: '#FFFFFF', marginTop: '0.1rem' }}>
                          {comp.name}
                        </h4>
                      </div>
                      <ScoreRing score={comp.score} size={40} strokeWidth={3.5} />
                    </div>

                    {/* Tags */}
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem' }}>
                      {comp.tags.map(tag => (
                        <Badge key={tag} variant="neutral" style={{ fontSize: '0.68rem', padding: '0.15rem 0.5rem' }}>
                          {tag}
                        </Badge>
                      ))}
                    </div>

                    {/* KPI Grid: Latency | Cost | Complexity */}
                    <div
                      style={{
                        display: 'grid',
                        gridTemplateColumns: 'repeat(3, 1fr)',
                        backgroundColor: 'var(--bg-secondary)',
                        padding: '0.6rem 0.75rem',
                        borderRadius: '8px',
                        border: '1px solid var(--border-subtle)',
                        gap: '0.4rem',
                      }}
                    >
                      <div>
                        <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Latency</span>
                        <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#FFFFFF', marginTop: '0.05rem' }}>{comp.latency}</div>
                      </div>
                      <div>
                        <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Cost</span>
                        <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#FFFFFF', marginTop: '0.05rem' }}>{comp.cost}</div>
                      </div>
                      <div>
                        <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Complexity</span>
                        <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#FFFFFF', marginTop: '0.05rem' }}>{comp.complexity}</div>
                      </div>
                    </div>

                    {/* Justification snippet */}
                    {comp.justification && (
                      <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.45 }}>
                        <strong style={{ color: 'var(--text-primary)' }}>Why selected:</strong> {comp.justification}
                      </div>
                    )}

                    {/* Confidence Progress Bar */}
                    <div style={{ paddingTop: '0.2rem' }}>
                      <ProgressBar value={comp.confidence} label="Engineering Confidence Level" color="auto" height={5} />
                    </div>
                  </Card>
                );
              })}
            </div>
          </div>
        </div>
      </section>
    </motion.div>
  );
};
