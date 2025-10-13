import React from 'react';
import { Link } from 'react-router-dom';
import { CalendarIcon, UserGroupIcon, ChartBarIcon } from '@heroicons/react/24/outline';
import { Badge } from './Badge';
import { Card } from './Card';
import clsx from 'clsx';

export interface ProjectCardProps {
  id: string;
  title: string;
  description?: string;
  status: 'active' | 'completed' | 'draft';
  createdAt: string;
  candidatesCount?: number;
  avgScore?: number;
  onClick?: () => void;
  className?: string;
}

const statusConfig: Record<string, { variant: 'success' | 'default' | 'warning' | 'danger', label: string }> = {
  active: { variant: 'success', label: 'Active' },
  completed: { variant: 'success', label: 'Completed' },
  draft: { variant: 'warning', label: 'Draft' },
  running: { variant: 'warning', label: 'Running' },
  pending: { variant: 'default', label: 'Pending' },
  failed: { variant: 'danger', label: 'Failed' },
};

export const ProjectCard: React.FC<ProjectCardProps> = ({
  id,
  title,
  description,
  status,
  createdAt,
  candidatesCount,
  avgScore,
  onClick,
  className,
}) => {
  const statusInfo = statusConfig[status] || { variant: 'default' as const, label: status.charAt(0).toUpperCase() + status.slice(1) };
  const formattedDate = new Date(createdAt).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });

  const cardContent = (
    <Card variant="interactive" padding="lg" className="h-full">
      <div className="flex flex-col h-full">
        {/* Header */}
        <div className="flex items-start justify-between gap-3 mb-3">
          <h3 className="text-lg font-semibold text-gray-900 flex-1 line-clamp-2">
            {title}
          </h3>
          <Badge variant={statusInfo.variant} size="sm" pill>
            {statusInfo.label}
          </Badge>
        </div>

        {/* Description */}
        {description && (
          <p className="text-sm text-gray-600 mb-4 line-clamp-2">
            {description}
          </p>
        )}

        {/* Stats */}
        <div className="mt-auto space-y-2">
          <div className="flex flex-wrap gap-4 text-sm text-gray-500">
            <div className="flex items-center gap-1">
              <CalendarIcon className="h-4 w-4" />
              <span>{formattedDate}</span>
            </div>

            {candidatesCount !== undefined && (
              <div className="flex items-center gap-1">
                <UserGroupIcon className="h-4 w-4" />
                <span>{candidatesCount} candidates</span>
              </div>
            )}

            {avgScore !== undefined && avgScore !== null && (
              <div className="flex items-center gap-1">
                <ChartBarIcon className="h-4 w-4" />
                <span>Avg: {avgScore}%</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </Card>
  );

  if (onClick) {
    return (
      <button
        onClick={onClick}
        type="button"
        className={clsx(
          'block w-full text-left cursor-pointer',
          className
        )}
      >
        {cardContent}
      </button>
    );
  }

  return (
    <Link
      to={`/projects/${id}`}
      className={clsx('block w-full text-left', className)}
    >
      {cardContent}
    </Link>
  );
};

export default ProjectCard;
