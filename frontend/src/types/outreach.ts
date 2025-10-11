/**
 * TypeScript types for Module 004: Outreach Generator
 *
 * These types correspond to the Pydantic models in src/outreach_generator/models.py
 */

export enum ChannelType {
  EMAIL = 'email',
  LINKEDIN = 'linkedin',
  TWITTER = 'twitter',
}

export enum FollowUpAngle {
  REMINDER = 'reminder',
  TECHNICAL_CHALLENGE = 'technical_challenge',
  CAREER_GROWTH = 'career_growth',
  SOFT_CLOSE = 'soft_close',
}

export interface PersonalizationMetadata {
  referenced_repositories: string[];
  technical_details_mentioned: string[];
  enrichment_data_used: Record<string, string>;
  analysis_insights: {
    achievements: string[];
    passion_areas: string[];
    career_trajectory: string;
    minimal_data_fallback: boolean;
  };
  cliches_removed: string[];
  quality_flags: string[];
}

export interface OutreachMessage {
  shortlist_id: string;
  channel: ChannelType;
  subject_line: string | null;
  message_text: string;
  personalization_score: number; // 0-100
  personalization_metadata: PersonalizationMetadata;
  tokens_used: number;
  stage_breakdown: {
    analysis: number;
    generation: number;
    refinement: number;
    total: number;
  };
  is_edited: boolean;
  generated_at: string; // ISO datetime
  edited_at: string | null; // ISO datetime
}

export interface FollowUpSequence {
  outreach_message_id: string;
  sequence_number: number; // 1-3
  scheduled_days_after: number; // 3, 7, or 14
  message_text: string;
  angle: FollowUpAngle;
  generated_at: string; // ISO datetime
}

export interface GenerateOutreachResponse {
  project_id: string;
  github_username: string;
  messages: OutreachMessage[]; // Can be 1-3 messages (email, LinkedIn, Twitter)
}

export interface GenerateFollowUpsResponse {
  outreach_message_id: string;
  follow_ups: FollowUpSequence[]; // Always 3 follow-ups
}

export interface UpdateOutreachRequest {
  message_text: string;
}

export interface RegenerateOutreachResponse {
  project_id: string;
  github_username: string;
  channel: ChannelType;
  message: OutreachMessage;
}
