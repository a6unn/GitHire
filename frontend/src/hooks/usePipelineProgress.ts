import { useQuery } from '@tanstack/react-query';
import { pipelineApi } from '../api/pipeline';

export const usePipelineProgress = (projectId: string | null, enabled: boolean = true) => {
  return useQuery({
    queryKey: ['pipeline-status', projectId],
    queryFn: () => pipelineApi.getPipelineStatus(projectId!),
    enabled: enabled && !!projectId,
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      // Stop polling when pipeline is completed or failed
      if (status === 'completed' || status === 'failed') {
        return false;
      }
      // Poll every 2 seconds while running
      return 2000;
    },
    refetchOnWindowFocus: false,
  });
};
