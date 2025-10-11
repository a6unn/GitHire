import React from 'react';
import clsx from 'clsx';

export interface StatCardProps {
  label: string;
  value: string | number;
  icon?: React.ReactNode;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  variant?: 'default' | 'primary' | 'secondary' | 'accent';
  className?: string;
}

const variantStyles = {
  default: {
    container: 'bg-white border-gray-200',
    icon: 'text-gray-600 bg-gray-100',
    value: 'text-gray-900',
    label: 'text-gray-600',
  },
  primary: {
    container: 'bg-gradient-to-br from-primary-50 to-purple-50 border-primary-200',
    icon: 'text-primary-600 bg-primary-100',
    value: 'text-primary-900',
    label: 'text-primary-700',
  },
  secondary: {
    container: 'bg-gradient-to-br from-secondary-50 to-teal-50 border-secondary-200',
    icon: 'text-secondary-600 bg-secondary-100',
    value: 'text-secondary-900',
    label: 'text-secondary-700',
  },
  accent: {
    container: 'bg-gradient-to-br from-accent-50 to-orange-50 border-accent-200',
    icon: 'text-accent-600 bg-accent-100',
    value: 'text-accent-900',
    label: 'text-accent-700',
  },
};

export const StatCard: React.FC<StatCardProps> = ({
  label,
  value,
  icon,
  trend,
  variant = 'default',
  className,
}) => {
  const styles = variantStyles[variant];

  return (
    <div
      className={clsx(
        'rounded-lg border p-6 transition-all duration-200 hover-lift',
        styles.container,
        className
      )}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className={clsx('text-sm font-medium', styles.label)}>{label}</p>
          <p className={clsx('mt-2 text-3xl font-bold', styles.value)}>{value}</p>

          {trend && (
            <div className="mt-2 flex items-center gap-1">
              <span
                className={clsx(
                  'text-sm font-medium',
                  trend.isPositive ? 'text-green-600' : 'text-red-600'
                )}
              >
                {trend.isPositive ? '↑' : '↓'} {Math.abs(trend.value)}%
              </span>
              <span className="text-sm text-gray-500">vs last month</span>
            </div>
          )}
        </div>

        {icon && (
          <div className={clsx('p-3 rounded-lg transition-transform duration-200 hover:scale-110', styles.icon)}>
            {icon}
          </div>
        )}
      </div>
    </div>
  );
};

export default StatCard;
