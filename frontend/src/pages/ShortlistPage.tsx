import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  ArrowLeftIcon,
  CheckCircleIcon,
  UserGroupIcon,
} from '@heroicons/react/24/outline';
import { projectsApi } from '../api/projects';
import { useToast } from '../contexts/ToastContext';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { EmptyState } from '../components/ui/EmptyState';
import { Skeleton } from '../components/ui/Skeleton';
import type { RankedCandidate } from '../types/pipeline';

export const ShortlistPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { showToast } = useToast();
  const [selectedCandidates, setSelectedCandidates] = useState<Set<string>>(new Set());

  const { data: project, isLoading } = useQuery({
    queryKey: ['project', projectId],
    queryFn: () => projectsApi.getProject(projectId!),
    enabled: !!projectId,
  });

  const shortlistMutation = useMutation({
    mutationFn: (candidateUsernames: string[]) =>
      projectsApi.shortlistCandidates(projectId!, candidateUsernames),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['project', projectId] });
      showToast('Candidates shortlisted successfully!', 'success');
      navigate(`/projects/${projectId}`);
    },
    onError: (error: any) => {
      console.error('Shortlist failed:', error);
      showToast(error.response?.data?.detail || 'Failed to shortlist candidates', 'error');
    },
  });

  const handleToggleCandidate = (username: string) => {
    const newSelected = new Set(selectedCandidates);
    if (newSelected.has(username)) {
      newSelected.delete(username);
    } else {
      newSelected.add(username);
    }
    setSelectedCandidates(newSelected);
  };

  const handleSelectAll = () => {
    if (rankedCandidates.length === selectedCandidates.size) {
      setSelectedCandidates(new Set());
    } else {
      setSelectedCandidates(new Set(rankedCandidates.map(c => c.github_username)));
    }
  };

  const handleShortlist = () => {
    if (selectedCandidates.size === 0) {
      showToast('Please select at least one candidate', 'error');
      return;
    }
    shortlistMutation.mutate(Array.from(selectedCandidates));
  };

  if (isLoading) {
    return (
      <div className="space-y-8 animate-fade-in">
        <Skeleton variant="rectangular" height="60px" />
        <Skeleton variant="rectangular" height="400px" />
      </div>
    );
  }

  if (!project) {
    return (
      <EmptyState
        icon={<UserGroupIcon className="h-12 w-12" />}
        title="Project Not Found"
        description="The project you're looking for doesn't exist or has been deleted."
        action={{
          label: 'Back to Projects',
          onClick: () => navigate('/projects'),
        }}
      />
    );
  }

  const rankedCandidates = (project.results_json?.ranked_candidates || []) as RankedCandidate[];

  if (rankedCandidates.length === 0) {
    return (
      <div className="space-y-8 animate-fade-in">
        <Button
          onClick={() => navigate(`/projects/${projectId}`)}
          variant="ghost"
          leftIcon={<ArrowLeftIcon className="h-4 w-4" />}
        >
          Back to Project
        </Button>

        <EmptyState
          icon={<UserGroupIcon className="h-12 w-12" />}
          title="No Ranked Candidates"
          description="This project doesn't have any ranked candidates yet. Please rank candidates first."
          action={{
            label: 'Back to Project',
            onClick: () => navigate(`/projects/${projectId}`),
          }}
        />
      </div>
    );
  }

  const sortedCandidates = [...rankedCandidates].sort((a, b) => a.rank - b.rank);

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Back Button */}
      <Button
        onClick={() => navigate(`/projects/${projectId}`)}
        variant="ghost"
        leftIcon={<ArrowLeftIcon className="h-4 w-4" />}
      >
        Back to Project
      </Button>

      {/* Header */}
      <Card variant="elevated" padding="lg">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Select Candidates to Shortlist
            </h1>
            <p className="text-gray-600">
              {project.name || project.job_title || 'Untitled Project'} • {rankedCandidates.length} ranked candidates
            </p>
          </div>

          <div className="flex gap-3">
            <Button
              onClick={handleSelectAll}
              variant="secondary"
              size="lg"
            >
              {selectedCandidates.size === rankedCandidates.length ? 'Deselect All' : 'Select All'}
            </Button>
            <Button
              onClick={handleShortlist}
              variant="primary"
              size="lg"
              leftIcon={<CheckCircleIcon className="h-5 w-5" />}
              isLoading={shortlistMutation.isPending}
              disabled={shortlistMutation.isPending || selectedCandidates.size === 0}
            >
              Shortlist {selectedCandidates.size > 0 ? `(${selectedCandidates.size})` : ''}
            </Button>
          </div>
        </div>
      </Card>

      {/* Candidates List with Checkboxes */}
      <div className="space-y-4">
        {sortedCandidates.map((candidate) => {
          const isSelected = selectedCandidates.has(candidate.github_username);
          const getScoreColor = (score: number) => {
            if (score >= 80) return 'text-green-600 bg-green-100';
            if (score >= 60) return 'text-yellow-600 bg-yellow-100';
            return 'text-orange-600 bg-orange-100';
          };

          return (
            <Card
              key={candidate.github_username}
              variant={isSelected ? 'elevated' : 'bordered'}
              padding="lg"
              className={`cursor-pointer transition-all ${
                isSelected ? 'ring-2 ring-primary-500 bg-primary-50' : 'hover:shadow-md'
              }`}
              onClick={() => handleToggleCandidate(candidate.github_username)}
            >
              <div className="flex items-start gap-4">
                {/* Checkbox */}
                <div className="flex items-center pt-1">
                  <input
                    type="checkbox"
                    checked={isSelected}
                    onChange={() => handleToggleCandidate(candidate.github_username)}
                    onClick={(e) => e.stopPropagation()}
                    className="h-5 w-5 rounded border-gray-300 text-primary-600 focus:ring-primary-500 cursor-pointer"
                  />
                </div>

                {/* Rank Badge */}
                <div className="flex-shrink-0">
                  <div className="w-12 h-12 rounded-full bg-primary-100 flex items-center justify-center">
                    <span className="text-xl font-bold text-primary-600">#{candidate.rank}</span>
                  </div>
                </div>

                {/* Candidate Info */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-4 mb-3">
                    <div>
                      <a
                        href={`https://github.com/${candidate.github_username}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-lg font-semibold text-gray-900 hover:text-primary-600"
                        onClick={(e) => e.stopPropagation()}
                      >
                        {candidate.github_username}
                      </a>
                      {candidate.name && (
                        <p className="text-sm text-gray-600">{candidate.name}</p>
                      )}
                    </div>

                    <div className="flex items-center gap-2">
                      <span className={`px-3 py-1 rounded-full text-sm font-semibold ${getScoreColor(candidate.score)}`}>
                        {Math.round(candidate.score)}%
                      </span>
                    </div>
                  </div>

                  {/* Bio */}
                  {candidate.bio && (
                    <p className="text-gray-600 mb-3 line-clamp-2">{candidate.bio}</p>
                  )}

                  {/* Stats */}
                  <div className="flex flex-wrap gap-4 text-sm text-gray-600">
                    {candidate.location && (
                      <div className="flex items-center gap-1">
                        <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                        </svg>
                        {candidate.location}
                      </div>
                    )}
                    {candidate.followers !== undefined && (
                      <div className="flex items-center gap-1">
                        <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                        </svg>
                        {candidate.followers} followers
                      </div>
                    )}
                    {candidate.public_repos !== undefined && (
                      <div className="flex items-center gap-1">
                        <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                        </svg>
                        {candidate.public_repos} repos
                      </div>
                    )}
                  </div>

                  {/* Skills */}
                  {candidate.matched_skills && candidate.matched_skills.length > 0 && (
                    <div className="mt-3 flex flex-wrap gap-2">
                      {candidate.matched_skills.slice(0, 5).map((skill) => (
                        <span
                          key={skill}
                          className="px-2 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded"
                        >
                          {skill}
                        </span>
                      ))}
                      {candidate.matched_skills.length > 5 && (
                        <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs font-medium rounded">
                          +{candidate.matched_skills.length - 5} more
                        </span>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </Card>
          );
        })}
      </div>

      {/* Fixed Bottom Bar */}
      {selectedCandidates.size > 0 && (
        <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 shadow-lg p-4 z-10">
          <div className="max-w-7xl mx-auto flex items-center justify-between">
            <div className="text-gray-900">
              <span className="font-semibold">{selectedCandidates.size}</span> candidate{selectedCandidates.size !== 1 ? 's' : ''} selected
            </div>
            <Button
              onClick={handleShortlist}
              variant="primary"
              size="lg"
              leftIcon={<CheckCircleIcon className="h-5 w-5" />}
              isLoading={shortlistMutation.isPending}
              disabled={shortlistMutation.isPending}
            >
              Shortlist {selectedCandidates.size} Candidate{selectedCandidates.size !== 1 ? 's' : ''}
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};
