import React from 'react';
import { motion } from 'framer-motion';
import { Loader2 } from 'lucide-react';

interface LoadingIndicatorProps {
  label?: string;
  size?: number;
  fullScreen?: boolean;
}

export const LoadingIndicator: React.FC<LoadingIndicatorProps> = ({
  label = 'Processing Engineering Data...',
  size = 32,
  fullScreen = false,
}) => {
  const content = (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem', textAlign: 'center' }}>
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ repeat: Infinity, duration: 1, ease: 'linear' }}
        style={{ color: 'var(--accent-gold)' }}
      >
        <Loader2 size={size} />
      </motion.div>
      {label && (
        <p style={{ fontSize: '0.95rem', fontWeight: 500, color: 'var(--text-secondary)' }}>
          {label}
        </p>
      )}
    </div>
  );

  if (fullScreen) {
    return (
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '400px',
          width: '100%',
          padding: '3rem',
        }}
      >
        {content}
      </div>
    );
  }

  return (
    <div style={{ padding: '2rem 0', display: 'flex', justifyContent: 'center' }}>
      {content}
    </div>
  );
};
