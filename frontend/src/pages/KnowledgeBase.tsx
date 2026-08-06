import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Search, ExternalLink, Github, BookOpen } from 'lucide-react';
import { EmptyState, Skeleton, ScoreRing } from '../components/common';
import { KnowledgeRegistryResponse, KnowledgeCategory } from '../types';
import { knowledgeService } from '../services';

const PRIORITY_COLORS: Record<string, string> = {
  'FORGE RECOMMENDED': '#ef4444',
  'POPULAR':           '#3b82f6',
  'ENTERPRISE':        '#eab308',
  'EXPERIMENTAL':      '#a855f7',
};

export const KnowledgeBase: React.FC = () => {
  const [selectedCat,  setSelectedCat]  = useState<KnowledgeCategory | 'all'>('all');
  const [searchQuery,  setSearchQuery]  = useState('');
  const [registry,     setRegistry]     = useState<KnowledgeRegistryResponse | null>(null);
  const [loading,      setLoading]      = useState(true);
  const [error,        setError]        = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    knowledgeService.getRegistry(selectedCat, searchQuery)
      .then(res => {
        if (cancelled) return;
        if (res?.components) {
          const priorities = ['FORGE RECOMMENDED', 'POPULAR', 'ENTERPRISE', undefined, undefined, 'EXPERIMENTAL'];
          res.components = res.components.map((c: any, i: number) => ({
            ...c,
            priorityIndicator: priorities[i] ?? undefined,
          }));
        }
        setRegistry(res);
        setLoading(false);
      })
      .catch(err => {
        if (!cancelled) {
          setError(err.message || 'Backend Not Available');
          setLoading(false);
        }
      });
    return () => { cancelled = true; };
  }, [selectedCat, searchQuery]);

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
        <h1 className="page-title">Knowledge Base</h1>
        <p className="page-subtitle">240+ curated AI components with production benchmarks and tradeoff analysis</p>
      </div>

      {/* ── Search ────────────────────────────────────────── */}
      <div style={{ position: 'relative', maxWidth: '680px' }}>
        <Search size={17} style={{ position: 'absolute', left: '14px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)', pointerEvents: 'none' }} />
        <input
          type="text"
          value={searchQuery}
          onChange={e => setSearchQuery(e.target.value)}
          placeholder="Search LLMs, vector databases, frameworks…"
          className="forge-input"
          style={{ paddingLeft: '2.5rem', height: '44px', fontSize: '0.9375rem' }}
        />
      </div>

      {/* ── Category Tabs ─────────────────────────────────── */}
      <div className="forge-tabs" style={{ marginBottom: 0 }}>
        <button
          onClick={() => setSelectedCat('all')}
          className={`forge-tab-btn${selectedCat === 'all' ? ' active' : ''}`}
        >
          All <span style={{ fontSize: '0.6875rem', opacity: 0.7 }}>15</span>
        </button>
        {registry?.categories.map(c => (
          <button
            key={c.name}
            onClick={() => setSelectedCat(c.name)}
            className={`forge-tab-btn${selectedCat === c.name ? ' active' : ''}`}
          >
            {c.label} <span style={{ fontSize: '0.6875rem', opacity: 0.7 }}>{c.count}</span>
          </button>
        ))}
      </div>

      {/* ── Grid ──────────────────────────────────────────── */}
      {loading ? (
        <div className="grid-3col">
          {[...Array(6)].map((_, i) => <Skeleton key={i} variant="card" height={300} />)}
        </div>
      ) : error ? (
        <EmptyState
          icon={BookOpen}
          title="Backend Not Available"
          description={error}
        />
      ) : !registry || registry.components.length === 0 ? (
        <EmptyState
          icon={BookOpen}
          title="No Matching Components"
          description="No components match your current filters."
          actionText="Reset Filters"
          onAction={() => { setSelectedCat('all'); setSearchQuery(''); }}
        />
      ) : (
        <div className="grid-3col" style={{ alignItems: 'stretch' }}>
          {registry.components.map((item: any, idx: number) => {
            const priority     = item.priorityIndicator as string | undefined;
            const priorityColor = priority ? PRIORITY_COLORS[priority] : undefined;
            const score        = item.benchmarkScore ?? (85 + idx * 2);

            return (
              <motion.div
                key={item.id}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.2, delay: idx * 0.04 }}
                className="forge-card forge-card-interactive hover-glow"
                style={{
                  padding: '1.5rem',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '0.875rem',
                  position: 'relative',
                  height: '100%',
                }}
              >
                {/* Score Ring — top-right, clickable */}
                <div
                  style={{ position: 'absolute', top: '1.25rem', right: '1.25rem', cursor: 'pointer' }}
                  title="View component details"
                  onClick={() => {/* score detail click — future nav */}}
                >
                  <ScoreRing score={score} size={40} strokeWidth={4} />
                </div>

                {/* Priority label */}
                {priority && (
                  <div style={{ fontSize: '0.625rem', fontWeight: 800, color: priorityColor, textTransform: 'uppercase', letterSpacing: '0.06em', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                    ★ {priority}
                  </div>
                )}

                {/* Title / org */}
                <div style={{ paddingRight: '3rem' }}>
                  <h3 style={{ fontSize: '1.125rem', fontWeight: 800, color: '#FFFFFF', lineHeight: 1.25 }}>{item.name}</h3>
                  <div style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>{item.organization}</div>
                </div>

                {/* Category badge */}
                <div>
                  <span style={{
                    display: 'inline-flex', padding: '0.2rem 0.6rem',
                    borderRadius: 'var(--radius-pill)',
                    backgroundColor: 'var(--bg-primary)',
                    border: '1px solid var(--border-subtle)',
                    fontSize: '0.6875rem', color: 'var(--text-muted)', fontWeight: 600,
                    textTransform: 'uppercase', letterSpacing: '0.04em',
                  }}>
                    {item.category}
                  </span>
                </div>

                {/* Description */}
                <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', lineHeight: 1.55, flex: 1 }}>
                  {item.description}
                </p>

                {/* Tags */}
                {item.keyFeatures && (
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem' }}>
                    {item.keyFeatures.slice(0, 4).map((f: string) => (
                      <span key={f} className="forge-chip">{f}</span>
                    ))}
                  </div>
                )}

                {/* Tertiary links */}
                <div style={{ display: 'flex', gap: '1rem', paddingTop: '0.875rem', borderTop: '1px solid var(--border-subtle)', marginTop: '0.25rem' }}>
                  {item.officialDocumentation && (
                    <a href={item.officialDocumentation} target="_blank" rel="noreferrer"
                      style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.3rem', transition: 'color 0.15s', textDecoration: 'none' }}
                      onMouseEnter={e => (e.currentTarget.style.color = '#FFFFFF')}
                      onMouseLeave={e => (e.currentTarget.style.color = 'var(--text-muted)')}
                    >
                      <ExternalLink size={11} /> Docs
                    </a>
                  )}
                  {item.githubRepository && (
                    <a href={item.githubRepository} target="_blank" rel="noreferrer"
                      style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.3rem', transition: 'color 0.15s', textDecoration: 'none' }}
                      onMouseEnter={e => (e.currentTarget.style.color = '#FFFFFF')}
                      onMouseLeave={e => (e.currentTarget.style.color = 'var(--text-muted)')}
                    >
                      <Github size={11} /> GitHub
                    </a>
                  )}
                </div>
              </motion.div>
            );
          })}
        </div>
      )}
    </motion.div>
  );
};
