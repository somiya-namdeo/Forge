import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  BookOpen,
  Search,
  ExternalLink,
  Github,
  CheckCircle,
  Clock,
  Layers,
  Sparkles,
  Database,
  Cpu,
  ShieldCheck
} from 'lucide-react';
import { Card, Badge, Button, EmptyState, Skeleton } from '../components/common';
import { KnowledgeComponent, KnowledgeRegistryResponse, KnowledgeCategory } from '../types';
import { knowledgeService } from '../services';

export const KnowledgeBase: React.FC = () => {
  const [selectedCat, setSelectedCat] = useState<KnowledgeCategory | 'all'>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [registry, setRegistry] = useState<KnowledgeRegistryResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadRegistry() {
      setLoading(true);
      const res = await knowledgeService.getRegistry(selectedCat, searchQuery);
      setRegistry(res);
      setLoading(false);
    }
    loadRegistry();
  }, [selectedCat, searchQuery]);

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.35 }}
      style={{ display: 'flex', flexDirection: 'column', gap: '2.5rem' }}
    >
      {/* Header Bar */}
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1.5rem', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '1.5rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
            <Badge variant="gold">● CANONICAL COMPONENT REGISTRY</Badge>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Dynamically Synced against Verifiable Sources</span>
          </div>
          <h1 style={{ fontSize: '2.5rem', fontWeight: 800 }}>
            AI Component Knowledge Base
          </h1>
          <p style={{ fontSize: '1.05rem', color: 'var(--text-secondary)', maxWidth: '750px', marginTop: '0.4rem' }}>
            Browse verified foundation models, vector search databases, cross-encoders, and agent orchestration frameworks with real open source license and documentation attributions.
          </p>
        </div>

        {/* Dynamic Total Count Badge (Strict Policy: No Hardcoded "240+ components") */}
        {registry && (
          <Card style={{ padding: '1rem 1.5rem', backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--border-accent)', display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <ShieldCheck size={32} style={{ color: 'var(--accent-gold)' }} />
            <div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>Verified Registry Count</div>
              <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#FFFFFF' }}>{registry.totalComponents} Active Components</div>
            </div>
          </Card>
        )}
      </header>

      {/* Filter Tabs & Search Bar */}
      <section style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1.5rem' }}>
        {/* Category Pill Tabs */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.6rem' }}>
          <button
            type="button"
            onClick={() => setSelectedCat('all')}
            style={{
              padding: '0.55rem 1.25rem',
              borderRadius: 'var(--radius-pill)',
              fontSize: '0.9rem',
              fontWeight: selectedCat === 'all' ? 700 : 500,
              backgroundColor: selectedCat === 'all' ? 'var(--accent-gold)' : 'var(--bg-secondary)',
              color: selectedCat === 'all' ? '#0B0D12' : 'var(--text-secondary)',
              border: selectedCat === 'all' ? 'none' : '1px solid var(--border-subtle)',
              cursor: 'pointer',
              transition: 'all 0.2s',
            }}
          >
            All Components
          </button>
          {registry?.categories.map(c => {
            const active = selectedCat === c.name;
            return (
              <button
                key={c.name}
                type="button"
                onClick={() => setSelectedCat(c.name)}
                style={{
                  padding: '0.55rem 1.25rem',
                  borderRadius: 'var(--radius-pill)',
                  fontSize: '0.9rem',
                  fontWeight: active ? 700 : 500,
                  backgroundColor: active ? 'var(--accent-gold)' : 'var(--bg-secondary)',
                  color: active ? '#0B0D12' : 'var(--text-secondary)',
                  border: active ? 'none' : '1px solid var(--border-subtle)',
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                }}
              >
                <span>{c.label}</span>
                <span style={{ fontSize: '0.78rem', opacity: 0.8, backgroundColor: 'rgba(0,0,0,0.15)', padding: '0.1rem 0.5rem', borderRadius: '8px' }}>
                  {c.count}
                </span>
              </button>
            );
          })}
        </div>

        {/* Search Input */}
        <div style={{ position: 'relative', width: '320px', maxWidth: '100%' }}>
          <Search size={18} style={{ position: 'absolute', left: '14px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search verified components..."
            style={{
              width: '100%',
              padding: '0.75rem 1rem 0.75rem 2.6rem',
              borderRadius: '12px',
              backgroundColor: 'var(--bg-secondary)',
              border: '1px solid var(--border-hover)',
              color: '#FFFFFF',
              fontSize: '0.92rem',
              outline: 'none',
            }}
          />
        </div>
      </section>

      {/* Component Registry Grid */}
      {loading ? (
        <div className="grid-3col">
          <Skeleton variant="card" height={260} />
          <Skeleton variant="card" height={260} />
          <Skeleton variant="card" height={260} />
        </div>
      ) : !registry || registry.components.length === 0 ? (
        <EmptyState
          icon={BookOpen}
          title="No Matching Components Found"
          description="We couldn't find any verifiable components matching your category filter or search term."
          actionText="Reset Filters"
          onAction={() => { setSelectedCat('all'); setSearchQuery(''); }}
        />
      ) : (
        <div className="grid-3col" style={{ gap: '1.6rem' }}>
          {registry.components.map((item, idx) => (
            <Card
              key={item.id}
              interactive
              delay={idx * 0.05}
              style={{ padding: '1.75rem', display: 'flex', flexDirection: 'column', gap: '1.2rem', height: '100%' }}
            >
              {/* Card Header */}
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
                  <span style={{ fontSize: '0.75rem', color: 'var(--accent-gold)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                    {item.category}
                  </span>
                  <Badge variant={item.priority === 'high' ? 'green' : 'neutral'} style={{ fontSize: '0.7rem' }}>
                    ✔ VERIFIED {item.lastVerified}
                  </Badge>
                </div>
                <h3 style={{ fontSize: '1.3rem', fontWeight: 800, color: '#FFFFFF' }}>
                  {item.name}
                </h3>
                <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginTop: '0.15rem' }}>
                  By <strong>{item.organization}</strong> · License: <strong>{item.license}</strong>
                </div>
              </div>

              {/* Description */}
              <p style={{ fontSize: '0.92rem', color: 'var(--text-secondary)', lineHeight: 1.5, flex: 1 }}>
                {item.description}
              </p>

              {/* Key Features Chips */}
              {item.keyFeatures && (
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
                  {item.keyFeatures.map(feat => (
                    <span key={feat} style={{ fontSize: '0.75rem', padding: '0.25rem 0.6rem', backgroundColor: 'rgba(255,255,255,0.05)', borderRadius: '6px', color: 'var(--text-primary)' }}>
                      • {feat}
                    </span>
                  ))}
                </div>
              )}

              {/* Action Buttons to external docs */}
              <div style={{ display: 'flex', gap: '0.75rem', paddingTop: '0.8rem', borderTop: '1px solid var(--border-subtle)' }}>
                {item.officialDocumentation && (
                  <a
                    href={item.officialDocumentation}
                    target="_blank"
                    rel="noreferrer"
                    style={{ flex: 1, textDecoration: 'none' }}
                  >
                    <button className="forge-btn-secondary" style={{ width: '100%', fontSize: '0.82rem', padding: '0.55rem' }}>
                      <ExternalLink size={14} /> Official Docs
                    </button>
                  </a>
                )}
                {item.githubRepository && (
                  <a
                    href={item.githubRepository}
                    target="_blank"
                    rel="noreferrer"
                    style={{ textDecoration: 'none' }}
                  >
                    <button className="forge-btn-ghost" title="GitHub Repository" style={{ padding: '0.6rem 0.8rem', backgroundColor: 'rgba(255,255,255,0.06)' }}>
                      <Github size={16} />
                    </button>
                  </a>
                )}
              </div>
            </Card>
          ))}
        </div>
      )}
    </motion.div>
  );
};
