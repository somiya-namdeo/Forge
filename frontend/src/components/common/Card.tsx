import React, { ReactNode } from 'react';
import { motion } from 'framer-motion';

interface CardProps {
  children: ReactNode;
  interactive?: boolean;
  accentBorder?: boolean;
  className?: string;
  style?: React.CSSProperties;
  onClick?: () => void;
  delay?: number;
}

export const Card: React.FC<CardProps> = ({
  children,
  interactive = false,
  accentBorder = false,
  className = '',
  style = {},
  onClick,
  delay = 0,
}) => {
  const baseClasses = `forge-card ${interactive ? 'forge-card-interactive' : ''} ${accentBorder ? 'forge-card-accent-border' : ''} ${className}`;

  return (
    <motion.div
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: 'easeOut', delay }}
      className={baseClasses}
      style={{ ...style, cursor: onClick || interactive ? 'pointer' : 'default' }}
      onClick={onClick}
    >
      {children}
    </motion.div>
  );
};
