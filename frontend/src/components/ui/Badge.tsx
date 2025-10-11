import React from 'react';
import clsx from 'clsx';
import { getBadgeColors, type ColorVariant } from '../../utils/colors';

export type BadgeSize = 'sm' | 'md' | 'lg';

export interface BadgeProps {
  children: React.ReactNode;
  variant?: ColorVariant;
  size?: BadgeSize;
  pill?: boolean;
  className?: string;
}

const sizeStyles: Record<BadgeSize, string> = {
  sm: 'px-2 py-0.5 text-xs',
  md: 'px-2.5 py-0.5 text-sm',
  lg: 'px-3 py-1 text-base',
};

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  pill = false,
  className = '',
}) => {
  return (
    <span
      className={clsx(
        'inline-flex items-center font-medium border transition-all duration-200',
        'hover:scale-105',
        pill ? 'rounded-full' : 'rounded',
        getBadgeColors(variant),
        sizeStyles[size],
        className
      )}
    >
      {children}
    </span>
  );
};

export default Badge;
