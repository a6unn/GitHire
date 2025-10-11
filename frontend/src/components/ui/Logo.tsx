import React from 'react';
import { Link } from 'react-router-dom';
import clsx from 'clsx';

export type LogoVariant = 'full' | 'icon';
export type LogoSize = 'sm' | 'md' | 'lg';

export interface LogoProps {
  variant?: LogoVariant;
  size?: LogoSize;
  className?: string;
  linkTo?: string;
}

const sizeStyles: Record<LogoSize, { text: string; icon: string }> = {
  sm: { text: 'text-xl', icon: 'h-8 w-8' },
  md: { text: 'text-2xl', icon: 'h-10 w-10' },
  lg: { text: 'text-3xl', icon: 'h-12 w-12' },
};

const LogoIcon: React.FC<{ size: LogoSize }> = ({ size }) => (
  <img
    src="https://d7umqicpi7263.cloudfront.net/img/product/68229e91-9320-4898-a4a9-c4f66b69d941.com/3a03047938cb9f1c111f7ede48c3ed6b"
    alt="GitHire Logo"
    className={clsx(sizeStyles[size].icon, 'object-contain')}
  />
);

export const Logo: React.FC<LogoProps> = ({
  variant = 'full',
  size = 'md',
  className = '',
  linkTo = '/dashboard',
}) => {
  const content = (
    <div className={clsx('flex items-center gap-2', className)}>
      <LogoIcon size={size} />
      {variant === 'full' && (
        <span className={clsx('font-bold text-gradient-primary', sizeStyles[size].text)}>
          GitHire
        </span>
      )}
    </div>
  );

  if (linkTo) {
    return (
      <Link to={linkTo} className="inline-flex items-center">
        {content}
      </Link>
    );
  }

  return content;
};

export default Logo;
