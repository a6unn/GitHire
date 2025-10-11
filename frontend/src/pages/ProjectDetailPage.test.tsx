import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ToastProvider } from '../contexts/ToastContext';
import { ProjectDetailPage } from './ProjectDetailPage';
import { projectsApi } from '../api/projects';
import type { Project } from '../types/project';

// Mock the API
vi.mock('../api/projects', () => ({
  projectsApi: {
    getProject: vi.fn(),
    deleteProject: vi.fn(),
    exportProject: vi.fn(),
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

const renderProjectDetailPage = (projectId: string = 'test-project-id') => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  return render(
    <QueryClientProvider client={queryClient}>
      <ToastProvider>
        <MemoryRouter initialEntries={[`/projects/${projectId}`]}>
          <Routes>
            <Route path="/projects/:projectId" element={<ProjectDetailPage />} />
          </Routes>
        </MemoryRouter>
      </ToastProvider>
    </QueryClientProvider>
  );
};

describe('ProjectDetailPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  const mockProject: Project = {
    project_id: 'test-project-id',
    user_id: 'user-123',
    status: 'completed',
    job_description_text: 'Senior Python Developer with 5+ years of experience.',
    candidate_count: 10,
    created_at: '2025-10-06T12:00:00Z',
    pipeline_start_time: '2025-10-06T12:00:00Z',
    pipeline_end_time: '2025-10-06T12:00:15Z',
    results_json: {
      status: 'success',
      candidates: [],
      ranked_candidates: [
        {
          github_username: 'testdev',
          total_score: 85.5,
          rank: 1,
          domain_score: 90.0,
          score_breakdown: { skill_match: 90.0, experience: 85.0, activity: 82.0 },
          strengths: ['Strong Python skills'],
          concerns: [],
        },
      ],
      outreach_messages: [],
    },
  };

  it('renders project details', async () => {
    vi.mocked(projectsApi.getProject).mockResolvedValue(mockProject);

    renderProjectDetailPage();

    await waitFor(() => {
      const heading = screen.getByRole('heading', { level: 1 });
      expect(heading.textContent).toContain('Project');
      expect(heading.textContent).toContain('test-pro');
    });

    expect(screen.getByText('Completed')).toBeInTheDocument();
    expect(screen.getByText(/Senior Python Developer/i)).toBeInTheDocument();
  });

  it('shows loading state', () => {
    vi.mocked(projectsApi.getProject).mockImplementation(
      () => new Promise(() => {}) // Never resolves
    );

    renderProjectDetailPage();

    expect(document.querySelector('.animate-spin')).toBeInTheDocument();
  });

  it('shows error state for non-existent project', async () => {
    vi.mocked(projectsApi.getProject).mockRejectedValue(new Error('Not found'));

    renderProjectDetailPage();

    await waitFor(() => {
      expect(screen.getByText(/Project Not Found/i)).toBeInTheDocument();
    });
  });

  it('navigates back to projects list', async () => {
    vi.mocked(projectsApi.getProject).mockResolvedValue(mockProject);

    renderProjectDetailPage();

    await waitFor(() => {
      expect(screen.getByText('Completed')).toBeInTheDocument();
    });

    const backButton = screen.getByRole('button', { name: /back to projects/i });
    fireEvent.click(backButton);

    expect(mockNavigate).toHaveBeenCalledWith('/projects');
  });

  it('exports project results', async () => {
    vi.mocked(projectsApi.getProject).mockResolvedValue(mockProject);
    const mockBlob = new Blob(['test'], { type: 'application/json' });
    vi.mocked(projectsApi.exportProject).mockResolvedValue(mockBlob);

    // Mock URL.createObjectURL
    global.URL.createObjectURL = vi.fn(() => 'blob:test');
    global.URL.revokeObjectURL = vi.fn();

    renderProjectDetailPage();

    await waitFor(() => {
      expect(screen.getByText('Completed')).toBeInTheDocument();
    });

    const exportButton = screen.getByRole('button', { name: /export results/i });
    fireEvent.click(exportButton);

    await waitFor(() => {
      expect(projectsApi.exportProject).toHaveBeenCalledWith('test-project-id');
    });
  });

  it('opens delete confirmation modal', async () => {
    vi.mocked(projectsApi.getProject).mockResolvedValue(mockProject);

    renderProjectDetailPage();

    await waitFor(() => {
      expect(screen.getByText('Completed')).toBeInTheDocument();
    });

    const deleteButton = screen.getByRole('button', { name: /delete project/i });
    fireEvent.click(deleteButton);

    expect(screen.getByText(/Are you sure you want to delete/i)).toBeInTheDocument();
  });

  it('deletes project and navigates to projects list', async () => {
    vi.mocked(projectsApi.getProject).mockResolvedValue(mockProject);
    vi.mocked(projectsApi.deleteProject).mockResolvedValue({ message: 'Deleted' });

    renderProjectDetailPage();

    await waitFor(() => {
      expect(screen.getByText('Completed')).toBeInTheDocument();
    });

    // Open modal
    const deleteButton = screen.getByRole('button', { name: /delete project/i });
    fireEvent.click(deleteButton);

    // Confirm deletion
    const confirmButton = screen.getByRole('button', { name: 'Delete' });
    fireEvent.click(confirmButton);

    await waitFor(() => {
      expect(projectsApi.deleteProject).toHaveBeenCalled();
      const calls = vi.mocked(projectsApi.deleteProject).mock.calls;
      expect(calls[0][0]).toBe('test-project-id');
      expect(mockNavigate).toHaveBeenCalledWith('/projects');
    });
  });

  it('displays results for completed project', async () => {
    vi.mocked(projectsApi.getProject).mockResolvedValue(mockProject);

    renderProjectDetailPage();

    await waitFor(() => {
      expect(screen.getByText('Completed')).toBeInTheDocument();
    });

    // ResultsList should be rendered
    expect(screen.getByText(/testdev/i)).toBeInTheDocument();
  });

  it('shows running status message', async () => {
    const runningProject = { ...mockProject, status: 'running' as const, results_json: undefined };
    vi.mocked(projectsApi.getProject).mockResolvedValue(runningProject);

    renderProjectDetailPage();

    await waitFor(() => {
      expect(screen.getByText(/Pipeline Running/i)).toBeInTheDocument();
    });
  });

  it('shows failed status message', async () => {
    const failedProject = { ...mockProject, status: 'failed' as const, results_json: undefined };
    vi.mocked(projectsApi.getProject).mockResolvedValue(failedProject);

    renderProjectDetailPage();

    await waitFor(() => {
      expect(screen.getByText(/Pipeline Failed/i)).toBeInTheDocument();
    });
  });

  it('disables export button when no results', async () => {
    const projectWithoutResults = { ...mockProject, results_json: undefined };
    vi.mocked(projectsApi.getProject).mockResolvedValue(projectWithoutResults);

    renderProjectDetailPage();

    await waitFor(() => {
      expect(screen.getByText('Completed')).toBeInTheDocument();
    });

    const exportButton = screen.getByRole('button', { name: /export results/i });
    expect(exportButton).toBeDisabled();
  });
});
