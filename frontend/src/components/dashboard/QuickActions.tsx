import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  SparklesIcon,
  EnvelopeIcon,
  ChartBarIcon,
  RocketLaunchIcon,
  ArrowRightIcon,
} from '@heroicons/react/24/outline';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';

interface QuickAction {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  count?: number;
  color: 'blue' | 'green' | 'purple' | 'orange';
  action: () => void;
}

interface QuickActionsProps {
  readyToContactCount: number;
  needsRankingCount: number;
  onNavigate: (path: string) => void;
  onCreateProject: () => void;
}

export const QuickActions: React.FC<QuickActionsProps> = ({
  readyToContactCount,
  needsRankingCount,
  onNavigate,
  onCreateProject,
}) => {
  const actions: QuickAction[] = [
    {
      id: 'ready_contact',
      title: 'Ready to Contact',
      description: 'Generate outreach for shortlisted candidates',
      icon: <EnvelopeIcon className="h-5 w-5" />,
      count: readyToContactCount,
      color: 'green',
      action: () => onNavigate('/projects?filter=ready_to_contact'),
    },
    {
      id: 'needs_ranking',
      title: 'Needs Ranking',
      description: 'Rank candidates to identify top talent',
      icon: <ChartBarIcon className="h-5 w-5" />,
      count: needsRankingCount,
      color: 'blue',
      action: () => onNavigate('/projects?filter=in_progress'),
    },
    {
      id: 'new_project',
      title: 'Start New Search',
      description: 'Create a project to find developers',
      icon: <RocketLaunchIcon className="h-5 w-5" />,
      color: 'purple',
      action: onCreateProject,
    },
  ];

  const getColorClasses = (color: string) => {
    const colors = {
      blue: {
        bg: 'bg-blue-50 hover:bg-blue-100',
        border: 'border-blue-200 hover:border-blue-300',
        icon: 'text-blue-600',
        badge: 'bg-blue-100 text-blue-700',
      },
      green: {
        bg: 'bg-green-50 hover:bg-green-100',
        border: 'border-green-200 hover:border-green-300',
        icon: 'text-green-600',
        badge: 'bg-green-100 text-green-700',
      },
      purple: {
        bg: 'bg-purple-50 hover:bg-purple-100',
        border: 'border-purple-200 hover:border-purple-300',
        icon: 'text-purple-600',
        badge: 'bg-purple-100 text-purple-700',
      },
      orange: {
        bg: 'bg-orange-50 hover:bg-orange-100',
        border: 'border-orange-200 hover:border-orange-300',
        icon: 'text-orange-600',
        badge: 'bg-orange-100 text-orange-700',
      },
    };
    return colors[color as keyof typeof colors];
  };

  return (
    <Card variant="elevated" padding="lg">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <SparklesIcon className="h-6 w-6 text-primary-600" />
          <h2 className="text-xl font-semibold text-gray-900">Quick Actions</h2>
        </div>
        <Badge variant="default" size="sm">
          What's Next?
        </Badge>
      </div>

      <div className="space-y-3">
        {actions.map((action) => {
          const colors = getColorClasses(action.color);
          return (
            <button
              key={action.id}
              onClick={action.action}
              className={`
                w-full group relative overflow-hidden rounded-lg border-2 p-4 text-left
                transition-all duration-200 transform hover:scale-[1.02] hover:shadow-md
                ${colors.bg} ${colors.border}
              `}
            >
              <div className="flex items-center gap-4">
                {/* Icon */}
                <div className={`flex-shrink-0 p-2 rounded-lg ${colors.icon}`}>
                  {action.icon}
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <h3 className="font-semibold text-gray-900">{action.title}</h3>
                    {action.count !== undefined && action.count > 0 && (
                      <span className={`px-2 py-0.5 rounded-full text-xs font-bold ${colors.badge}`}>
                        {action.count}
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-gray-600 mt-0.5">{action.description}</p>
                </div>

                {/* Arrow */}
                <div className="flex-shrink-0 text-gray-400 group-hover:text-gray-600 transition-transform group-hover:translate-x-1">
                  <ArrowRightIcon className="h-5 w-5" />
                </div>
              </div>

              {/* Animated background */}
              <div className="absolute inset-0 bg-gradient-to-r from-transparent to-white/20 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-700"></div>
            </button>
          );
        })}
      </div>

      {/* Tip */}
      <div className="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
        <p className="text-xs text-blue-700">
          💡 <strong>Tip:</strong> Focus on "Ready to Contact" projects first - they're waiting for your outreach!
        </p>
      </div>
    </Card>
  );
};
