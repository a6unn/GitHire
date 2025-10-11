import React from 'react';

interface PipelineStage {
  name: string;
  label: string;
}

const PIPELINE_STAGES: PipelineStage[] = [
  { name: 'parsing', label: 'Parsing Job Description' },
  { name: 'searching', label: 'Searching GitHub' },
  { name: 'ranking', label: 'Ranking Candidates' },
  { name: 'outreach', label: 'Generating Outreach' },
];

interface PipelineProgressProps {
  currentStage?: string | null;
  progressPercentage: number;
  status: 'running' | 'completed' | 'failed';
  startedAt?: string | null;
}

export const PipelineProgress: React.FC<PipelineProgressProps> = ({
  currentStage,
  progressPercentage,
  status,
  startedAt,
}) => {
  const getCurrentStageIndex = () => {
    if (!currentStage) return -1;
    return PIPELINE_STAGES.findIndex((stage) =>
      currentStage.toLowerCase().includes(stage.name)
    );
  };

  const currentStageIndex = getCurrentStageIndex();

  const getStageStatus = (index: number): 'completed' | 'current' | 'pending' => {
    if (status === 'completed') return 'completed';
    if (index < currentStageIndex) return 'completed';
    if (index === currentStageIndex) return 'current';
    return 'pending';
  };

  const formatElapsedTime = () => {
    if (!startedAt) return null;
    const start = new Date(startedAt).getTime();
    const now = Date.now();
    const elapsed = Math.floor((now - start) / 1000);

    if (elapsed < 60) return `${elapsed}s`;
    const minutes = Math.floor(elapsed / 60);
    const seconds = elapsed % 60;
    return `${minutes}m ${seconds}s`;
  };

  return (
    <div className="w-full bg-white rounded-lg shadow p-6">
      <div className="mb-6">
        <div className="flex justify-between items-center mb-2">
          <h3 className="text-lg font-semibold text-gray-900">
            {status === 'running' && 'Pipeline Running...'}
            {status === 'completed' && 'Pipeline Completed'}
            {status === 'failed' && 'Pipeline Failed'}
          </h3>
          {startedAt && (
            <span className="text-sm text-gray-600">
              Elapsed: {formatElapsedTime()}
            </span>
          )}
        </div>

        {/* Progress Bar */}
        <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
          <div
            className={`h-full transition-all duration-500 ${
              status === 'failed'
                ? 'bg-red-500'
                : status === 'completed'
                ? 'bg-green-500'
                : 'bg-primary-500'
            }`}
            style={{ width: `${progressPercentage}%` }}
          />
        </div>
        <div className="mt-1 text-right text-sm text-gray-600">
          {progressPercentage}%
        </div>
      </div>

      {/* Stages */}
      <div className="space-y-4">
        {PIPELINE_STAGES.map((stage, index) => {
          const stageStatus = getStageStatus(index);

          return (
            <div key={stage.name} className="flex items-start">
              <div className="flex-shrink-0 mr-4">
                {stageStatus === 'completed' && (
                  <div className="w-8 h-8 rounded-full bg-green-500 flex items-center justify-center">
                    <svg
                      className="w-5 h-5 text-white"
                      fill="none"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                )}
                {stageStatus === 'current' && (
                  <div className="w-8 h-8 rounded-full bg-primary-500 flex items-center justify-center">
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  </div>
                )}
                {stageStatus === 'pending' && (
                  <div className="w-8 h-8 rounded-full bg-gray-300 flex items-center justify-center">
                    <div className="w-3 h-3 rounded-full bg-white" />
                  </div>
                )}
              </div>
              <div className="flex-grow">
                <p
                  className={`text-sm font-medium ${
                    stageStatus === 'current'
                      ? 'text-primary-600'
                      : stageStatus === 'completed'
                      ? 'text-green-600'
                      : 'text-gray-500'
                  }`}
                >
                  {stage.label}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
