import React from 'react';
import { Card } from '../ui/Card';
import { FunnelIcon } from '@heroicons/react/24/outline';

interface PipelineStage {
  name: string;
  count: number;
  color: string;
}

interface PipelineVisualizationProps {
  draftCount: number;
  sourcedCount: number;
  rankedCount: number;
  shortlistedCount: number;
}

export const PipelineVisualization: React.FC<PipelineVisualizationProps> = ({
  draftCount,
  sourcedCount,
  rankedCount,
  shortlistedCount,
}) => {
  const stages: PipelineStage[] = [
    { name: 'Draft', count: draftCount, color: 'bg-gray-400' },
    { name: 'Sourced', count: sourcedCount, color: 'bg-blue-400' },
    { name: 'Ranked', count: rankedCount, color: 'bg-purple-400' },
    { name: 'Shortlisted', count: shortlistedCount, color: 'bg-green-400' },
  ];

  const maxCount = Math.max(...stages.map(s => s.count), 1);

  return (
    <Card variant="elevated" padding="lg">
      <div className="flex items-center gap-2 mb-6">
        <FunnelIcon className="h-6 w-6 text-primary-600" />
        <h2 className="text-xl font-semibold text-gray-900">Recruiting Pipeline</h2>
      </div>

      <div className="space-y-4">
        {stages.map((stage, index) => {
          const widthPercent = maxCount > 0 ? (stage.count / maxCount) * 100 : 0;
          const isLast = index === stages.length - 1;

          return (
            <div key={stage.name} className="relative">
              {/* Stage Bar */}
              <div className="flex items-center gap-4">
                {/* Label */}
                <div className="w-28 flex-shrink-0">
                  <span className="text-sm font-medium text-gray-700">{stage.name}</span>
                </div>

                {/* Progress Bar Container */}
                <div className="flex-1 relative">
                  <div className="h-10 bg-gray-100 rounded-lg overflow-hidden border border-gray-200">
                    <div
                      className={`h-full ${stage.color} transition-all duration-500 ease-out flex items-center justify-end pr-3`}
                      style={{ width: `${Math.max(widthPercent, stage.count > 0 ? 10 : 0)}%` }}
                    >
                      {stage.count > 0 && (
                        <span className="text-white font-bold text-sm drop-shadow-md">
                          {stage.count}
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                {/* Count Badge */}
                <div className="w-12 flex-shrink-0 text-right">
                  <span className={`inline-flex items-center justify-center w-10 h-10 rounded-full text-sm font-bold ${stage.color} text-white`}>
                    {stage.count}
                  </span>
                </div>
              </div>

              {/* Connecting Arrow */}
              {!isLast && (
                <div className="ml-14 my-1">
                  <svg className="h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
                  </svg>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Summary */}
      <div className="mt-6 pt-6 border-t border-gray-200">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600">Total Active Projects</span>
          <span className="font-bold text-gray-900 text-lg">
            {draftCount + sourcedCount + rankedCount + shortlistedCount}
          </span>
        </div>
        {shortlistedCount > 0 && (
          <div className="mt-2 p-2 bg-green-50 rounded-md">
            <p className="text-xs text-green-700">
              🎉 <strong>{shortlistedCount}</strong> project{shortlistedCount !== 1 ? 's' : ''} ready for candidate outreach!
            </p>
          </div>
        )}
      </div>
    </Card>
  );
};
