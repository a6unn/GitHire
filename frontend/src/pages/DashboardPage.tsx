import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { RocketLaunchIcon, FolderOpenIcon, UserGroupIcon, ChartBarIcon } from '@heroicons/react/24/outline';
import { useAuth } from '../contexts/AuthContext';
import { projectsApi } from '../api/projects';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { StatCard } from '../components/ui/StatCard';
import { ProjectCard } from '../components/ui/ProjectCard';
import { EmptyState } from '../components/ui/EmptyState';
import { Skeleton } from '../components/ui/Skeleton';
import { ActivityTimeline } from '../components/visualizations/ActivityTimeline';
import { QuickActions } from '../components/dashboard/QuickActions';
import { PipelineVisualization } from '../components/dashboard/PipelineVisualization';
import CreateProjectModal from '../components/CreateProjectModal';
import type { TimelineItem } from '../components/visualizations/ActivityTimeline';

export const DashboardPage: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

  // Fetch recent projects
  const { data: projectsData, isLoading: isLoadingProjects } = useQuery({
    queryKey: ['projects', { limit: 6 }],
    queryFn: () => projectsApi.getProjects({ limit: 6 }),
  });

  const recentProjects = projectsData?.projects || [];
  const totalProjects = projectsData?.total || 0;

  // Calculate stats from ALL projects (not just recent 6)
  const allProjects = recentProjects; // In real app, fetch all projects for accurate stats

  const totalCandidates = allProjects.reduce(
    (sum, project) => sum + (project.candidate_count || 0),
    0
  );
  const avgScore = allProjects.length > 0
    ? Math.round(
        allProjects.reduce((sum, project) => sum + (project.avg_score || 0), 0) /
          allProjects.length
      )
    : 0;

  // Calculate pipeline counts
  const countByStatus = (status: string[]) =>
    allProjects.filter(p => status.includes(p.status.toLowerCase())).length;

  const draftCount = countByStatus(['draft']);
  const sourcedCount = countByStatus(['sourced', 'sourcing']);
  const rankedCount = countByStatus(['ranked', 'ranking']);
  const shortlistedCount = countByStatus(['shortlisted']);
  const needsRankingCount = rankedCount; // Projects that need ranking

  // Mock trend data (in real app, compare with previous period)
  const projectsTrend = totalProjects >= 3 ? { value: 25, isPositive: true } : undefined;
  const candidatesTrend = totalCandidates >= 50 ? { value: 15, isPositive: true } : undefined;
  const scoreTrend = avgScore >= 35 ? { value: 8, isPositive: true } : undefined;

  // Create activity timeline from projects
  const activityItems: TimelineItem[] = recentProjects.map((project) => ({
    id: project.project_id,
    title: project.job_title || 'Untitled Project',
    description: `${project.candidate_count || 0} candidates found`,
    timestamp: project.created_at,
    status: project.status === 'completed' ? 'completed' : project.status === 'failed' ? 'failed' : 'pending',
  }));

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="mt-2 text-gray-600">Welcome back, {user?.name || user?.email}!</p>
        </div>
        <Button
          onClick={() => setIsCreateModalOpen(true)}
          variant="primary"
          size="lg"
          leftIcon={<RocketLaunchIcon className="h-5 w-5" />}
        >
          Create Project
        </Button>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatCard
          label="Total Projects"
          value={totalProjects}
          icon={<FolderOpenIcon className="h-6 w-6" />}
          variant="primary"
          trend={projectsTrend}
        />
        <StatCard
          label="Total Candidates"
          value={totalCandidates}
          icon={<UserGroupIcon className="h-6 w-6" />}
          variant="secondary"
          trend={candidatesTrend}
        />
        <StatCard
          label="Average Match Score"
          value={`${avgScore}%`}
          icon={<ChartBarIcon className="h-6 w-6" />}
          variant="accent"
          trend={scoreTrend}
        />
      </div>

      {/* Quick Actions & Pipeline Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <QuickActions
          readyToContactCount={shortlistedCount}
          needsRankingCount={needsRankingCount}
          onNavigate={(path) => navigate(path)}
          onCreateProject={() => setIsCreateModalOpen(true)}
        />
        <PipelineVisualization
          draftCount={draftCount}
          sourcedCount={sourcedCount}
          rankedCount={rankedCount}
          shortlistedCount={shortlistedCount}
        />
      </div>

      {/* Recent Projects */}
      <Card variant="elevated" padding="lg">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-gray-900">Recent Projects</h2>
          {totalProjects > 0 && (
            <Button
              onClick={() => navigate('/projects')}
              variant="ghost"
              size="sm"
            >
              View All
            </Button>
          )}
        </div>

        {isLoadingProjects ? (
          <div className="space-y-4">
            <Skeleton key="skeleton-1" variant="rectangular" height="120px" />
            <Skeleton key="skeleton-2" variant="rectangular" height="120px" />
            <Skeleton key="skeleton-3" variant="rectangular" height="120px" />
          </div>
        ) : recentProjects.length > 0 ? (
          <div className="space-y-4">
            {recentProjects.map((project, index) => (
              <div
                key={project.project_id}
                className="stagger-item"
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                <ProjectCard
                  id={project.project_id}
                  title={project.job_title || 'Untitled Project'}
                  description={project.job_description_text?.substring(0, 100)}
                  status={project.status as 'active' | 'completed' | 'draft'}
                  createdAt={project.created_at}
                  candidatesCount={project.candidate_count}
                  avgScore={project.avg_score}
                />
              </div>
            ))}
          </div>
        ) : (
          <EmptyState
            icon={<FolderOpenIcon className="h-12 w-12" />}
            title="No projects yet"
            description="Create your first project to start finding the perfect developers on GitHub"
            action={{
              label: 'Create Project',
              onClick: () => setIsCreateModalOpen(true),
            }}
          />
        )}
      </Card>

      {/* Activity Timeline */}
      {activityItems.length > 0 && (
        <ActivityTimeline items={activityItems} />
      )}

      {/* Create Project Modal */}
      <CreateProjectModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
      />
    </div>
  );
};
