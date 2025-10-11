import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  ArrowLeftIcon,
  ArrowDownTrayIcon,
  TrashIcon,
  ClockIcon,
  UserGroupIcon,
  ChartBarIcon,
  CalendarIcon,
  FolderOpenIcon,
  RocketLaunchIcon,
  SparklesIcon,
  CheckCircleIcon,
} from '@heroicons/react/24/outline';
import { projectsApi } from '../api/projects';
import { useToast } from '../contexts/ToastContext';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { StatCard } from '../components/ui/StatCard';
import { EmptyState } from '../components/ui/EmptyState';
import { Modal } from '../components/ui/Modal';
import { Skeleton } from '../components/ui/Skeleton';
import { ResultsList } from '../components/ResultsList';
import { ScoreDistributionChart } from '../components/visualizations/ScoreDistributionChart';
import type { RankedCandidate, OutreachMessage } from '../types/pipeline';

export const ProjectDetailPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { showToast } = useToast();
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [exportLoading, setExportLoading] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);

  const { data: project, isLoading, error } = useQuery({
    queryKey: ['project', projectId],
    queryFn: () => projectsApi.getProject(projectId!),
    enabled: !!projectId,
  });

  const { data: shortlistedCandidates = [] } = useQuery({
    queryKey: ['shortlist', projectId],
    queryFn: () => projectsApi.getShortlist(projectId!),
    enabled: !!projectId && (project?.status === 'ranked' || project?.status === 'shortlisted'),
  });

  const deleteMutation = useMutation({
    mutationFn: projectsApi.deleteProject,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
      showToast('Project deleted successfully', 'success');
      navigate('/projects');
    },
    onError: () => {
      showToast('Failed to delete project', 'error');
    },
  });

  const resetMutation = useMutation({
    mutationFn: projectsApi.resetProject,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['project', projectId] });
      showToast('Project reset to draft successfully', 'success');
    },
    onError: () => {
      showToast('Failed to reset project', 'error');
    },
  });

  const handleReset = () => {
    if (projectId) {
      resetMutation.mutate(projectId);
    }
  };

  const handleExport = async () => {
    if (!projectId) return;

    setExportLoading(true);
    try {
      const blob = await projectsApi.exportProject(projectId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `project_${project?.job_title || projectId}.json`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      showToast('Project exported successfully', 'success');
    } catch (error) {
      console.error('Export failed:', error);
      showToast('Failed to export project', 'error');
    } finally {
      setExportLoading(false);
    }
  };

  const handleDelete = () => {
    setDeleteModalOpen(true);
  };

  const handleConfirmDelete = () => {
    if (projectId) {
      deleteMutation.mutate(projectId);
    }
  };

  const handleSourceCandidates = async () => {
    if (!projectId) return;

    setActionLoading(true);
    try {
      await projectsApi.sourceCandidates(projectId);
      queryClient.invalidateQueries({ queryKey: ['project', projectId] });
      showToast('Sourcing candidates...', 'success');
    } catch (error: any) {
      console.error('Source failed:', error);
      showToast(error.response?.data?.detail || 'Failed to source candidates', 'error');
    } finally {
      setActionLoading(false);
    }
  };

  const handleRankCandidates = async () => {
    if (!projectId) return;

    setActionLoading(true);
    try {
      await projectsApi.rankCandidates(projectId);
      queryClient.invalidateQueries({ queryKey: ['project', projectId] });
      showToast('Ranking candidates...', 'success');
    } catch (error: any) {
      console.error('Rank failed:', error);
      showToast(error.response?.data?.detail || 'Failed to rank candidates', 'error');
    } finally {
      setActionLoading(false);
    }
  };

  const handleToggleShortlist = async (username: string) => {
    if (!projectId) return;

    try {
      await projectsApi.toggleShortlist(projectId, username);
      // Invalidate both project and shortlist queries
      queryClient.invalidateQueries({ queryKey: ['project', projectId] });
      queryClient.invalidateQueries({ queryKey: ['shortlist', projectId] });
    } catch (error: any) {
      console.error('Toggle shortlist failed:', error);
      showToast(error.response?.data?.detail || 'Failed to update shortlist', 'error');
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      month: 'long',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getExecutionTime = () => {
    if (!project?.pipeline_start_time || !project?.pipeline_end_time) {
      return null;
    }

    const start = new Date(project.pipeline_start_time).getTime();
    const end = new Date(project.pipeline_end_time).getTime();
    const seconds = Math.round((end - start) / 1000);

    return `${seconds} seconds`;
  };

  if (isLoading) {
    return (
      <div className="space-y-8 animate-fade-in">
        <Skeleton variant="rectangular" height="60px" />
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Skeleton variant="rectangular" height="120px" />
          <Skeleton variant="rectangular" height="120px" />
          <Skeleton variant="rectangular" height="120px" />
        </div>
        <Skeleton variant="rectangular" height="400px" />
      </div>
    );
  }

  if (error || !project) {
    return (
      <EmptyState
        icon={<FolderOpenIcon className="h-12 w-12" />}
        title="Project Not Found"
        description="The project you're looking for doesn't exist or has been deleted."
        action={{
          label: 'Back to Projects',
          onClick: () => navigate('/projects'),
        }}
      />
    );
  }

  const statusBadgeVariant: Record<string, 'success' | 'warning' | 'danger' | 'default'> = {
    draft: 'default',
    sourcing: 'warning',
    sourced: 'default',
    ranking: 'warning',
    ranked: 'default',
    shortlisted: 'success',
    // Legacy statuses
    completed: 'success',
    running: 'warning',
    failed: 'danger',
    pending: 'default',
  };

  const badgeVariant = statusBadgeVariant[project.status] || 'default';
  const rankedCandidates = (project.results_json?.ranked_candidates || []) as RankedCandidate[];
  const outreachMessages = (project.results_json?.outreach_messages || []) as OutreachMessage[];
  const candidates = (project.results_json?.candidates || []);
  const avgScore = project.avg_score || 0;
  const shortlistedUsernames = new Set(shortlistedCandidates.map((s: any) => s.github_username));

  // Determine which action button to show based on status
  const getActionButton = () => {
    if (project.status === 'draft') {
      return (
        <Button
          onClick={handleSourceCandidates}
          variant="primary"
          size="lg"
          leftIcon={<RocketLaunchIcon className="h-5 w-5" />}
          isLoading={actionLoading}
          disabled={actionLoading}
        >
          Source Candidates
        </Button>
      );
    }

    if (project.status === 'sourced') {
      return (
        <Button
          onClick={handleRankCandidates}
          variant="primary"
          size="lg"
          leftIcon={<SparklesIcon className="h-5 w-5" />}
          isLoading={actionLoading}
          disabled={actionLoading}
        >
          Rank Candidates
        </Button>
      );
    }

    if (project.status === 'ranked') {
      return (
        <Button
          onClick={() => navigate(`/projects/${projectId}/shortlist`)}
          variant="primary"
          size="lg"
          leftIcon={<CheckCircleIcon className="h-5 w-5" />}
        >
          Review & Shortlist
        </Button>
      );
    }

    return null;
  };

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Back Button */}
      <Button
        onClick={() => navigate('/projects')}
        variant="ghost"
        leftIcon={<ArrowLeftIcon className="h-4 w-4" />}
      >
        Back to Projects
      </Button>

      {/* Header Card */}
      <Card variant="elevated" padding="lg">
        <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4 mb-6">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-3xl font-bold text-gray-900">
                {project.name || project.job_title || 'Untitled Project'}
              </h1>
              <Badge variant={badgeVariant} pill>
                {project.status.charAt(0).toUpperCase() + project.status.slice(1)}
              </Badge>
            </div>
            {project.job_title && project.name && (
              <p className="text-lg font-medium text-gray-700 mb-1">{project.job_title}</p>
            )}
            <p className="text-gray-600">
              Created {formatDate(project.created_at)}
            </p>
          </div>

          <div className="flex gap-3">
            {getActionButton()}
            {(project.status === 'sourced' || project.status === 'ranked' || project.status === 'failed') && (
              <Button
                onClick={handleReset}
                variant="secondary"
                isLoading={resetMutation.isPending}
                disabled={resetMutation.isPending}
              >
                Reset to Draft
              </Button>
            )}
            <Button
              onClick={handleExport}
              disabled={exportLoading || !project.results_json}
              variant="secondary"
              leftIcon={<ArrowDownTrayIcon className="h-5 w-5" />}
              isLoading={exportLoading}
            >
              Export
            </Button>
            <Button
              onClick={handleDelete}
              variant="danger"
              leftIcon={<TrashIcon className="h-5 w-5" />}
            >
              Delete
            </Button>
          </div>
        </div>

        <div className="mb-6">
          <h3 className="font-semibold text-gray-900 mb-2">Job Description</h3>
          <p className="text-gray-600 whitespace-pre-wrap leading-relaxed">
            {project.job_description_text}
          </p>
        </div>
      </Card>

      {/* Stats Grid */}
      {(project.status === 'completed' || project.status === 'ranked' || project.status === 'shortlisted') && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <StatCard
            label="Total Candidates"
            value={project.candidate_count || 0}
            icon={<UserGroupIcon className="h-6 w-6" />}
            variant="primary"
          />
          <StatCard
            label="Average Score"
            value={avgScore ? `${Math.round(avgScore)}%` : 'N/A'}
            icon={<ChartBarIcon className="h-6 w-6" />}
            variant="secondary"
          />
          <StatCard
            label="Execution Time"
            value={getExecutionTime() || 'N/A'}
            icon={<ClockIcon className="h-6 w-6" />}
            variant="accent"
          />
        </div>
      )}

      {/* Draft Status */}
      {project.status === 'draft' && (
        <Card variant="bordered" padding="lg" className="border-gray-200 bg-gray-50">
          <EmptyState
            icon={<RocketLaunchIcon className="h-12 w-12" />}
            title="Ready to Source Candidates"
            description="Click 'Source Candidates' above to start searching for developers on GitHub based on your job description."
          />
        </Card>
      )}

      {/* Sourcing Status */}
      {project.status === 'sourcing' && (
        <Card variant="bordered" padding="lg" className="border-blue-200 bg-blue-50">
          <EmptyState
            icon={
              <svg className="h-12 w-12 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            }
            title="Sourcing Candidates..."
            description="Searching GitHub for developers matching your job description. This may take a few minutes."
          />
        </Card>
      )}

      {/* Sourced Status */}
      {project.status === 'sourced' && (
        <Card variant="bordered" padding="lg" className="border-green-200 bg-green-50">
          <EmptyState
            icon={<CheckCircleIcon className="h-12 w-12 text-green-600" />}
            title={`Found ${candidates.length} Candidates`}
            description="Click 'Rank Candidates' above to score and rank these candidates based on their skills and experience."
          />
        </Card>
      )}

      {/* Ranking Status */}
      {project.status === 'ranking' && (
        <Card variant="bordered" padding="lg" className="border-blue-200 bg-blue-50">
          <EmptyState
            icon={
              <svg className="h-12 w-12 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            }
            title="Ranking Candidates..."
            description="Analyzing candidate profiles and calculating scores. This may take a few minutes."
          />
        </Card>
      )}

      {/* Ranked Status - Show Results */}
      {(project.status === 'ranked' || project.status === 'completed' || project.status === 'shortlisted') && rankedCandidates.length > 0 && (
        <div className="animate-slide-in space-y-6">
          {/* Shortlisted Banner */}
          {project.status === 'shortlisted' && shortlistedUsernames.size > 0 && (
            <Card variant="bordered" padding="md" className="border-green-200 bg-green-50">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <CheckCircleIcon className="h-6 w-6 text-green-600 flex-shrink-0" />
                  <div>
                    <h3 className="font-semibold text-green-900">Candidates Shortlisted</h3>
                    <p className="text-sm text-green-700">You have shortlisted {shortlistedUsernames.size} candidate{shortlistedUsernames.size !== 1 ? 's' : ''}. Next steps: enrichment and outreach.</p>
                  </div>
                </div>
                <Button
                  onClick={() => navigate(`/projects/${projectId}/shortlisted`)}
                  variant="primary"
                  size="sm"
                >
                  View Shortlist ({shortlistedUsernames.size})
                </Button>
              </div>
            </Card>
          )}

          {/* Score Distribution Chart */}
          <ScoreDistributionChart
            scores={rankedCandidates.map((c) => c.total_score)}
          />

          {/* Results List */}
          <ResultsList
            candidates={rankedCandidates}
            outreachMessages={outreachMessages}
            projectId={projectId!}
            shortlistedUsernames={shortlistedUsernames}
            onToggleShortlist={handleToggleShortlist}
          />
        </div>
      )}

      {/* Failed Status */}
      {project.status === 'failed' && (
        <Card variant="bordered" padding="lg" className="border-red-200 bg-red-50">
          <EmptyState
            icon={
              <svg className="h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            }
            title="Pipeline Failed"
            description="This project failed during execution. Please try creating a new project with a different job description."
            action={{
              label: 'Create New Project',
              onClick: () => navigate('/dashboard'),
            }}
          />
        </Card>
      )}

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={deleteModalOpen}
        onClose={() => setDeleteModalOpen(false)}
        title="Delete Project"
        footer={
          <div className="flex gap-3 justify-end">
            <Button onClick={() => setDeleteModalOpen(false)} variant="secondary">
              Cancel
            </Button>
            <Button
              onClick={handleConfirmDelete}
              variant="danger"
              isLoading={deleteMutation.isPending}
            >
              Delete Project
            </Button>
          </div>
        }
      >
        <p className="text-gray-600">
          Are you sure you want to delete <span className="font-semibold">{project.job_title || 'this project'}</span>?
          This action cannot be undone and all results will be lost.
        </p>
      </Modal>
    </div>
  );
};
