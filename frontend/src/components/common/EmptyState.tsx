import React from 'react';
import { motion } from 'framer-motion';
import { LucideIcon, Sparkles } from 'lucide-react';

interface EmptyStateProps {
  icon?: LucideIcon;
  title: string;
  description: string;
  actionText?: string;
  onAction?: () => void;
  loading?: boolean;
  compact?: boolean;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  icon: Icon = Sparkles,
  title,
  description,
  actionText,
  onAction,
  loading = false,
  compact = false,
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: 'easeOut' }}
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        textAlign: 'center',
        padding: compact ? '2rem 1.5rem' : '4rem 2rem',
        backgroundColor: 'var(--card-bg)',
        border: '1px dashed var(--border-subtle)',
        borderRadius: 'var(--radius-card)',
        margin: compact ? '0' : '1.5rem 0',
      }}
    >
      <div
        style={{
          width: '56px',
          height: '56px',
          borderRadius: '50%',
          backgroundColor: 'rgba(212, 175, 99, 0.08)',
          border: '1px solid var(--border-accent)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          marginBottom: '1.25rem',
          color: 'var(--accent-gold)',
          boxShadow: 'var(--shadow-glow-gold)',
        }}
      >
        <Icon size={26} />
      </div>
      <h3 style={{ fontSize: '1.25rem', marginBottom: '0.6rem', fontWeight: 600 }}>
        {title}
      </h3>
      <p style={{ maxWidth: '440px', fontSize: '0.95rem', marginBottom: actionText ? '1.75rem' : '0' }}>
        {description}
      </p>
      {actionText && onAction && (
        <button
          className="forge-btn-primary"
          onClick={onAction}
          disabled={loading}
          style={{ marginTop: '0.5rem' }}
        >
          <Sparkles size={16} />
          {loading ? 'Initializing Engine...' : actionText}
        </button>
      )}
    </motion.div>
  );
};
