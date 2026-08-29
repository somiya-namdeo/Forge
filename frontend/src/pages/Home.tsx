import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Sparkles,
  ArrowRight,
  Brain,
  BarChart2,
  BookOpen,
  Cpu,
  CheckCircle2,
  FileText
} from 'lucide-react';
import { Card, Badge, Button } from '../components/common';
import { decisionService } from '../services';
import { GeneratedArchitecture } from '../types';
import { NavPage } from '../components/navigation';
import { useForgeContext } from '../context';

interface HomeProps {
  onNavigate: (page: NavPage) => void;
}

const QUICK_TOPICS = [
  { name: 'Healthcare AI', prompt: 'Build a healthcare RAG assistant for 2 million clinical documents with strict data privacy, high factual accuracy, and low-latency responses.' },
  { name: 'Finance Copilot', prompt: 'Build a financial analysis copilot for 500,000 market and research documents with strong security, reliable retrieval, and moderate operating costs.' },
  { name: 'Code Assistant', prompt: 'Build a code assistant for a large enterprise repository that provides accurate code search and generation with low latency and support for private deployments.' },
  { name: 'Research Agent', prompt: 'Build a research agent that processes academic papers and technical reports, retrieves relevant evidence, and generates cited research summaries.' },
  { name: 'Legal AI', prompt: 'Build a legal RAG assistant for 5 million confidential documents with low latency, high factual accuracy, and strict data privacy.' },
  { name: 'Support AI', prompt: 'Build an AI customer support assistant for 10 million knowledge-base articles with high availability, fast responses, and accurate answers.' },
];

