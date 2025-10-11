import React, { useState } from 'react';
import { ChevronDownIcon, ChevronUpIcon, InformationCircleIcon } from '@heroicons/react/24/outline';
import { ArrowTopRightOnSquareIcon } from '@heroicons/react/20/solid';
import type { RankedCandidate, OutreachMessage } from '../types/pipeline';

interface ResultsListProps {
  candidates: RankedCandidate[];
  outreachMessages: OutreachMessage[];
  projectId: string;
  shortlistedUsernames: Set<string>;
  onToggleShortlist: (username: string) => Promise<void>;
}

export const ResultsList: React.FC<ResultsListProps> = ({
  candidates,
  outreachMessages,
  projectId,
  shortlistedUsernames,
  onToggleShortlist,
}) => {
  const [sortField, setSortField] = useState<'rank' | 'total_score'>('rank');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');
  const [togglingUsername, setTogglingUsername] = useState<string | null>(null);

  if (candidates.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-8 text-center">
        <div className="max-w-md mx-auto">
          <svg
            className="mx-auto h-12 w-12 text-gray-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <h3 className="mt-4 text-lg font-medium text-gray-900">
            No Candidates Found
          </h3>
          <p className="mt-2 text-sm text-gray-600">
            The pipeline didn't find any candidates matching your job description.
            Try broadening your requirements or using different keywords.
          </p>
        </div>
      </div>
    );
  }

  // Sort candidates
  const sortedCandidates = [...candidates].sort((a, b) => {
    const aVal = a[sortField];
    const bVal = b[sortField];
    return sortDirection === 'asc' ? aVal - bVal : bVal - aVal;
  });

  const handleSort = (field: 'rank' | 'total_score') => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const handleToggleShortlist = async (username: string) => {
    setTogglingUsername(username);
    try {
      await onToggleShortlist(username);
    } finally {
      setTogglingUsername(null);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'bg-green-50 text-green-700';
    if (score >= 60) return 'bg-blue-50 text-blue-700';
    if (score >= 40) return 'bg-yellow-50 text-yellow-700';
    return 'bg-orange-50 text-orange-700';
  };

  const SortIcon = ({ field }: { field: 'rank' | 'total_score' }) => {
    if (sortField !== field) return null;
    return sortDirection === 'asc' ? (
      <ChevronUpIcon className="h-4 w-4" />
    ) : (
      <ChevronDownIcon className="h-4 w-4" />
    );
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">
          Top Candidates ({candidates.length})
        </h2>
      </div>

      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Name
                </th>
                <th
                  scope="col"
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  onClick={() => handleSort('total_score')}
                >
                  <div className="flex items-center gap-1">
                    Match %
                    <SortIcon field="total_score" />
                  </div>
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Matched Skills
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Strengths
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Shortlist
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {sortedCandidates.map((candidate) => {
                const isShortlisted = shortlistedUsernames.has(candidate.github_username);
                const isToggling = togglingUsername === candidate.github_username;

                return (
                  <tr key={candidate.github_username} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center gap-2">
                        <div className="flex-1">
                          <a
                            href={`https://github.com/${candidate.github_username}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-sm font-medium text-primary-600 hover:text-primary-800 flex items-center gap-1"
                          >
                            {candidate.github_username}
                            <ArrowTopRightOnSquareIcon className="h-3.5 w-3.5" />
                          </a>
                          <div className="text-xs text-gray-500">
                            Rank #{candidate.rank}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center gap-1.5">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-md text-sm font-semibold ${getScoreColor(candidate.total_score)}`}>
                          {Math.round(candidate.total_score)}%
                        </span>
                        <div className="group relative">
                          <InformationCircleIcon className="h-4 w-4 text-gray-400 cursor-help" />
                          <div className="invisible group-hover:visible absolute z-10 w-48 p-2 mt-1 text-xs bg-gray-900 text-white rounded shadow-lg -left-20">
                            <div className="space-y-1">
                              <div>Skill Match: {candidate.score_breakdown.skill_match ? `${Math.round(candidate.score_breakdown.skill_match)}%` : 'N/A'}</div>
                              <div>Experience: {candidate.score_breakdown.experience ? `${Math.round(candidate.score_breakdown.experience)}%` : 'N/A'}</div>
                              <div>Activity: {candidate.score_breakdown.activity ? `${Math.round(candidate.score_breakdown.activity)}%` : 'N/A'}</div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex flex-wrap gap-1">
                        {candidate.score_breakdown.matched_skills && candidate.score_breakdown.matched_skills.length > 0 ? (
                          <>
                            {/* Deduplicate skills and show first 3 */}
                            {Array.from(new Set(candidate.score_breakdown.matched_skills)).slice(0, 3).map((skill) => (
                              <span
                                key={skill}
                                className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800"
                              >
                                {skill}
                              </span>
                            ))}
                            {Array.from(new Set(candidate.score_breakdown.matched_skills)).length > 3 && (
                              <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-600">
                                +{Array.from(new Set(candidate.score_breakdown.matched_skills)).length - 3} more
                              </span>
                            )}
                          </>
                        ) : (
                          <span className="text-sm text-gray-400">No skills detected</span>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex flex-wrap gap-1">
                        {candidate.strengths && candidate.strengths.length > 0 ? (
                          <>
                            {/* Show all strengths since they're valuable info */}
                            {candidate.strengths.map((strength, idx) => (
                              <span
                                key={idx}
                                className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800"
                              >
                                {strength}
                              </span>
                            ))}
                          </>
                        ) : (
                          <span className="text-sm text-gray-400">-</span>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <button
                        onClick={() => handleToggleShortlist(candidate.github_username)}
                        disabled={isToggling}
                        className={`px-3 py-1 text-sm font-medium rounded-md transition-colors ${
                          isShortlisted
                            ? 'bg-purple-100 text-purple-700 hover:bg-purple-200'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        } disabled:opacity-50 disabled:cursor-not-allowed`}
                      >
                        {isToggling ? 'Loading...' : isShortlisted ? 'Unshortlist' : 'Shortlist'}
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
