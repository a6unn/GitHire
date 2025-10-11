export type ProjectStatus =
  | 'draft'
  | 'sourcing'
  | 'sourced'
  | 'ranking'
  | 'ranked'
  | 'shortlisted'
  | 'running'  // Legacy
  | 'completed'  // Legacy
  | 'failed';  // Legacy

export interface Project {
  project_id: string;
  user_id: string;
  name: string | null;
  job_title: string | null;
  status: ProjectStatus;
  job_description_text: string;
  location?: string | null;
  candidate_count: number;
  avg_score: number | null;
  created_at: string;
  updated_at: string;
  pipeline_start_time: string | null;
  pipeline_end_time: string | null;
  results_json?: {
    status?: string;
    candidates?: any[];
    ranked_candidates?: any[];
    outreach_messages?: any[];
    metadata?: any;
  };
}

export interface ProjectListItem {
  project_id: string;
  name: string | null;
  job_title: string | null;
  status: ProjectStatus;
  job_description_text: string;
  candidate_count: number;
  created_at: string;
  updated_at: string;
  pipeline_start_time: string | null;
  pipeline_end_time: string | null;
}

export interface ProjectsResponse {
  projects: ProjectListItem[];
  total: number;
}

export interface ProjectFilters {
  status?: ProjectStatus;
  limit?: number;
  offset?: number;
}

export interface CreateProjectRequest {
  name: string;
  job_title: string;
  job_description_text: string;
  location?: string;
}

export interface QuickStartParseResponse {
  project_name: string;
  job_title: string;
  location: string | null;
  skills: string[];
  experience_years: string | null;
  job_description_text: string;
}
