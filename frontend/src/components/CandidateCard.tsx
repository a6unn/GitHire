import React, { useState } from 'react';
import type { RankedCandidate, OutreachMessage } from '../types/pipeline';

interface CandidateCardProps {
  candidate: RankedCandidate;
  outreachMessage?: OutreachMessage;
  rank: number;
}

export const CandidateCard: React.FC<CandidateCardProps> = ({
  candidate,
  outreachMessage,
  rank,
}) => {
  const [copied, setCopied] = useState(false);

  const handleCopyMessage = async () => {
    if (!outreachMessage) return;

    try {
      await navigator.clipboard.writeText(outreachMessage.message);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Failed to copy:', error);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600 bg-green-100';
    if (score >= 60) return 'text-yellow-600 bg-yellow-100';
    return 'text-orange-600 bg-orange-100';
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="w-12 h-12 rounded-full bg-primary-100 flex items-center justify-center">
            <span className="text-xl font-bold text-primary-600">#{rank}</span>
          </div>
          <div>
            <a
              href={`https://github.com/${candidate.github_username}`}
              target="_blank"
              rel="noopener noreferrer"
              className="text-lg font-semibold text-gray-900 hover:text-primary-600"
            >
              {candidate.github_username}
            </a>
            <div className="flex items-center space-x-2 mt-1">
              <span
                className={`px-2 py-1 rounded text-sm font-medium ${getScoreColor(
                  candidate.total_score
                )}`}
              >
                {candidate.total_score.toFixed(1)} / 100
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Score Breakdown */}
      {Object.keys(candidate.score_breakdown).length > 0 && (
        <div className="mb-4">
          <p className="text-sm font-medium text-gray-700 mb-2">Score Breakdown:</p>
          <div className="space-y-1">
            {Object.entries(candidate.score_breakdown)
              .filter(([key, value]) => typeof value === 'number')
              .map(([key, value]) => (
                <div key={key} className="flex items-center justify-between text-sm">
                  <span className="text-gray-600 capitalize">{key.replace(/_/g, ' ')}:</span>
                  <span className="font-medium text-gray-900">{(value as number).toFixed(1)}</span>
                </div>
              ))}
          </div>
        </div>
      )}

      {/* Strengths */}
      {candidate.strengths && candidate.strengths.length > 0 && (
        <div className="mb-4">
          <p className="text-sm font-medium text-gray-700 mb-2">Strengths:</p>
          <div className="flex flex-wrap gap-2">
            {candidate.strengths.map((strength, index) => (
              <span
                key={index}
                className="px-2 py-1 bg-green-100 text-green-800 rounded text-xs"
              >
                {strength}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Concerns */}
      {candidate.concerns && candidate.concerns.length > 0 && (
        <div className="mb-4">
          <p className="text-sm font-medium text-gray-700 mb-2">Concerns:</p>
          <div className="flex flex-wrap gap-2">
            {candidate.concerns.map((concern, index) => (
              <span
                key={index}
                className="px-2 py-1 bg-yellow-100 text-yellow-800 rounded text-xs"
              >
                {concern}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Outreach Message */}
      {outreachMessage && (
        <div className="border-t pt-4">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm font-medium text-gray-700">Outreach Message:</p>
            <button
              onClick={handleCopyMessage}
              className="text-xs px-3 py-1 bg-primary-600 text-white rounded hover:bg-primary-700 transition-colors"
            >
              {copied ? 'Copied!' : 'Copy'}
            </button>
          </div>
          <div className="bg-gray-50 rounded p-3">
            <p className="text-sm font-medium text-gray-900 mb-1">
              {outreachMessage.subject}
            </p>
            <p className="text-sm text-gray-700 whitespace-pre-wrap">
              {outreachMessage.message}
            </p>
            {outreachMessage.personalization_notes && (
              <p className="text-xs text-gray-500 mt-2 italic">
                Personalization: {outreachMessage.personalization_notes}
              </p>
            )}
          </div>
        </div>
      )}

      {/* GitHub Link */}
      <div className="mt-4 pt-4 border-t">
        <a
          href={`https://github.com/${candidate.github_username}`}
          target="_blank"
          rel="noopener noreferrer"
          className="text-sm text-primary-600 hover:text-primary-700 font-medium"
        >
          View GitHub Profile →
        </a>
      </div>
    </div>
  );
};
