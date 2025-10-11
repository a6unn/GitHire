import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import {
  ArrowLeftIcon,
  SparklesIcon,
  EnvelopeIcon,
  CheckCircleIcon,
  ClockIcon,
  XMarkIcon,
  ChevronDownIcon,
  ChevronUpIcon,
} from '@heroicons/react/24/outline';
import { projectsApi } from '../api/projects';
import { useToast } from '../contexts/ToastContext';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { EmptyState } from '../components/ui/EmptyState';
import { Skeleton } from '../components/ui/Skeleton';
import { OutreachPanel } from '../components/OutreachPanel';
import { FollowUpPanel } from '../components/FollowUpPanel';

interface ShortlistedCandidate {
  shortlist_id: string;
  project_id: string;
  github_username: string;
  candidate_data: any;
  enriched_data?: any;
  enrichment_status: string;
  enriched_at?: string;
  created_at: string;
}

// Wrapper component that fetches outreach messages and passes to both panels
const OutreachSectionWrapper: React.FC<{
  projectId: string;
  githubUsername: string;
  isEnriched: boolean;
}> = ({ projectId, githubUsername, isEnriched }) => {
  const queryClient = useQueryClient();
  const [selectedChannel, setSelectedChannel] = useState<'email' | 'linkedin' | 'twitter'>('email');

  // Fetch outreach messages
  const { data: outreachMessages } = useQuery({
    queryKey: ['outreach', projectId, githubUsername],
    queryFn: () => projectsApi.getOutreach(projectId, githubUsername),
    enabled: isEnriched,
  });

  return (
    <div className="pt-6 border-t border-gray-200 space-y-6 animate-slide-in">
      {/* Outreach Panel */}
      <OutreachPanel
        projectId={projectId}
        githubUsername={githubUsername}
        isEnriched={isEnriched}
        selectedChannel={selectedChannel}
        onChannelChange={setSelectedChannel}
        onFollowUpsGenerated={() => {
          // Refresh to show follow-ups
          queryClient.invalidateQueries({ queryKey: ['follow-ups', projectId, githubUsername] });
        }}
      />

      {/* Follow-Up Panel */}
      <FollowUpPanel
        projectId={projectId}
        githubUsername={githubUsername}
        outreachMessages={outreachMessages || []}
        selectedChannel={selectedChannel}
      />
    </div>
  );
};

