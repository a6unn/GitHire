import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ToastProvider } from '../contexts/ToastContext';
import { ProjectsPage } from './ProjectsPage';
import { projectsApi } from '../api/projects';
import type { ProjectsResponse } from '../types/project';

// Mock the API
vi.mock('../api/projects', () => ({
  projectsApi: {
    getProjects: vi.fn(),
    deleteProject: vi.fn(),
  },
}));

// Mock useNavigate
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

const renderProjectsPage = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  return render(
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <ToastProvider>
          <ProjectsPage />
        </ToastProvider>
      </BrowserRouter>
    </QueryClientProvider>
  );
};

describe('ProjectsPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  const mockProjectsResponse: ProjectsResponse = {
    projects: [
      {
        id: 'project-1',
        project_id: 'project-1',
        status: 'completed',
        job_title: 'Senior Python Developer',
        job_description: 'Looking for senior Python developer',
        job_description_text: 'Senior Python Developer',
        candidates_count: 10,
        candidate_count: 10,
        avg_score: 85,
        created_at: '2025-10-06T12:00:00Z',
        pipeline_start_time: '2025-10-06T12:00:00Z',
        pipeline_end_time: '2025-10-06T12:00:15Z',
        results_json: null,
      },
      {
        id: 'project-2',
        project_id: 'project-2',
        status: 'running',
        job_title: 'Full Stack Engineer',
        job_description: 'Full stack engineer position',
        job_description_text: 'Full Stack Engineer',
        candidates_count: 0,
        candidate_count: 0,
        avg_score: 0,
        created_at: '2025-10-05T10:00:00Z',
        pipeline_start_time: null,
        pipeline_end_time: null,
        results_json: null,
      },
    ],
    total: 2,
  };

  it('renders projects list', async () => {
    vi.mocked(projectsApi.getProjects).mockResolvedValue(mockProjectsResponse);

    renderProjectsPage();

    await waitFor(() => {
      expect(screen.getByText(/2 projects total/i)).toBeInTheDocument();
    });

    // Check that project titles appear in links
    const links = screen.getAllByRole('link');
    const projectLinks = links.filter(link =>
      link.textContent?.includes('Senior Python Developer') ||
      link.textContent?.includes('Full Stack Engineer')
    );
    expect(projectLinks.length).toBeGreaterThanOrEqual(2);
  });

  it('shows loading state', () => {
    vi.mocked(projectsApi.getProjects).mockImplementation(
      () => new Promise(() => {}) // Never resolves
    );

    renderProjectsPage();

    // Should show skeleton loaders
    expect(screen.getByText(/My Projects/i)).toBeInTheDocument();
  });

  it('shows error state', async () => {
    vi.mocked(projectsApi.getProjects).mockRejectedValue(new Error('API Error'));

    renderProjectsPage();

    await waitFor(() => {
      expect(screen.getByText(/Error Loading Projects/i)).toBeInTheDocument();
    });
  });

  it('shows empty state when no projects', async () => {
    vi.mocked(projectsApi.getProjects).mockResolvedValue({ projects: [], total: 0 });

    renderProjectsPage();

    await waitFor(() => {
      expect(screen.getByText(/No Projects Found/i)).toBeInTheDocument();
      expect(screen.getByText(/haven't created any projects yet/i)).toBeInTheDocument();
    });
  });

  it('filters projects by status', async () => {
    vi.mocked(projectsApi.getProjects).mockResolvedValue(mockProjectsResponse);

    renderProjectsPage();

    await waitFor(() => {
      expect(screen.getByText(/2 projects total/i)).toBeInTheDocument();
    });

    const completedButton = screen.getByRole('button', { name: 'Completed' });
    fireEvent.click(completedButton);

    await waitFor(() => {
      expect(projectsApi.getProjects).toHaveBeenLastCalledWith({ status: 'completed' });
    });
  });

  it('navigates to dashboard on New Project button click', async () => {
    vi.mocked(projectsApi.getProjects).mockResolvedValue(mockProjectsResponse);

    renderProjectsPage();

    await waitFor(() => {
      expect(screen.getByText(/2 projects total/i)).toBeInTheDocument();
    });

    const newProjectButton = screen.getByRole('button', { name: /New Project/i });
    fireEvent.click(newProjectButton);

    expect(mockNavigate).toHaveBeenCalledWith('/dashboard');
  });

  it('opens delete confirmation modal', async () => {
    vi.mocked(projectsApi.getProjects).mockResolvedValue(mockProjectsResponse);

    renderProjectsPage();

    await waitFor(() => {
      expect(screen.getByText(/2 projects total/i)).toBeInTheDocument();
    });

    const deleteButtons = screen.getAllByRole('button', { name: /delete/i });
    fireEvent.click(deleteButtons[0]);

    expect(screen.getByText(/Are you sure you want to delete this project/i)).toBeInTheDocument();
  });

  it('deletes project on confirmation', async () => {
    vi.mocked(projectsApi.getProjects).mockResolvedValue(mockProjectsResponse);
    vi.mocked(projectsApi.deleteProject).mockResolvedValue({ message: 'Deleted' });

    renderProjectsPage();

    await waitFor(() => {
      expect(screen.getByText(/2 projects total/i)).toBeInTheDocument();
    });

    // Click delete
    const deleteButtons = screen.getAllByRole('button', { name: /delete/i });
    fireEvent.click(deleteButtons[0]);

    // Confirm deletion
    const confirmButton = screen.getByRole('button', { name: 'Delete' });
    fireEvent.click(confirmButton);

    await waitFor(() => {
      expect(projectsApi.deleteProject).toHaveBeenCalled();
      const calls = vi.mocked(projectsApi.deleteProject).mock.calls;
      expect(calls[0][0]).toBe('project-1');
    });
  });
});
