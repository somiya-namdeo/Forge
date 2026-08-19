import React from 'react';
import { motion } from 'framer-motion';

interface ScoreRingProps {
  score: number; // 0 - 100
  size?: number;
  strokeWidth?: number;
  label?: string;
}

export const ScoreRing: React.FC<ScoreRingProps> = ({
  score,
  size = 46,
  strokeWidth = 4,
}) => {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const clampedScore = Math.min(Math.max(score, 0), 100);
  const strokeDashoffset = circumference - (clampedScore / 100) * circumference;

  // Secondary Color Token Rules: Only use secondary colors for scores and status
  let strokeColor = 'var(--status-green)'; // >= 95
  if (clampedScore < 86) {
    strokeColor = 'var(--status-purple)';
  } else if (clampedScore < 90) {
    strokeColor = 'var(--status-blue)';
  } else if (clampedScore < 95) {
    strokeColor = '#f97316'; // orange/gold
  }

  return (
    <div style={{ 
      position: 'relative', 
      width: size, 
      height: size, 
      minWidth: size,
      minHeight: size,
      flexShrink: 0,
      display: 'inline-flex', 
      alignItems: 'center', 
      justifyContent: 'center',
      borderRadius: '50%',
      overflow: 'hidden'
    }}>
      <svg width={size} height={size} style={{ transform: 'rotate(-90deg)', display: 'block' }}>
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="rgba(255, 255, 255, 0.08)"
          strokeWidth={strokeWidth}
          fill="none"
        />
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={strokeColor}
          strokeWidth={strokeWidth}
          fill="none"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset }}
          transition={{ duration: 1, ease: 'easeOut', delay: 0.15 }}
          strokeLinecap="round"
        />
      </svg>
      <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: 'var(--font-heading)', fontSize: size < 30 ? '0.55rem' : (size < 50 ? '0.85rem' : '1.1rem'), fontWeight: 700, color: strokeColor }}>
        {Math.round(clampedScore)}
      </div>
    </div>
  );
};
