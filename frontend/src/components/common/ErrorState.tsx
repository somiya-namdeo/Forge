import React from 'react';
import { motion } from 'framer-motion';
import { AlertCircle, RefreshCw } from 'lucide-react';

interface ErrorStateProps {
  title?: string;
  message: string;
  onRetry?: () => void;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  title = 'Execution Failure',
  message,
  onRetry,
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        textAlign: 'center',
        padding: '3rem 2rem',
        backgroundColor: 'rgba(239, 68, 68, 0.05)',
        border: '1px solid rgba(239, 68, 68, 0.25)',
        borderRadius: 'var(--radius-card)',
        margin: '1.5rem 0',
      }}
    >
      <div
        style={{
          width: '50px',
          height: '50px',
          borderRadius: '50%',
          backgroundColor: 'rgba(239, 68, 68, 0.12)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#ef4444',
          marginBottom: '1rem',
        }}
      >
        <AlertCircle size={24} />
      </div>
      <h3 style={{ fontSize: '1.2rem', marginBottom: '0.5rem', color: '#FFFFFF' }}>
        {title}
      </h3>
      <p style={{ maxWidth: '480px', fontSize: '0.95rem', color: 'var(--text-secondary)', marginBottom: onRetry ? '1.5rem' : '0' }}>
        {message}
      </p>
      {onRetry && (
        <button className="forge-btn-secondary" onClick={onRetry}>
          <RefreshCw size={16} />
          Retry Execution
        </button>
      )}
    </motion.div>
  );
};
