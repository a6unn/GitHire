import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { FolderOpenIcon, PlusIcon, FunnelIcon } from '@heroicons/react/24/outline';
import { useToast } from '../contexts/ToastContext';
import { projectsApi } from '../api/projects';
import { Button } from '../components/ui/Button';
import { ProjectCard } from '../components/ui/ProjectCard';
import { EmptyState } from '../components/ui/EmptyState';
import { Skeleton } from '../components/ui/Skeleton';
import { Modal } from '../components/ui/Modal';
import { Badge } from '../components/ui/Badge';
import CreateProjectModal from '../components/CreateProjectModal';
import type { ProjectFilters } from '../types/project';

type ActionFilter = 'all' | 'in_progress' | 'ready_to_contact';

export const ProjectsPage: React.FC = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { showToast } = useToast();
  const [actionFilter, setActionFilter] = useState<ActionFilter>('all');
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [projectToDelete, setProjectToDelete] = useState<{ id: string; title: string } | null>(null);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

  // Fetch all projects (we'll filter client-side for action-based filters)
  const { data, isLoading, error } = useQuery({
    queryKey: ['projects'],
    queryFn: () => projectsApi.getProjects(),
  });

  const deleteMutation = useMutation({
    mutationFn: projectsApi.deleteProject,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
      setDeleteModalOpen(false);
      setProjectToDelete(null);
      showToast('Project deleted successfully', 'success');
    },
    onError: () => {
      showToast('Failed to delete project', 'error');
    },
  });

  const handleDeleteClick = (projectId: string, title: string) => {
    setProjectToDelete({ id: projectId, title });
    setDeleteModalOpen(true);
  };

  const handleConfirmDelete = () => {
    if (projectToDelete) {
      deleteMutation.mutate(projectToDelete.id);
    }
  };

  const allProjects = data?.projects || [];

  // Helper function to check if project is in progress
  const isInProgress = (status: string): boolean => {
    const statusLower = status.toLowerCase();
    return ['draft', 'sourcing', 'sourced', 'ranking', 'ranked'].includes(statusLower);
  };

  // Helper function to check if project is ready to contact
  const isReadyToContact = (status: string): boolean => {
    return status.toLowerCase() === 'shortlisted';
  };

  // Filter projects based on action filter
  const projects = allProjects.filter((project) => {
    if (actionFilter === 'all') return true;
    if (actionFilter === 'in_progress') return isInProgress(project.status);
    if (actionFilter === 'ready_to_contact') return isReadyToContact(project.status);
    return true;
  });

  const total = projects.length;
  const inProgressCount = allProjects.filter(p => isInProgress(p.status)).length;
  const readyToContactCount = allProjects.filter(p => isReadyToContact(p.status)).length;

  // Map project status to card status
  const mapProjectStatus = (status: string): 'active' | 'completed' | 'draft' => {
    const statusLower = status.toLowerCase();

    // Ready to contact (shortlisted)
    if (statusLower === 'shortlisted') {
      return 'completed';
    }

    // In progress (working on it)
    if (['sourcing', 'sourced', 'ranking', 'ranked', 'running', 'pending'].includes(statusLower)) {
      return 'active';
    }

    // Draft (not started)
    return 'draft';
  };

  const actionFilters = [
    {
      value: 'all' as const,
      label: 'All Projects',
      count: allProjects.length,
      description: 'View all your projects'
    },
    {
      value: 'in_progress' as const,
      label: 'In Progress',
      count: inProgressCount,
      description: 'Projects being worked on'
    },
    {
      value: 'ready_to_contact' as const,
      label: 'Ready to Contact',
      count: readyToContactCount,
      description: 'Shortlisted candidates ready for outreach'
    },
  ];

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <EmptyState
          icon={<FolderOpenIcon className="h-12 w-12" />}
          title="Error Loading Projects"
          description="Failed to load projects. Please try again."
          action={{
            label: 'Retry',
            onClick: () => queryClient.invalidateQueries({ queryKey: ['projects'] }),
          }}
        />
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">My Projects</h1>
          <p className="text-gray-600 mt-1">
            {total} project{total !== 1 ? 's' : ''} total
          </p>
        </div>
        <Button
          onClick={() => setIsCreateModalOpen(true)}
          variant="primary"
          size="lg"
          leftIcon={<PlusIcon className="h-5 w-5" />}
        >
          Create Project
        </Button>
      </div>

      {/* Action-Based Filter Tabs */}
      <div className="flex flex-wrap items-center gap-3">
        <FunnelIcon className="h-5 w-5 text-gray-400" />
        {actionFilters.map((filter) => (
          <button
            key={filter.value}
            onClick={() => setActionFilter(filter.value)}
            className={`
              group px-5 py-3 rounded-lg font-medium transition-all relative
              ${
                actionFilter === filter.value
                  ? 'bg-primary-600 text-white shadow-lg scale-105'
                  : 'bg-white text-gray-700 border-2 border-gray-200 hover:border-primary-400 hover:shadow-md'
              }
            `}
            title={filter.description}
          >
            <div className="flex items-center gap-2">
              <span>{filter.label}</span>
              <span
                className={`
                  inline-flex items-center justify-center min-w-[24px] h-6 px-2 rounded-full text-xs font-bold
                  ${
                    actionFilter === filter.value
                      ? 'bg-white text-primary-600'
                      : 'bg-gray-100 text-gray-700 group-hover:bg-primary-100 group-hover:text-primary-700'
                  }
                `}
              >
                {filter.count}
              </span>
            </div>
          </button>
        ))}
      </div>

      {/* Projects Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <Skeleton key={i} variant="rectangular" height="200px" />
          ))}
        </div>
      ) : projects.length === 0 ? (
        <EmptyState
          icon={<FolderOpenIcon className="h-12 w-12" />}
          title={actionFilter === 'all' ? 'No Projects Yet' : 'No Projects Found'}
          description={
            actionFilter === 'all'
              ? "You haven't created any projects yet. Start by creating your first project to find great developers!"
              : actionFilter === 'in_progress'
              ? "No projects are currently in progress. Create a new project or complete existing ones."
              : "No projects are ready for outreach yet. Complete the ranking stage to shortlist candidates."
          }
          action={{
            label: actionFilter === 'all' ? 'Create Your First Project' : 'View All Projects',
            onClick: () => actionFilter === 'all' ? setIsCreateModalOpen(true) : setActionFilter('all'),
          }}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map((project, index) => (
            <div
              key={project.project_id}
              className="stagger-item"
              style={{ animationDelay: `${index * 0.05}s` }}
            >
              <ProjectCard
                id={project.project_id}
                title={project.job_title || 'Untitled Project'}
                description={project.job_description_text?.substring(0, 120)}
                status={mapProjectStatus(project.status)}
                createdAt={project.created_at}
                candidatesCount={project.candidate_count}
                avgScore={project.avg_score ?? undefined}
              />
            </div>
          ))}
        </div>
      )}

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={deleteModalOpen}
        onClose={() => setDeleteModalOpen(false)}
        title="Delete Project"
        footer={
          <div className="flex gap-3 justify-end">
            <Button
              onClick={() => setDeleteModalOpen(false)}
              variant="secondary"
            >
              Cancel
            </Button>
            <Button
              onClick={handleConfirmDelete}
              variant="danger"
              isLoading={deleteMutation.isPending}
            >
              Delete
            </Button>
          </div>
        }
      >
        <p className="text-gray-600">
          Are you sure you want to delete{' '}
          <span className="font-semibold">{projectToDelete?.title}</span>? This action cannot
          be undone and all results will be lost.
        </p>
      </Modal>

      {/* Create Project Modal */}
      <CreateProjectModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
      />
    </div>
  );
};
