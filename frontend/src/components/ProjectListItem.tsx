import React from 'react';
import { Link } from 'react-router-dom';
import type { ProjectListItem as ProjectListItemType } from '../types/project';

interface ProjectListItemProps {
  project: ProjectListItemType;
  onDelete: (projectId: string) => void;
}

const statusStyles = {
  pending: 'bg-gray-100 text-gray-800',
  running: 'bg-blue-100 text-blue-800',
  completed: 'bg-green-100 text-green-800',
  failed: 'bg-red-100 text-red-800',
};

const statusLabels = {
  pending: 'Pending',
  running: 'Running',
  completed: 'Completed',
  failed: 'Failed',
};

export const ProjectListItem: React.FC<ProjectListItemProps> = ({ project, onDelete }) => {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getExecutionTime = () => {
    if (!project.pipeline_start_time || !project.pipeline_end_time) {
      return null;
    }

    const start = new Date(project.pipeline_start_time).getTime();
    const end = new Date(project.pipeline_end_time).getTime();
    const seconds = Math.round((end - start) / 1000);

    return `${seconds}s`;
  };

  const truncateText = (text: string, maxLength: number) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <Link
              to={`/projects/${project.project_id}`}
              className="text-lg font-semibold text-primary-600 hover:text-primary-700"
            >
              Project {project.project_id.slice(0, 8)}
            </Link>
            <span
              className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${
                statusStyles[project.status]
              }`}
            >
              {statusLabels[project.status]}
            </span>
          </div>

          <p className="text-gray-600 text-sm mb-3">
            {truncateText(project.job_description_text, 150)}
          </p>

          <div className="flex gap-4 text-sm text-gray-500">
            <span>Created: {formatDate(project.created_at)}</span>
            {project.candidate_count > 0 && (
              <span className="font-medium text-gray-700">
                {project.candidate_count} candidate{project.candidate_count !== 1 ? 's' : ''}
              </span>
            )}
            {getExecutionTime() && (
              <span>Execution time: {getExecutionTime()}</span>
            )}
          </div>
        </div>

        <button
          onClick={() => onDelete(project.project_id)}
          className="ml-4 text-red-600 hover:text-red-700 text-sm font-medium"
          aria-label="Delete project"
        >
          Delete
        </button>
      </div>
    </div>
  );
};
