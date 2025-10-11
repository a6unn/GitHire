import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ProjectListItem } from './ProjectListItem';
import type { ProjectListItem as ProjectListItemType } from '../types/project';

const renderProjectListItem = (project: ProjectListItemType, onDelete = vi.fn()) => {
  return render(
    <BrowserRouter>
      <ProjectListItem project={project} onDelete={onDelete} />
    </BrowserRouter>
  );
};

describe('ProjectListItem', () => {
  const mockProject: ProjectListItemType = {
    project_id: '123e4567-e89b-12d3-a456-426614174000',
    status: 'completed',
    job_description_text: 'Looking for a Senior Python Developer with 5+ years of experience.',
    candidate_count: 10,
    created_at: '2025-10-06T12:00:00Z',
    pipeline_start_time: '2025-10-06T12:00:00Z',
    pipeline_end_time: '2025-10-06T12:00:15Z',
  };

  it('renders project information', () => {
    renderProjectListItem(mockProject);

    expect(screen.getByText(/Project 123e4567/i)).toBeInTheDocument();
    expect(screen.getByText('Completed')).toBeInTheDocument();
    expect(screen.getByText(/10 candidates/i)).toBeInTheDocument();
  });

  it('truncates long job descriptions', () => {
    const longProject = {
      ...mockProject,
      job_description_text: 'A'.repeat(200),
    };

    renderProjectListItem(longProject);

    const text = screen.getByText(/A+\.\.\./);
    expect(text.textContent?.length).toBeLessThan(200);
  });

  it('shows execution time when available', () => {
    renderProjectListItem(mockProject);

    expect(screen.getByText(/Execution time: 15s/i)).toBeInTheDocument();
  });

  it('renders different status styles', () => {
    const statuses: Array<'pending' | 'running' | 'completed' | 'failed'> = [
      'pending',
      'running',
      'completed',
      'failed',
    ];

    statuses.forEach((status) => {
      const { unmount } = renderProjectListItem({ ...mockProject, status });
      expect(screen.getByText(status.charAt(0).toUpperCase() + status.slice(1))).toBeInTheDocument();
      unmount();
    });
  });

  it('calls onDelete when delete button is clicked', () => {
    const onDelete = vi.fn();
    renderProjectListItem(mockProject, onDelete);

    const deleteButton = screen.getByRole('button', { name: /delete/i });
    fireEvent.click(deleteButton);

    expect(onDelete).toHaveBeenCalledWith(mockProject.project_id);
  });

  it('renders link to project detail page', () => {
    renderProjectListItem(mockProject);

    const link = screen.getByRole('link', { name: /Project 123e4567/i });
    expect(link).toHaveAttribute('href', `/projects/${mockProject.project_id}`);
  });

  it('handles projects with no candidates', () => {
    const projectWithNoCandidates = {
      ...mockProject,
      candidate_count: 0,
    };

    renderProjectListItem(projectWithNoCandidates);

    expect(screen.queryByText(/candidates/i)).not.toBeInTheDocument();
  });

  it('handles singular candidate count', () => {
    const projectWithOneCandidate = {
      ...mockProject,
      candidate_count: 1,
    };

    renderProjectListItem(projectWithOneCandidate);

    expect(screen.getByText(/1 candidate$/i)).toBeInTheDocument();
  });
});
