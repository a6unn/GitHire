export interface PipelineRunRequest {
  job_description_text: string;
}

export interface Candidate {
  github_username: string;
  profile_url: string;
  repositories: string[];
  programming_languages: string[];
  location: string;
  bio: string;
  contribution_count: number;
  account_age_days: number;
}

export interface RankedCandidate {
  github_username: string;
  total_score: number;
  rank: number;
  domain_score: number;
  score_breakdown: {
    skill_match?: number;
    experience?: number;
    activity?: number;
    matched_skills?: string[];
    missing_skills?: string[];
    [key: string]: number | string[] | undefined;
  };
  strengths: string[];
  concerns: string[];
}

export interface OutreachMessage {
  github_username: string;
  message: string;
  personalization_notes: string;
  subject: string;
}

export interface PipelineMetadata {
  execution_time_seconds: number;
  candidates_found: number;
  candidates_ranked: number;
  messages_generated: number;
  start_time: string;
  end_time: string;
  module_results: Record<string, any>;
}

export interface PipelineRunResponse {
  project_id: string;
  status: string;
  candidates: Candidate[];
  ranked_candidates: RankedCandidate[];
  outreach_messages: OutreachMessage[];
  metadata: PipelineMetadata;
}

export interface PipelineStatusResponse {
  project_id: string;
  status: 'running' | 'completed' | 'failed';
  current_module: string | null;
  progress_percentage: number;
  started_at: string | null;
  completed_at: string | null;
}
