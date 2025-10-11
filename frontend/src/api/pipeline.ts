import apiClient from './client';
import type {
  PipelineRunRequest,
  PipelineRunResponse,
  PipelineStatusResponse,
} from '../types/pipeline';

export const pipelineApi = {
  /**
   * Run the recruitment pipeline
   */
  runPipeline: async (data: PipelineRunRequest): Promise<PipelineRunResponse> => {
    const response = await apiClient.post<PipelineRunResponse>('/pipeline/run', data);
    return response.data;
  },

  /**
   * Get pipeline execution status
   */
  getPipelineStatus: async (projectId: string): Promise<PipelineStatusResponse> => {
    const response = await apiClient.get<PipelineStatusResponse>(`/pipeline/status/${projectId}`);
    return response.data;
  },
};
