import React from 'react';
import clsx from 'clsx';

export type SkeletonVariant = 'text' | 'circular' | 'rectangular';

export interface SkeletonProps {
  variant?: SkeletonVariant;
  width?: string | number;
  height?: string | number;
  className?: string;
}

const variantStyles: Record<SkeletonVariant, string> = {
  text: 'h-4 rounded',
  circular: 'rounded-full',
  rectangular: 'rounded-lg',
};

export const Skeleton: React.FC<SkeletonProps> = ({
  variant = 'text',
  width,
  height,
  className = '',
}) => {
  const style: React.CSSProperties = {};

  if (width) {
    style.width = typeof width === 'number' ? `${width}px` : width;
  }

  if (height) {
    style.height = typeof height === 'number' ? `${height}px` : height;
  } else if (variant === 'circular' && width) {
    // For circular, height should match width if not specified
    style.height = typeof width === 'number' ? `${width}px` : width;
  }

  return (
    <div
      className={clsx(
        'bg-gray-200 animate-pulse relative overflow-hidden',
        variantStyles[variant],
        !width && 'w-full',
        className
      )}
      style={style}
      aria-label="Loading..."
      role="status"
    >
      <div className="absolute inset-0 shimmer bg-shimmer" />
    </div>
  );
};

export default Skeleton;