export const Home: React.FC<HomeProps> = ({ onNavigate }) => {
  const { setDecisionResult, addSessionArchitecture } = useForgeContext();
  const [promptInput, setPromptInput] = useState('');
  const [selectedTopic, setSelectedTopic] = useState('Legal AI');
  const [generating, setGenerating] = useState(false);

  const handleGenerate = async () => {
    if (!promptInput.trim() && !selectedTopic) return;
    setGenerating(true);
    try {
      const response = await decisionService.runDecisionEngine({
        project_name: selectedTopic,
        project_description: promptInput || `Build a high-precision RAG assistant optimized for ${selectedTopic}.`,
        deployment_target: 'aws',
        priority: 'balanced'
      });
      setDecisionResult(response as any);
      addSessionArchitecture(response as any);
      // Navigate straight to the generated architecture report
      onNavigate('new-architecture');
    } catch (err: any) {
      console.error(err.message || 'Failed to generate architecture');
    } finally {
      setGenerating(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.3, ease: 'easeOut' }}
      style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}
    >
      {/* Hero Section */}
      <section
        style={{
          backgroundColor: 'var(--card-bg)',
          border: '1px solid var(--border-subtle)',
          borderRadius: '18px',
          padding: '1.75rem 2rem',
          boxShadow: '0 16px 40px rgba(0,0,0,0.55)',
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1.5rem', position: 'relative', zIndex: 2 }}>
          <div style={{ flex: '1 1 520px', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <Badge variant="gold" style={{ padding: '0.4rem 1rem', fontSize: '0.78rem' }}>
                ● AI ARCHITECT · READY
              </Badge>
            </div>

            <h1 style={{ fontSize: '2rem', fontWeight: 800, lineHeight: 1.15 }}>
              What are you <span className="text-gradient-gold">building today?</span>
            </h1>

            <p style={{ fontSize: '0.92rem', color: 'var(--text-secondary)', maxWidth: '500px' }}>
              Describe your AI project requirements in natural language. Forge designs the complete production-ready architecture for you.
            </p>

            {/* Prompt Input Box */}
            <div
              style={{
                backgroundColor: 'var(--bg-secondary)',
                border: '1px solid var(--border-hover)',
                borderRadius: '12px',
                padding: '0.9rem 1rem',
                display: 'flex',
                flexDirection: 'column',
                gap: '0.75rem',
                boxShadow: 'inset 0 2px 8px rgba(0,0,0,0.4)',
                marginTop: '0.25rem',
              }}
            >
              <textarea
                value={promptInput}
                onChange={(e) => setPromptInput(e.target.value)}
                placeholder="Build a legal RAG assistant for 5 million confidential documents with low latency and high factual accuracy..."
                rows={2}
                style={{
                  width: '100%',
                  resize: 'none',
                  fontSize: '0.88rem',
                  color: '#FFFFFF',
                  lineHeight: '1.5',
                }}
              />

              {/* Quick Topic Chips */}
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.45rem', alignItems: 'center' }}>
                <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 600, marginRight: '0.15rem' }}>TOPICS:</span>
                {QUICK_TOPICS.map((topic) => {
                  const isSelected = selectedTopic === topic.name;
                  return (
                    <button
                      key={topic.name}
                      type="button"
                      onClick={() => {
                        setSelectedTopic(topic.name);
                        setPromptInput(topic.prompt);
                      }}
                      style={{
                        padding: '0.2rem 0.65rem',
                        borderRadius: 'var(--radius-pill)',
                        fontSize: '0.75rem',
                        fontWeight: isSelected ? 600 : 500,
                        backgroundColor: isSelected ? 'rgba(212, 175, 99, 0.2)' : 'rgba(255, 255, 255, 0.04)',
                        color: isSelected ? 'var(--accent-gold)' : 'var(--text-secondary)',
                        border: isSelected ? '1px solid var(--border-accent)' : '1px solid var(--border-subtle)',
                        transition: 'all 0.2s',
                      }}
                    >
                      {topic.name}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Action CTA */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginTop: '0.2rem' }}>
              <Button
                variant="primary"
                icon={Sparkles}
                onClick={handleGenerate}
                disabled={generating}
              >
                {generating ? 'Engineering Architecture...' : 'Generate Architecture'}
              </Button>
              <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                Powered by verifiable open source registries
              </span>
            </div>
          </div>

          {/* Animated Hexagonal 3D AI Wireframe Visualizer */}
          <div
            style={{
              flex: '0 0 240px',
              height: '240px',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              position: 'relative',
              margin: '0 auto',
            }}
          >
            <motion.div
              animate={{
                rotateY: [0, 360],
                rotateZ: [0, 8, -8, 0],
              }}
              transition={{ duration: 25, repeat: Infinity, ease: 'linear' }}
              style={{
                width: '180px',
                height: '180px',
                position: 'relative',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              {/* Outer Hexagon Wireframe SVG */}
              <svg width="180" height="180" viewBox="0 0 240 240" fill="none" style={{ position: 'absolute', inset: 0, filter: 'drop-shadow(0 0 16px rgba(212, 175, 99, 0.3))' }}>
                <polygon
                  points="120,10 215,65 215,175 120,230 25,175 25,65"
                  stroke="var(--accent-gold)"
                  strokeWidth="1.5"
                  strokeDasharray="4 4"
                  fill="rgba(212, 175, 99, 0.02)"
                />
                <polygon
                  points="120,40 185,80 185,160 120,200 55,160 55,80"
                  stroke="rgba(255, 255, 255, 0.15)"
                  strokeWidth="1"
                  fill="rgba(19, 23, 32, 0.8)"
                />
                {/* Connecting lines */}
                <line x1="120" y1="10" x2="120" y2="40" stroke="var(--border-accent)" strokeWidth="1" />
                <line x1="215" y1="65" x2="185" y2="80" stroke="var(--border-accent)" strokeWidth="1" />
                <line x1="215" y1="175" x2="185" y2="160" stroke="var(--border-accent)" strokeWidth="1" />
                <line x1="120" y1="230" x2="120" y2="200" stroke="var(--border-accent)" strokeWidth="1" />
                <line x1="25" y1="175" x2="55" y2="160" stroke="var(--border-accent)" strokeWidth="1" />
                <line x1="25" y1="65" x2="55" y2="80" stroke="var(--border-accent)" strokeWidth="1" />

                {/* Glowing Vertices */}
                <circle cx="120" cy="10" r="5" fill="var(--accent-gold)" />
                <circle cx="215" cy="65" r="4" fill="var(--status-blue)" />
                <circle cx="215" cy="175" r="4" fill="var(--status-green)" />
                <circle cx="120" cy="230" r="5" fill="var(--accent-gold)" />
                <circle cx="25" cy="175" r="4" fill="var(--status-purple)" />
                <circle cx="25" cy="65" r="4" fill="#f97316" />
              </svg>

              {/* Center Brain/Sparkle core */}
              <motion.div
                animate={{ scale: [0.95, 1.08, 0.95] }}
                transition={{ repeat: Infinity, duration: 4, ease: 'easeInOut' }}
                style={{
                  width: '58px',
                  height: '58px',
                  borderRadius: '50%',
                  background: 'radial-gradient(circle, rgba(212, 175, 99, 0.25) 0%, rgba(11, 13, 18, 0.9) 100%)',
                  border: '1px solid var(--accent-gold)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  boxShadow: 'var(--shadow-glow-gold)',
                  zIndex: 10,
                }}
              >
                <Cpu size={26} style={{ color: 'var(--accent-gold)' }} />
              </motion.div>
            </motion.div>
            <div style={{ marginTop: '1rem', fontFamily: 'var(--font-heading)', fontWeight: 700, fontSize: '0.75rem', letterSpacing: '0.15em', color: 'var(--accent-gold)', textTransform: 'uppercase' }}>
              AI ARCHITECT · ENGINE
            </div>
          </div>
        </div>
      </section>

      {/* Quick Start Section */}
      <section style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', marginTop: '0.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '1rem' }}>
          <div style={{ height: '1px', flex: 1, background: 'linear-gradient(90deg, transparent, var(--border-accent))', opacity: 0.5 }} />
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Sparkles size={14} style={{ color: 'var(--accent-gold)' }} />
            <h3 style={{ fontSize: '0.85rem', fontWeight: 700, letterSpacing: '0.15em', color: 'var(--text-primary)', textTransform: 'uppercase' }}>
              QUICK START
            </h3>
            <Sparkles size={14} style={{ color: 'var(--accent-gold)' }} />
          </div>
          <div style={{ height: '1px', flex: 1, background: 'linear-gradient(270deg, transparent, var(--border-accent))', opacity: 0.5 }} />
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(190px, 1fr))',
          gap: '1.25rem',
          alignItems: 'stretch'
        }}>
          {/* Card 1: New Architecture */}
          <motion.div whileHover="hover" initial="initial">
            <Card
              interactive
              onClick={() => onNavigate('new-architecture')}
              style={{ padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '1rem', height: '100%', cursor: 'pointer', background: 'linear-gradient(135deg, rgba(212,175,99,0.05) 0%, rgba(19,23,32,1) 100%)', borderColor: 'var(--border-accent)' }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', width: '42px', height: '42px', borderRadius: '50%', border: '1px solid var(--accent-gold)', backgroundColor: 'rgba(212,175,99,0.1)' }}>
                <Sparkles size={20} style={{ color: 'var(--accent-gold)' }} />
              </div>
              <div style={{ flex: 1 }}>
                <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#FFFFFF', marginBottom: '0.35rem' }}>New Architecture</h4>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.4 }}>Design a custom stack from scratch</p>
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: 'auto' }}>
                <motion.div variants={{ hover: { x: 4 } }} transition={{ duration: 0.2 }}>
                  <ArrowRight size={16} style={{ color: 'var(--accent-gold)' }} />
                </motion.div>
              </div>
            </Card>
          </motion.div>

          {/* Card 2: Decision Engine */}
          <motion.div whileHover="hover" initial="initial">
            <Card
              interactive
              onClick={() => onNavigate('decision-engine')}
              style={{ padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '1rem', height: '100%', cursor: 'pointer' }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', width: '42px', height: '42px', borderRadius: '50%', border: '1px solid var(--status-blue)', backgroundColor: 'rgba(56, 189, 248, 0.1)' }}>
                <Brain size={20} style={{ color: 'var(--status-blue)' }} />
              </div>
              <div style={{ flex: 1 }}>
                <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#FFFFFF', marginBottom: '0.35rem' }}>Decision Engine</h4>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.4 }}>Get evidence-backed architecture recommendations</p>
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: 'auto' }}>
                <motion.div variants={{ hover: { x: 4 } }} transition={{ duration: 0.2 }}>
                  <ArrowRight size={16} style={{ color: 'var(--status-blue)' }} />
                </motion.div>
              </div>
            </Card>
          </motion.div>

          {/* Card 3: Run Evaluation */}
          <motion.div whileHover="hover" initial="initial">
            <Card
              interactive
              onClick={() => onNavigate('evaluation')}
              style={{ padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '1rem', height: '100%', cursor: 'pointer' }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', width: '42px', height: '42px', borderRadius: '50%', border: '1px solid var(--status-green)', backgroundColor: 'rgba(34, 197, 94, 0.1)' }}>
                <CheckCircle2 size={20} style={{ color: 'var(--status-green)' }} />
              </div>
              <div style={{ flex: 1 }}>
                <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#FFFFFF', marginBottom: '0.35rem' }}>Run Evaluation</h4>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.4 }}>Evaluate RAG pipeline quality</p>
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: 'auto' }}>
                <motion.div variants={{ hover: { x: 4 } }} transition={{ duration: 0.2 }}>
                  <ArrowRight size={16} style={{ color: 'var(--status-green)' }} />
                </motion.div>
              </div>
            </Card>
          </motion.div>

          {/* Card 4: Browse Knowledge Base */}
          <motion.div whileHover="hover" initial="initial">
            <Card
              interactive
              onClick={() => onNavigate('knowledge-base')}
              style={{ padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '1rem', height: '100%', cursor: 'pointer' }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', width: '42px', height: '42px', borderRadius: '50%', border: '1px solid var(--status-purple)', backgroundColor: 'rgba(168, 85, 247, 0.1)' }}>
                <BookOpen size={20} style={{ color: 'var(--status-purple)' }} />
              </div>
              <div style={{ flex: 1 }}>
                <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#FFFFFF', marginBottom: '0.35rem' }}>Browse Knowledge Base</h4>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.4 }}>Explore verified AI technologies</p>
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: 'auto' }}>
                <motion.div variants={{ hover: { x: 4 } }} transition={{ duration: 0.2 }}>
                  <ArrowRight size={16} style={{ color: 'var(--status-purple)' }} />
                </motion.div>
              </div>
            </Card>
          </motion.div>

          {/* Card 5: View Reports */}
          <motion.div whileHover="hover" initial="initial">
            <Card
              interactive
              onClick={() => onNavigate('reports')}
              style={{ padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '1rem', height: '100%', cursor: 'pointer' }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', width: '42px', height: '42px', borderRadius: '50%', border: '1px solid #f97316', backgroundColor: 'rgba(249, 115, 22, 0.1)' }}>
                <FileText size={20} style={{ color: '#f97316' }} />
              </div>
              <div style={{ flex: 1 }}>
                <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#FFFFFF', marginBottom: '0.35rem' }}>View Reports</h4>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.4 }}>Generate and export architecture reports</p>
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: 'auto' }}>
                <motion.div variants={{ hover: { x: 4 } }} transition={{ duration: 0.2 }}>
                  <ArrowRight size={16} style={{ color: '#f97316' }} />
                </motion.div>
              </div>
            </Card>
          </motion.div>
        </div>
      </section>
    </motion.div>
  );
};
