import React from 'react';
import { motion } from 'framer-motion';

interface ProgressBarProps {
  value: number; // 0 - 100
  label?: string;
  showPercentage?: boolean;
  color?: 'green' | 'blue' | 'purple' | 'orange' | 'gold' | 'auto';
  height?: number;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  value,
  label,
  showPercentage = true,
  color = 'auto',
  height = 8,
}) => {
  const clamped = Math.min(Math.max(value, 0), 100);

  let barColor = 'var(--accent-gold)';
  if (color === 'green' || (color === 'auto' && clamped >= 93)) barColor = 'var(--status-green)';
  else if (color === 'orange' || (color === 'auto' && clamped >= 88 && clamped < 93)) barColor = '#f97316';
  else if (color === 'blue' || (color === 'auto' && clamped >= 80 && clamped < 88)) barColor = 'var(--status-blue)';
  else if (color === 'purple' || (color === 'auto' && clamped < 80)) barColor = 'var(--status-purple)';
  else if (color === 'gold') barColor = 'var(--accent-gold)';

  return (
    <div style={{ width: '100%' }}>
      {(label || showPercentage) && (
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.45rem', fontSize: '0.85rem' }}>
          {label && <span style={{ color: 'var(--text-secondary)', fontWeight: 500 }}>{label}</span>}
          {showPercentage && <span style={{ fontFamily: 'var(--font-heading)', fontWeight: 600, color: 'var(--text-primary)' }}>{Math.round(clamped)}%</span>}
        </div>
      )}
      <div style={{ width: '100%', height: `${height}px`, backgroundColor: 'rgba(255, 255, 255, 0.06)', borderRadius: 'var(--radius-pill)', overflow: 'hidden' }}>
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${clamped}%` }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
          style={{ height: '100%', backgroundColor: barColor, borderRadius: 'var(--radius-pill)' }}
        />
      </div>
    </div>
  );
};
