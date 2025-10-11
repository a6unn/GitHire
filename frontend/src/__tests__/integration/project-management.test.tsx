import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from '../../contexts/AuthContext';
import { ToastProvider } from '../../contexts/ToastContext';
import { ProjectsPage } from '../../pages/ProjectsPage';
import { ProjectDetailPage } from '../../pages/ProjectDetailPage';
import { projectsApi } from '../../api/projects';
import type { ProjectsResponse, Project } from '../../types/project';

// Mock API
vi.mock('../../api/projects', () => ({
  projectsApi: {
    getProjects: vi.fn(),
    getProject: vi.fn(),
    deleteProject: vi.fn(),
    exportProject: vi.fn(),
  },
}));

const renderWithRouter = (initialRoute: string, component: React.ReactElement) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  // Set up logged-in state
  localStorage.setItem('auth_token', 'test-token');
  localStorage.setItem('user', JSON.stringify({
    user_id: 'user-123',
    email: 'test@example.com',
    created_at: new Date().toISOString(),
  }));

  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={[initialRoute]}>
        <ToastProvider>
          <AuthProvider>
            <Routes>
              <Route path="/projects" element={<ProjectsPage />} />
              <Route path="/projects/:projectId" element={<ProjectDetailPage />} />
            </Routes>
          </AuthProvider>
        </ToastProvider>
      </MemoryRouter>
    </QueryClientProvider>
  );
};

describe('Project Management Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  const mockProjectsResponse: ProjectsResponse = {
    projects: [
      {
        project_id: 'project-1',
        status: 'completed',
        job_description_text: 'Python Developer',
        candidate_count: 5,
        created_at: '2025-10-06T12:00:00Z',
        pipeline_start_time: '2025-10-06T12:00:00Z',
        pipeline_end_time: '2025-10-06T12:00:10Z',
      },
      {
        project_id: 'project-2',
        status: 'running',
        job_description_text: 'JavaScript Developer',
        candidate_count: 0,
        created_at: '2025-10-06T11:00:00Z',
        pipeline_start_time: null,
        pipeline_end_time: null,
      },
    ],
    total: 2,
  };

  it('displays list of projects', async () => {
    vi.mocked(projectsApi.getProjects).mockResolvedValue(mockProjectsResponse);

    renderWithRouter('/projects', <ProjectsPage />);

    await waitFor(() => {
      expect(screen.getByText(/2 projects total/i)).toBeInTheDocument();
    });

    // Check both projects are displayed
    const links = screen.getAllByRole('link');
    const projectLinks = links.filter(link => link.textContent?.includes('Project'));
    expect(projectLinks.length).toBeGreaterThanOrEqual(2);
  });

  it('filters projects by status', async () => {
    vi.mocked(projectsApi.getProjects).mockResolvedValue(mockProjectsResponse);

    renderWithRouter('/projects', <ProjectsPage />);

    await waitFor(() => {
      expect(screen.getByText(/2 projects total/i)).toBeInTheDocument();
    });

    // Click on "Completed" filter
    const completedButton = screen.getByRole('button', { name: 'Completed' });
    fireEvent.click(completedButton);

    // Verify API was called with filter
    await waitFor(() => {
      expect(projectsApi.getProjects).toHaveBeenCalledWith({ status: 'completed' });
    });
  });

  it('navigates to project details', async () => {
    const mockProject: Project = {
      project_id: 'project-1',
      user_id: 'user-123',
      status: 'completed',
      job_description_text: 'Python Developer',
      candidate_count: 5,
      created_at: '2025-10-06T12:00:00Z',
      pipeline_start_time: '2025-10-06T12:00:00Z',
      pipeline_end_time: '2025-10-06T12:00:10Z',
      results_json: {
        status: 'success',
        candidates: [],
        ranked_candidates: [],
        outreach_messages: [],
      },
    };

    vi.mocked(projectsApi.getProject).mockResolvedValue(mockProject);

    renderWithRouter('/projects/project-1', <ProjectDetailPage />);

    await waitFor(() => {
      expect(screen.getByText('Completed')).toBeInTheDocument();
    });

    // Verify project details are shown
    expect(screen.getByText(/Python Developer/i)).toBeInTheDocument();
  });

  it('deletes project with confirmation', async () => {
    vi.mocked(projectsApi.getProjects).mockResolvedValue(mockProjectsResponse);
    vi.mocked(projectsApi.deleteProject).mockResolvedValue({ message: 'Deleted' });

    renderWithRouter('/projects', <ProjectsPage />);

    await waitFor(() => {
      expect(screen.getByText(/2 projects total/i)).toBeInTheDocument();
    });

    // Click delete button
    const deleteButtons = screen.getAllByRole('button', { name: /delete/i });
    fireEvent.click(deleteButtons[0]);

    // Confirmation modal should appear
    expect(screen.getByText(/are you sure you want to delete/i)).toBeInTheDocument();

    // Confirm deletion
    const confirmButton = screen.getByRole('button', { name: 'Delete' });
    fireEvent.click(confirmButton);

    // Verify API was called
    await waitFor(() => {
      expect(projectsApi.deleteProject).toHaveBeenCalled();
    });
  });

  it('exports project results', async () => {
    const mockProject: Project = {
      project_id: 'project-1',
      user_id: 'user-123',
      status: 'completed',
      job_description_text: 'Python Developer',
      candidate_count: 5,
      created_at: '2025-10-06T12:00:00Z',
      pipeline_start_time: '2025-10-06T12:00:00Z',
      pipeline_end_time: '2025-10-06T12:00:10Z',
      results_json: {
        status: 'success',
        candidates: [],
        ranked_candidates: [],
        outreach_messages: [],
      },
    };

    const mockBlob = new Blob(['test'], { type: 'application/json' });

    vi.mocked(projectsApi.getProject).mockResolvedValue(mockProject);
    vi.mocked(projectsApi.exportProject).mockResolvedValue(mockBlob);

    // Mock URL.createObjectURL
    global.URL.createObjectURL = vi.fn(() => 'blob:test');
    global.URL.revokeObjectURL = vi.fn();

    renderWithRouter('/projects/project-1', <ProjectDetailPage />);

    await waitFor(() => {
      expect(screen.getByText('Completed')).toBeInTheDocument();
    });

    // Click export button
    const exportButton = screen.getByRole('button', { name: /export results/i });
    fireEvent.click(exportButton);

    // Verify export API was called
    await waitFor(() => {
      expect(projectsApi.exportProject).toHaveBeenCalledWith('project-1');
    });
  });

  it('shows empty state when no projects exist', async () => {
    vi.mocked(projectsApi.getProjects).mockResolvedValue({ projects: [], total: 0 });

    renderWithRouter('/projects', <ProjectsPage />);

    await waitFor(() => {
      expect(screen.getByText(/No Projects Found/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/haven't created any projects yet/i)).toBeInTheDocument();
  });
});
