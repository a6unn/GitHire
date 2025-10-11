import apiClient from './client';
import type { Project, ProjectsResponse, ProjectFilters, CreateProjectRequest, QuickStartParseResponse } from '../types/project';
import type {
  GenerateOutreachResponse,
  GenerateFollowUpsResponse,
  OutreachMessage,
  UpdateOutreachRequest,
  RegenerateOutreachResponse,
  ChannelType,
} from '../types/outreach';

// Re-export types for convenience
export type { QuickStartParseResponse };

export const projectsApi = {
  /**
   * Parse quick-start text into structured project fields
   */
  parseQuickStart: async (quickText: string): Promise<QuickStartParseResponse> => {
    const response = await apiClient.post<QuickStartParseResponse>('/projects/quick-start/parse', {
      quick_text: quickText,
    });
    return response.data;
  },

  /**
   * Create a new project
   */
  createProject: async (data: CreateProjectRequest): Promise<Project> => {
    const response = await apiClient.post<Project>('/projects', data);
    return response.data;
  },

  /**
   * Get all projects for the authenticated user
   */
  getProjects: async (filters?: ProjectFilters): Promise<ProjectsResponse> => {
    const params = new URLSearchParams();

    if (filters?.status) {
      params.append('status', filters.status);
    }
    if (filters?.limit) {
      params.append('limit', filters.limit.toString());
    }
    if (filters?.offset) {
      params.append('offset', filters.offset.toString());
    }

    const queryString = params.toString();
    const url = `/projects${queryString ? `?${queryString}` : ''}`;

    const response = await apiClient.get<ProjectsResponse>(url);
    return response.data;
  },

  /**
   * Get a single project by ID
   */
  getProject: async (projectId: string): Promise<Project> => {
    const response = await apiClient.get<Project>(`/projects/${projectId}`);
    return response.data;
  },

  /**
   * Delete a project
   */
  deleteProject: async (projectId: string): Promise<{ message: string }> => {
    const response = await apiClient.delete<{ message: string }>(`/projects/${projectId}`);
    return response.data;
  },

  /**
   * Export project results as JSON
   */
  exportProject: async (projectId: string): Promise<Blob> => {
    const response = await apiClient.get(`/projects/${projectId}/export`, {
      responseType: 'blob',
    });
    return response.data;
  },

  /**
   * Source candidates for a project (Stage 1)
   */
  sourceCandidates: async (projectId: string): Promise<any> => {
    const response = await apiClient.post(`/projects/${projectId}/source`);
    return response.data;
  },

  /**
   * Rank candidates for a project (Stage 2)
   */
  rankCandidates: async (projectId: string): Promise<any> => {
    const response = await apiClient.post(`/projects/${projectId}/rank`);
    return response.data;
  },

  /**
   * Shortlist candidates for a project (Stage 3)
   */
  shortlistCandidates: async (projectId: string, candidateUsernames: string[]): Promise<any> => {
    const response = await apiClient.post(`/projects/${projectId}/shortlist`, {
      candidate_usernames: candidateUsernames,
    });
    return response.data;
  },

  /**
   * Get shortlisted candidates for a project
   */
  getShortlist: async (projectId: string): Promise<any[]> => {
    const response = await apiClient.get(`/projects/${projectId}/shortlist`);
    return response.data;
  },

  /**
   * Reset project to draft status
   */
  resetProject: async (projectId: string): Promise<any> => {
    const response = await apiClient.post(`/projects/${projectId}/reset`);
    return response.data;
  },

  /**
   * Toggle shortlist status for a single candidate
   */
  toggleShortlist: async (projectId: string, githubUsername: string): Promise<{
    project_id: string;
    github_username: string;
    is_shortlisted: boolean;
    shortlisted_count: number;
  }> => {
    const response = await apiClient.post(`/projects/${projectId}/shortlist/${githubUsername}/toggle`);
    return response.data;
  },

  /**
   * Enrich a shortlisted candidate with contact information
   */
  enrichCandidate: async (projectId: string, githubUsername: string): Promise<{
    shortlist_id: string;
    github_username: string;
    enrichment_status: string;
    enriched_data: any;
    enriched_at: string;
  }> => {
    const response = await apiClient.post(`/projects/${projectId}/shortlist/${githubUsername}/enrich`);
    return response.data;
  },

  // ============================================================================
  // Module 004: Outreach Generator API Functions
  // ============================================================================

  /**
   * Generate outreach messages for a shortlisted candidate (Module 004)
   */
  generateOutreach: async (projectId: string, githubUsername: string): Promise<GenerateOutreachResponse> => {
    const response = await apiClient.post<GenerateOutreachResponse>(
      `/projects/${projectId}/shortlist/${githubUsername}/outreach`
    );
    return response.data;
  },

  /**
   * Get existing outreach messages for a candidate
   */
  getOutreach: async (projectId: string, githubUsername: string): Promise<OutreachMessage[]> => {
    const response = await apiClient.get<OutreachMessage[]>(
      `/projects/${projectId}/shortlist/${githubUsername}/outreach`
    );
    return response.data;
  },

  /**
   * Update (edit) an outreach message
   */
  updateOutreach: async (
    projectId: string,
    githubUsername: string,
    messageId: string,
    data: UpdateOutreachRequest
  ): Promise<OutreachMessage> => {
    const response = await apiClient.put<OutreachMessage>(
      `/projects/${projectId}/shortlist/${githubUsername}/outreach/${messageId}`,
      data
    );
    return response.data;
  },

  /**
   * Regenerate an outreach message for a specific channel
   */
  regenerateOutreach: async (
    projectId: string,
    githubUsername: string,
    messageId: string
  ): Promise<RegenerateOutreachResponse> => {
    const response = await apiClient.post<RegenerateOutreachResponse>(
      `/projects/${projectId}/shortlist/${githubUsername}/outreach/${messageId}/regenerate`
    );
    return response.data;
  },

  /**
   * Generate follow-up sequences for an outreach message
   */
  generateFollowUps: async (
    projectId: string,
    githubUsername: string,
    messageId: string
  ): Promise<GenerateFollowUpsResponse> => {
    const response = await apiClient.post<GenerateFollowUpsResponse>(
      `/projects/${projectId}/shortlist/${githubUsername}/outreach/${messageId}/follow-ups`
    );
    return response.data;
  },

  /**
   * Get follow-up sequences for an outreach message
   */
  getFollowUps: async (
    projectId: string,
    githubUsername: string,
    messageId: string
  ): Promise<any[]> => {
    const response = await apiClient.get(
      `/projects/${projectId}/shortlist/${githubUsername}/outreach/${messageId}/follow-ups`
    );
    return response.data;
  },
};
