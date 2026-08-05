import React, { ReactNode } from 'react';
import { LucideIcon } from 'lucide-react';

interface ButtonProps {
  children: ReactNode;
  variant?: 'primary' | 'secondary' | 'ghost';
  icon?: LucideIcon;
  onClick?: () => void;
  disabled?: boolean;
  type?: 'button' | 'submit' | 'reset';
  className?: string;
  style?: React.CSSProperties;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  icon: Icon,
  onClick,
  disabled = false,
  type = 'button',
  className = '',
  style = {},
}) => {
  const btnClass = variant === 'primary' 
    ? 'forge-btn-primary' 
    : variant === 'secondary' 
    ? 'forge-btn-secondary' 
    : 'forge-btn-ghost';

  return (
    <button
      type={type}
      className={`${btnClass} ${className}`}
      onClick={onClick}
      disabled={disabled}
      style={style}
    >
      {Icon && <Icon size={16} />}
      {children}
    </button>
  );
};