export const ShortlistedCandidatesPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { showToast } = useToast();
  const [expandedCard, setExpandedCard] = useState<string | null>(null);
  const [outreachExpandedCard, setOutreachExpandedCard] = useState<string | null>(null);

  const { data: project, isLoading: isLoadingProject } = useQuery({
    queryKey: ['project', projectId],
    queryFn: () => projectsApi.getProject(projectId!),
    enabled: !!projectId,
  });

  const { data: shortlistedCandidates, isLoading: isLoadingShortlist } = useQuery({
    queryKey: ['shortlist', projectId],
    queryFn: () => projectsApi.getShortlist(projectId!),
    enabled: !!projectId,
  });

  const handleEnrich = async (username: string) => {
    if (!projectId) return;

    try {
      showToast('Enriching candidate profile...', 'info');
      await projectsApi.enrichCandidate(projectId, username);
      queryClient.invalidateQueries({ queryKey: ['shortlist', projectId] });
      showToast('Candidate profile enriched successfully!', 'success');
    } catch (error: any) {
      console.error('Enrichment failed:', error);
      showToast(error.response?.data?.detail || 'Failed to enrich candidate profile', 'error');
    }
  };

  const handleToggleOutreach = (shortlistId: string) => {
    setOutreachExpandedCard(outreachExpandedCard === shortlistId ? null : shortlistId);
  };

  const handleUnshortlist = async (username: string) => {
    if (!projectId) return;

    try {
      await projectsApi.toggleShortlist(projectId, username);
      queryClient.invalidateQueries({ queryKey: ['shortlist', projectId] });
      queryClient.invalidateQueries({ queryKey: ['project', projectId] });
      showToast('Candidate removed from shortlist', 'success');
    } catch (error: any) {
      console.error('Unshortlist failed:', error);
      showToast(error.response?.data?.detail || 'Failed to remove from shortlist', 'error');
    }
  };

  if (isLoadingProject || isLoadingShortlist) {
    return (
      <div className="space-y-8 animate-fade-in">
        <Skeleton variant="rectangular" height="60px" />
        <Skeleton variant="rectangular" height="400px" />
      </div>
    );
  }

  if (!project) {
    return (
      <EmptyState
        icon={<CheckCircleIcon className="h-12 w-12" />}
        title="Project Not Found"
        description="The project you're looking for doesn't exist or has been deleted."
        action={{
          label: 'Back to Projects',
          onClick: () => navigate('/projects'),
        }}
      />
    );
  }

  const candidates = (shortlistedCandidates || []) as ShortlistedCandidate[];

  if (candidates.length === 0) {
    return (
      <div className="space-y-8 animate-fade-in">
        <Button
          onClick={() => navigate(`/projects/${projectId}`)}
          variant="ghost"
          leftIcon={<ArrowLeftIcon className="h-4 w-4" />}
        >
          Back to Project
        </Button>

        <EmptyState
          icon={<CheckCircleIcon className="h-12 w-12" />}
          title="No Shortlisted Candidates"
          description="You haven't shortlisted any candidates yet. Go back to the project and shortlist candidates first."
          action={{
            label: 'Back to Project',
            onClick: () => navigate(`/projects/${projectId}`),
          }}
        />
      </div>
    );
  }

  const getEnrichmentBadge = (status: string) => {
    switch (status) {
      case 'completed':
        return <Badge variant="success">Enriched</Badge>;
      case 'in_progress':
        return <Badge variant="warning">Enriching...</Badge>;
      case 'failed':
        return <Badge variant="danger">Failed</Badge>;
      default:
        return <Badge variant="default">Pending</Badge>;
    }
  };

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Back Button */}
      <Button
        onClick={() => navigate(`/projects/${projectId}`)}
        variant="ghost"
        leftIcon={<ArrowLeftIcon className="h-4 w-4" />}
      >
        Back to Project
      </Button>

      {/* Header */}
      <Card variant="elevated" padding="lg">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Shortlisted Candidates
            </h1>
            <p className="text-gray-600">
              {project.name || project.job_title || 'Untitled Project'} • {candidates.length} candidate{candidates.length !== 1 ? 's' : ''} shortlisted
            </p>
          </div>
        </div>
      </Card>

      {/* Candidates List */}
      <div className="space-y-4">
        {candidates.map((shortlisted) => {
          const candidate = shortlisted.candidate_data;
          const isExpanded = expandedCard === shortlisted.shortlist_id;

          const getScoreColor = (score: number) => {
            if (score >= 80) return 'text-green-600 bg-green-100';
            if (score >= 60) return 'text-yellow-600 bg-yellow-100';
            return 'text-orange-600 bg-orange-100';
          };

          return (
            <Card
              key={shortlisted.shortlist_id}
              variant="elevated"
              padding="lg"
              className="transition-all hover:shadow-lg"
            >
              <div className="space-y-4">
                {/* Header */}
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-start gap-4 flex-1">
                    {/* Rank Badge */}
                    {candidate.rank && (
                      <div className="flex-shrink-0">
                        <div className="w-12 h-12 rounded-full bg-primary-100 flex items-center justify-center">
                          <span className="text-xl font-bold text-primary-600">#{candidate.rank}</span>
                        </div>
                      </div>
                    )}

                    {/* Candidate Info */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-3 mb-1">
                        <a
                          href={`https://github.com/${candidate.github_username}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-xl font-semibold text-gray-900 hover:text-primary-600"
                        >
                          {candidate.github_username}
                        </a>
                        {candidate.total_score !== undefined && (
                          <span className={`px-3 py-1 rounded-full text-sm font-semibold ${getScoreColor(candidate.total_score)}`}>
                            {Math.round(candidate.total_score)}%
                          </span>
                        )}
                      </div>
                      {candidate.name && (
                        <p className="text-sm text-gray-600 mb-2">{candidate.name}</p>
                      )}
                      {candidate.bio && (
                        <p className="text-gray-700 mb-3">{candidate.bio}</p>
                      )}
                    </div>
                  </div>

                  {/* Enrichment Status */}
                  <div className="flex-shrink-0">
                    {getEnrichmentBadge(shortlisted.enrichment_status)}
                  </div>
                </div>

                {/* Stats */}
                <div className="flex flex-wrap gap-4 text-sm text-gray-600">
                  {candidate.location && (
                    <div className="flex items-center gap-1">
                      <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                      </svg>
                      {candidate.location}
                    </div>
                  )}
                  {candidate.followers !== undefined && (
                    <div className="flex items-center gap-1">
                      <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                      </svg>
                      {candidate.followers} followers
                    </div>
                  )}
                  {candidate.public_repos !== undefined && (
                    <div className="flex items-center gap-1">
                      <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                      </svg>
                      {candidate.public_repos} repos
                    </div>
                  )}
                  <div className="flex items-center gap-1 text-gray-500">
                    <ClockIcon className="h-4 w-4" />
                    Shortlisted {new Date(shortlisted.created_at).toLocaleDateString()}
                  </div>
                </div>

                {/* Skills */}
                {candidate.matched_skills && candidate.matched_skills.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {candidate.matched_skills.slice(0, 8).map((skill: string) => (
                      <span
                        key={skill}
                        className="px-2 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded"
                      >
                        {skill}
                      </span>
                    ))}
                    {candidate.matched_skills.length > 8 && (
                      <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs font-medium rounded">
                        +{candidate.matched_skills.length - 8} more
                      </span>
                    )}
                  </div>
                )}

                {/* Action Buttons */}
                <div className="flex gap-3 pt-4 border-t border-gray-200">
                  <Button
                    onClick={() => handleUnshortlist(candidate.github_username)}
                    variant="danger"
                    size="sm"
                    leftIcon={<XMarkIcon className="h-4 w-4" />}
                  >
                    Unshortlist
                  </Button>
                  <Button
                    onClick={() => handleEnrich(candidate.github_username)}
                    variant="secondary"
                    size="sm"
                    leftIcon={<SparklesIcon className="h-4 w-4" />}
                    disabled={shortlisted.enrichment_status === 'completed'}
                  >
                    {shortlisted.enrichment_status === 'completed' ? 'Enriched' : 'Enrich Profile'}
                  </Button>
                  <Button
                    onClick={() => handleToggleOutreach(shortlisted.shortlist_id)}
                    variant="primary"
                    size="sm"
                    leftIcon={<EnvelopeIcon className="h-4 w-4" />}
                    rightIcon={outreachExpandedCard === shortlisted.shortlist_id ? <ChevronUpIcon className="h-4 w-4" /> : <ChevronDownIcon className="h-4 w-4" />}
                  >
                    {outreachExpandedCard === shortlisted.shortlist_id ? 'Hide Outreach' : 'Generate Outreach'}
                  </Button>
                  <Button
                    onClick={() => setExpandedCard(isExpanded ? null : shortlisted.shortlist_id)}
                    variant="ghost"
                    size="sm"
                  >
                    {isExpanded ? 'Hide' : 'View'} Details
                  </Button>
                </div>

                {/* Expanded Details */}
                {isExpanded && (
                  <div className="pt-4 border-t border-gray-200 space-y-4 animate-slide-in">
                    {/* Score Breakdown */}
                    {candidate.score_breakdown && (
                      <div>
                        <h4 className="font-semibold text-gray-900 mb-2">Score Breakdown</h4>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                          {candidate.skill_match_score !== undefined && (
                            <div className="bg-gray-50 p-3 rounded">
                              <div className="text-sm text-gray-600">Skill Match</div>
                              <div className="text-2xl font-bold text-gray-900">{Math.round(candidate.skill_match_score)}%</div>
                            </div>
                          )}
                          {candidate.activity_score !== undefined && (
                            <div className="bg-gray-50 p-3 rounded">
                              <div className="text-sm text-gray-600">Activity</div>
                              <div className="text-2xl font-bold text-gray-900">{Math.round(candidate.activity_score)}%</div>
                            </div>
                          )}
                          {candidate.experience_score !== undefined && (
                            <div className="bg-gray-50 p-3 rounded">
                              <div className="text-sm text-gray-600">Experience</div>
                              <div className="text-2xl font-bold text-gray-900">{Math.round(candidate.experience_score)}%</div>
                            </div>
                          )}
                          {candidate.domain_score !== undefined && (
                            <div className="bg-gray-50 p-3 rounded">
                              <div className="text-sm text-gray-600">Domain</div>
                              <div className="text-2xl font-bold text-gray-900">{Math.round(candidate.domain_score)}%</div>
                            </div>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Enriched Data (if available) */}
                    {shortlisted.enriched_data && (
                      <div>
                        <h4 className="font-semibold text-gray-900 mb-2">Contact Information</h4>
                        <div className="bg-green-50 p-4 rounded border border-green-200 space-y-3">
                          <p className="text-xs text-green-700 mb-2">
                            Enriched on {new Date(shortlisted.enriched_at!).toLocaleString()}
                          </p>

                          {shortlisted.enriched_data.primary_email && (
                            <div className="flex items-start gap-2">
                              <span className="text-sm font-medium text-gray-700">📧 Email:</span>
                              <span className="text-sm text-gray-900">{shortlisted.enriched_data.primary_email}</span>
                            </div>
                          )}

                          {shortlisted.enriched_data.additional_emails && shortlisted.enriched_data.additional_emails.length > 0 && (
                            <div className="flex items-start gap-2">
                              <span className="text-sm font-medium text-gray-700">📧 Alt Emails:</span>
                              <div className="text-sm text-gray-900">
                                {shortlisted.enriched_data.additional_emails.slice(0, 3).join(', ')}
                                {shortlisted.enriched_data.additional_emails.length > 3 && ` +${shortlisted.enriched_data.additional_emails.length - 3} more`}
                              </div>
                            </div>
                          )}

                          {shortlisted.enriched_data.linkedin_username && (
                            <div className="flex items-start gap-2">
                              <span className="text-sm font-medium text-gray-700">💼 LinkedIn:</span>
                              <a
                                href={`https://linkedin.com/in/${shortlisted.enriched_data.linkedin_username}`}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-sm text-blue-600 hover:underline"
                              >
                                linkedin.com/in/{shortlisted.enriched_data.linkedin_username}
                              </a>
                            </div>
                          )}

                          {shortlisted.enriched_data.twitter_username && (
                            <div className="flex items-start gap-2">
                              <span className="text-sm font-medium text-gray-700">🐦 Twitter:</span>
                              <a
                                href={`https://twitter.com/${shortlisted.enriched_data.twitter_username}`}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-sm text-blue-600 hover:underline"
                              >
                                @{shortlisted.enriched_data.twitter_username}
                              </a>
                            </div>
                          )}

                          {shortlisted.enriched_data.blog_url && (
                            <div className="flex items-start gap-2">
                              <span className="text-sm font-medium text-gray-700">🌐 Website:</span>
                              <a
                                href={shortlisted.enriched_data.blog_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-sm text-blue-600 hover:underline"
                              >
                                {shortlisted.enriched_data.blog_url}
                              </a>
                            </div>
                          )}

                          {!shortlisted.enriched_data.primary_email &&
                           !shortlisted.enriched_data.linkedin_username &&
                           !shortlisted.enriched_data.twitter_username &&
                           !shortlisted.enriched_data.blog_url && (
                            <p className="text-sm text-gray-600">No additional contact information found</p>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* Outreach Section */}
                {outreachExpandedCard === shortlisted.shortlist_id && (
                  <OutreachSectionWrapper
                    projectId={projectId!}
                    githubUsername={candidate.github_username}
                    isEnriched={shortlisted.enrichment_status === 'completed'}
                  />
                )}
              </div>
            </Card>
          );
        })}
      </div>

      {/* Info Banner */}
      <Card variant="bordered" padding="lg" className="bg-blue-50 border-blue-200">
        <div className="flex items-start gap-3">
          <div className="flex-shrink-0">
            <svg className="h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div>
            <h4 className="font-semibold text-blue-900 mb-1">Next Steps</h4>
            <p className="text-sm text-blue-800">
              Use the "Enrich Profile" button to gather additional data about candidates,
              then generate personalized outreach messages to contact them.
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
};
