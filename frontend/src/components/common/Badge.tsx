import React, { ReactNode } from 'react';

interface BadgeProps {
  children: ReactNode;
  variant?: 'green' | 'blue' | 'purple' | 'orange' | 'gold' | 'neutral';
  className?: string;
  style?: React.CSSProperties;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'neutral',
  className = '',
  style = {},
}) => {
  return (
    <span className={`forge-badge forge-badge-${variant} ${className}`} style={style}>
      {children}
    </span>
  );
};
