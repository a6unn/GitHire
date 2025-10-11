import React from 'react';
import { CheckCircleIcon, XCircleIcon, ClockIcon } from '@heroicons/react/24/outline';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';
import clsx from 'clsx';

export interface TimelineItem {
  id: string;
  title: string;
  description?: string;
  timestamp: string;
  status: 'completed' | 'failed' | 'pending';
}

export interface ActivityTimelineProps {
  items: TimelineItem[];
  className?: string;
}

const statusConfig = {
  completed: {
    icon: CheckCircleIcon,
    color: 'text-green-600',
    bgColor: 'bg-green-100',
    badge: 'success' as const,
  },
  failed: {
    icon: XCircleIcon,
    color: 'text-red-600',
    bgColor: 'bg-red-100',
    badge: 'danger' as const,
  },
  pending: {
    icon: ClockIcon,
    color: 'text-gray-600',
    bgColor: 'bg-gray-100',
    badge: 'default' as const,
  },
};

export const ActivityTimeline: React.FC<ActivityTimelineProps> = ({ items, className }) => {
  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;

    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  return (
    <Card variant="elevated" padding="lg" className={className}>
      <h3 className="text-lg font-semibold text-gray-900 mb-6">Recent Activity</h3>
      <div className="space-y-4">
        {items.length === 0 ? (
          <p className="text-sm text-gray-500 text-center py-8">No recent activity</p>
        ) : (
          items.map((item, index) => {
            const config = statusConfig[item.status];
            const Icon = config.icon;
            const isLast = index === items.length - 1;

            return (
              <div key={item.id} className="relative flex gap-4">
                {/* Timeline line */}
                {!isLast && (
                  <div className="absolute left-5 top-11 bottom-0 w-0.5 bg-gray-200" />
                )}

                {/* Icon */}
                <div className={clsx('relative flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center', config.bgColor)}>
                  <Icon className={clsx('h-5 w-5', config.color)} />
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0 pb-4">
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-900">{item.title}</p>
                      {item.description && (
                        <p className="text-sm text-gray-600 mt-1">{item.description}</p>
                      )}
                    </div>
                    <Badge variant={config.badge} size="sm">
                      {item.status}
                    </Badge>
                  </div>
                  <p className="text-xs text-gray-500 mt-2">{formatTime(item.timestamp)}</p>
                </div>
              </div>
            );
          })
        )}
      </div>
    </Card>
  );
};

export default ActivityTimeline;
