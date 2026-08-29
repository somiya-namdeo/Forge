import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Search, ExternalLink, Github, BookOpen, ChevronLeft, ChevronRight } from 'lucide-react';
import { EmptyState, Skeleton } from '../components/common';
import { KnowledgeRegistryResponse } from '../types';
import { knowledgeService } from '../services';

export const KnowledgeBase: React.FC = () => {
  const [selectedCat,  setSelectedCat]  = useState<string | 'all'>('all');
  const [searchQuery,  setSearchQuery]  = useState('');
  const [page,         setPage]         = useState(1);
  const [registry,     setRegistry]     = useState<KnowledgeRegistryResponse | null>(null);
  const [loading,      setLoading]      = useState(true);
  const [error,        setError]        = useState<string | null>(null);

  // Debounce search
  const [debouncedSearch, setDebouncedSearch] = useState(searchQuery);
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedSearch(searchQuery);
      setPage(1); // Reset page on new search
    }, 300);
    return () => clearTimeout(handler);
  }, [searchQuery]);

  useEffect(() => {
    setPage(1); // Reset page on category change
  }, [selectedCat]);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    knowledgeService.getRegistry(selectedCat, debouncedSearch, page)
      .then(res => {
        if (cancelled) return;
        setRegistry(res);
        setLoading(false);
      })
      .catch(err => {
        if (!cancelled) {
          setError(err.message || 'An error occurred while fetching knowledge components.');
          setLoading(false);
        }
      });
    return () => { cancelled = true; };
  }, [selectedCat, debouncedSearch, page]);

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
        <p className="page-subtitle">
          {registry 
            ? `${registry.totalComponents} technologies across ${registry.categories.length} categories`
            : "Loading technologies..."}
        </p>
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
          All {registry && <span style={{ fontSize: '0.6875rem', opacity: 0.7 }}>{registry.totalComponents}</span>}
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
          title="Backend Error"
          description={error}
        />
      ) : !registry || registry.components.length === 0 ? (
        <EmptyState
          icon={BookOpen}
          title="No Knowledge Components Found"
          description="No components match your current filters."
          actionText="Reset Filters"
          onAction={() => { setSelectedCat('all'); setSearchQuery(''); }}
        />
      ) : (
        <>
          <div className="grid-3col" style={{ alignItems: 'stretch' }}>
            {registry.components.map((item: any, idx: number) => {
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
                  {/* Priority label */}
                  {item.priority && (
                    <div style={{ fontSize: '0.625rem', fontWeight: 800, color: 'var(--accent-gold)', textTransform: 'uppercase', letterSpacing: '0.06em', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                      ★ {item.priority}
                    </div>
                  )}

                  {/* Title / org */}
                  <div style={{ paddingRight: '1rem' }}>
                    <h3 style={{ fontSize: '1.125rem', fontWeight: 800, color: '#FFFFFF', lineHeight: 1.25 }}>{item.name}</h3>
                    {item.organization && (
                      <div style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>{item.organization}</div>
                    )}
                  </div>

                  {/* Badges: Category and License */}
                  <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                    <span style={{
                      display: 'inline-flex', padding: '0.2rem 0.6rem',
                      borderRadius: 'var(--radius-pill)',
                      backgroundColor: 'var(--bg-primary)',
                      border: '1px solid var(--border-subtle)',
                      fontSize: '0.6875rem', color: 'var(--text-muted)', fontWeight: 600,
                      textTransform: 'uppercase', letterSpacing: '0.04em',
                    }}>
                      {item.category.replace(/_/g, ' ')}
                    </span>
                    {item.license && (
                      <span style={{
                        display: 'inline-flex', padding: '0.2rem 0.6rem',
                        borderRadius: 'var(--radius-pill)',
                        backgroundColor: 'var(--bg-primary)',
                        border: '1px solid var(--border-subtle)',
                        fontSize: '0.6875rem', color: 'var(--text-muted)', fontWeight: 600,
                        textTransform: 'uppercase', letterSpacing: '0.04em',
                      }}>
                        {item.license}
                      </span>
                    )}
                  </div>

                  {/* Description */}
                  <p style={{ 
                    fontSize: '0.875rem', 
                    color: 'var(--text-secondary)', 
                    lineHeight: 1.55, 
                    flex: 1, 
                    whiteSpace: 'pre-wrap', 
                    wordBreak: 'break-word',
                    display: '-webkit-box',
                    WebkitLineClamp: 4,
                    WebkitBoxOrient: 'vertical',
                    overflow: 'hidden'
                  }}>
                    {item.description}
                  </p>

                  {/* Tags */}
                  {item.keyFeatures && item.keyFeatures.length > 0 && (
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem' }}>
                      {item.keyFeatures.slice(0, 4).map((f: string) => (
                        <span key={f} className="forge-chip">{f}</span>
                      ))}
                    </div>
                  )}

                  {/* Tertiary links */}
                  {(item.officialDocumentation || item.githubRepository || item.lastVerified) && (
                    <div style={{ display: 'flex', gap: '1rem', paddingTop: '0.875rem', borderTop: '1px solid var(--border-subtle)', marginTop: '0.25rem', alignItems: 'center', justifyContent: 'space-between' }}>
                      <div style={{ display: 'flex', gap: '1rem' }}>
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
                      {item.lastVerified && (
                        <span style={{ fontSize: '0.6875rem', color: 'var(--text-muted)' }}>Updated {item.lastVerified}</span>
                      )}
                    </div>
                  )}
                </motion.div>
              );
            })}
          </div>

          {/* ── Pagination ──────────────────────────────────── */}
          {registry.total_pages > 1 && (
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '1rem', marginTop: '2rem' }}>
              <button 
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className="forge-btn-icon"
                style={{ opacity: page === 1 ? 0.5 : 1, cursor: page === 1 ? 'not-allowed' : 'pointer' }}
              >
                <ChevronLeft size={20} />
              </button>
              <span style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>
                Page {page} of {registry.total_pages}
              </span>
              <button 
                onClick={() => setPage(p => Math.min(registry.total_pages, p + 1))}
                disabled={page === registry.total_pages}
                className="forge-btn-icon"
                style={{ opacity: page === registry.total_pages ? 0.5 : 1, cursor: page === registry.total_pages ? 'not-allowed' : 'pointer' }}
              >
                <ChevronRight size={20} />
              </button>
            </div>
          )}
        </>
      )}
    </motion.div>
  );
};
