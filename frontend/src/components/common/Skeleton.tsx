import React from 'react';

interface SkeletonProps {
  height?: string | number;
  width?: string | number;
  borderRadius?: string | number;
  variant?: 'card' | 'text' | 'title' | 'avatar' | 'chart';
  className?: string;
}

export const Skeleton: React.FC<SkeletonProps> = ({
  height,
  width = '100%',
  borderRadius,
  variant = 'text',
  className = '',
}) => {
  let defaultHeight: string | number = '1rem';
  let defaultRadius: string | number = 'var(--radius-sm)';

  if (variant === 'card') {
    defaultHeight = '220px';
    defaultRadius = 'var(--radius-card)';
  } else if (variant === 'title') {
    defaultHeight = '2rem';
    defaultRadius = 'var(--radius-sm)';
  } else if (variant === 'avatar') {
    defaultHeight = '40px';
    width = '40px';
    defaultRadius = '50%';
  } else if (variant === 'chart') {
    defaultHeight = '320px';
    defaultRadius = 'var(--radius-md)';
  }

  const style: React.CSSProperties = {
    height: height || defaultHeight,
    width: typeof width === 'number' ? `${width}px` : width,
    borderRadius: borderRadius || defaultRadius,
  };

  return <div className={`animate-shimmer ${className}`} style={style} />;
};
