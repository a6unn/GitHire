import React from 'react';
import clsx from 'clsx';
import { getAvatarColor } from '../../utils/colors';

export type AvatarSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl';

export interface AvatarProps {
  src?: string;
  alt?: string;
  initials?: string;
  size?: AvatarSize;
  status?: 'online' | 'offline';
  className?: string;
}

const sizeStyles: Record<AvatarSize, string> = {
  xs: 'h-6 w-6 text-xs',
  sm: 'h-8 w-8 text-sm',
  md: 'h-10 w-10 text-base',
  lg: 'h-12 w-12 text-lg',
  xl: 'h-16 w-16 text-xl',
};

const statusSizeStyles: Record<AvatarSize, string> = {
  xs: 'h-1.5 w-1.5',
  sm: 'h-2 w-2',
  md: 'h-2.5 w-2.5',
  lg: 'h-3 w-3',
  xl: 'h-4 w-4',
};

export const Avatar: React.FC<AvatarProps> = ({
  src,
  alt = '',
  initials,
  size = 'md',
  status,
  className = '',
}) => {
  const [imageError, setImageError] = React.useState(false);

  const showInitials = !src || imageError;
  const displayInitials = initials || alt.slice(0, 2).toUpperCase();

  return (
    <div className={clsx('relative inline-block', className)}>
      <div
        className={clsx(
          'rounded-full flex items-center justify-center overflow-hidden',
          sizeStyles[size],
          showInitials && getAvatarColor(alt || initials || ''),
          showInitials && 'text-white font-medium'
        )}
      >
        {showInitials ? (
          <span>{displayInitials}</span>
        ) : (
          <img
            src={src}
            alt={alt}
            className="h-full w-full object-cover"
            onError={() => setImageError(true)}
          />
        )}
      </div>
      {status && (
        <span
          className={clsx(
            'absolute bottom-0 right-0 block rounded-full ring-2 ring-white',
            statusSizeStyles[size],
            status === 'online' ? 'bg-green-500' : 'bg-gray-400'
          )}
          aria-label={status}
        />
      )}
    </div>
  );
};

export default Avatar;
