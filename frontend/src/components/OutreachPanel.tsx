import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  EnvelopeIcon,
  ArrowPathIcon,
  PencilIcon,
  CheckIcon,
  XMarkIcon,
  SparklesIcon,
  ChartBarIcon,
  ClipboardDocumentIcon,
  ClipboardDocumentCheckIcon,
} from '@heroicons/react/24/outline';
import { projectsApi } from '../api/projects';
import { useToast } from '../contexts/ToastContext';
import { Button } from './ui/Button';
import { Card } from './ui/Card';
import { Badge } from './ui/Badge';
import type { OutreachMessage, ChannelType } from '../types/outreach';

interface OutreachPanelProps {
  projectId: string;
  githubUsername: string;
  isEnriched: boolean;
  selectedChannel?: Channel;
  onChannelChange?: (channel: Channel) => void;
  onFollowUpsGenerated?: () => void;
}

type Channel = 'email' | 'linkedin' | 'twitter';

const CHANNEL_CONFIG: Record<Channel, { icon: string; label: string; color: string }> = {
  email: { icon: '📧', label: 'Email', color: 'blue' },
  linkedin: { icon: '💼', label: 'LinkedIn', color: 'indigo' },
  twitter: { icon: '🐦', label: 'X (Twitter)', color: 'sky' },
};

export const OutreachPanel: React.FC<OutreachPanelProps> = ({
  projectId,
  githubUsername,
  isEnriched,
  selectedChannel: externalSelectedChannel,
  onChannelChange,
  onFollowUpsGenerated,
}) => {
  const { showToast } = useToast();
  const queryClient = useQueryClient();
  const [internalSelectedChannel, setInternalSelectedChannel] = useState<Channel>('email');
  const [editingMessageId, setEditingMessageId] = useState<string | null>(null);
  const [editedText, setEditedText] = useState('');
  const [copiedField, setCopiedField] = useState<string | null>(null);

  // Use external state if provided, otherwise use internal state
  const selectedChannel = externalSelectedChannel !== undefined ? externalSelectedChannel : internalSelectedChannel;
  const handleChannelChange = (channel: Channel) => {
    if (onChannelChange) {
      onChannelChange(channel);
    } else {
      setInternalSelectedChannel(channel);
    }
  };

  // Fetch outreach messages
  const { data: messages, isLoading } = useQuery({
    queryKey: ['outreach', projectId, githubUsername],
    queryFn: () => projectsApi.getOutreach(projectId, githubUsername),
    enabled: isEnriched,
  });

  // Generate outreach mutation
  const generateMutation = useMutation({
    mutationFn: () => projectsApi.generateOutreach(projectId, githubUsername),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['outreach', projectId, githubUsername] });
      showToast('Outreach messages generated successfully!', 'success');
    },
    onError: (error: any) => {
      showToast(error.response?.data?.detail || 'Failed to generate outreach', 'error');
    },
  });

  // Update outreach mutation
  const updateMutation = useMutation({
    mutationFn: ({ messageId, text }: { messageId: string; text: string }) =>
      projectsApi.updateOutreach(projectId, githubUsername, messageId, { message_text: text }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['outreach', projectId, githubUsername] });
      showToast('Message updated successfully!', 'success');
      setEditingMessageId(null);
    },
    onError: (error: any) => {
      showToast(error.response?.data?.detail || 'Failed to update message', 'error');
    },
  });

  // Regenerate outreach mutation
  const regenerateMutation = useMutation({
    mutationFn: (messageId: string) =>
      projectsApi.regenerateOutreach(projectId, githubUsername, messageId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['outreach', projectId, githubUsername] });
      showToast('Message regenerated successfully!', 'success');
    },
    onError: (error: any) => {
      showToast(error.response?.data?.detail || 'Failed to regenerate message', 'error');
    },
  });

  // Generate follow-ups mutation
  const generateFollowUpsMutation = useMutation({
    mutationFn: (messageId: string) =>
      projectsApi.generateFollowUps(projectId, githubUsername, messageId),
    onSuccess: (_, messageId) => {
      // Invalidate all follow-ups queries for this candidate to ensure refetch
      queryClient.invalidateQueries({ queryKey: ['follow-ups', projectId, githubUsername] });
      showToast('Follow-up sequence generated successfully!', 'success');
      onFollowUpsGenerated?.();
    },
    onError: (error: any) => {
      showToast(error.response?.data?.detail || 'Failed to generate follow-ups', 'error');
    },
  });

  if (!isEnriched) {
    return (
      <Card variant="bordered" padding="lg" className="bg-yellow-50 border-yellow-200">
        <div className="flex items-start gap-3">
          <div className="flex-shrink-0">
            <SparklesIcon className="h-6 w-6 text-yellow-600" />
          </div>
          <div>
            <h4 className="font-semibold text-yellow-900 mb-1">Enrichment Required</h4>
            <p className="text-sm text-yellow-800">
              Please enrich this candidate's profile first to generate personalized outreach messages.
            </p>
          </div>
        </div>
      </Card>
    );
  }

  const messagesArray = (messages || []) as OutreachMessage[];
  const currentMessage = messagesArray.find((m) => m.channel === selectedChannel);

  const getPersonalizationColor = (score: number) => {
    if (score >= 80) return 'text-green-600 bg-green-100';
    if (score >= 60) return 'text-yellow-600 bg-yellow-100';
    return 'text-orange-600 bg-orange-100';
  };

  const handleEdit = (message: OutreachMessage) => {
    setEditingMessageId(message.outreach_id);
    setEditedText(message.is_edited && message.edited_message ? message.edited_message : message.message_text);
  };

  const handleSaveEdit = (messageId: string) => {
    updateMutation.mutate({ messageId, text: editedText });
  };

  const handleCancelEdit = () => {
    setEditingMessageId(null);
    setEditedText('');
  };

  const handleCopy = async (text: string, field: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedField(field);
      setTimeout(() => setCopiedField(null), 2000);
    } catch (err) {
      console.error('Failed to copy text:', err);
    }
  };

  return (
    <Card variant="elevated" padding="lg" className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <EnvelopeIcon className="h-6 w-6 text-primary-600" />
          <h3 className="text-xl font-bold text-gray-900">Outreach Messages</h3>
        </div>
        {messagesArray.length === 0 ? (
          <Button
            onClick={() => generateMutation.mutate()}
            variant="primary"
            size="sm"
            leftIcon={<SparklesIcon className="h-4 w-4" />}
            isLoading={generateMutation.isPending}
          >
            Generate Outreach
          </Button>
        ) : (
          <Badge variant="success">
            {messagesArray.length} channel{messagesArray.length !== 1 ? 's' : ''}
          </Badge>
        )}
      </div>

      {isLoading ? (
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
          <p className="text-sm text-gray-600 mt-2">Loading messages...</p>
        </div>
      ) : messagesArray.length === 0 ? (
        <div className="text-center py-8 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
          <EnvelopeIcon className="h-12 w-12 text-gray-400 mx-auto mb-3" />
          <p className="text-gray-600 mb-1">No outreach messages yet</p>
          <p className="text-sm text-gray-500">Click "Generate Outreach" to create personalized messages</p>
        </div>
      ) : (
        <>
          {/* Channel Tabs */}
          <div className="flex gap-2 border-b border-gray-200">
            {Object.entries(CHANNEL_CONFIG).map(([channel, config]) => {
              const hasMessage = messagesArray.some((m) => m.channel === channel);
              const isSelected = selectedChannel === channel;

              return (
                <button
                  key={channel}
                  onClick={() => hasMessage && handleChannelChange(channel as Channel)}
                  disabled={!hasMessage}
                  className={`flex items-center gap-2 px-4 py-2 font-medium transition-all ${
                    isSelected
                      ? `text-${config.color}-600 border-b-2 border-${config.color}-600`
                      : hasMessage
                      ? 'text-gray-600 hover:text-gray-900'
                      : 'text-gray-400 cursor-not-allowed'
                  }`}
                >
                  <span className="text-lg">{config.icon}</span>
                  {config.label}
                  {hasMessage && isSelected && (
                    <span className="w-2 h-2 rounded-full bg-green-500"></span>
                  )}
                </button>
              );
            })}
          </div>

          {/* Message Content */}
          {currentMessage && (
            <div className="space-y-4">
              {/* Personalization Score */}
              <div className="flex items-center justify-between p-4 bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg border border-purple-200">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-white rounded-full shadow-sm">
                    <ChartBarIcon className="h-5 w-5 text-purple-600" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-700">Personalization Score</p>
                    <div className="flex items-center gap-2 mt-1">
                      <div className="w-32 h-2 bg-gray-200 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-purple-500 to-pink-500"
                          style={{ width: `${currentMessage.personalization_score}%` }}
                        ></div>
                      </div>
                      <span className={`px-2 py-0.5 rounded text-xs font-semibold ${getPersonalizationColor(currentMessage.personalization_score)}`}>
                        {Math.round(currentMessage.personalization_score)}%
                      </span>
                    </div>
                  </div>
                </div>
                <div className="text-right text-xs text-gray-600">
                  <p>{currentMessage.tokens_used} tokens used</p>
                  {currentMessage.is_edited && (
                    <Badge variant="default" className="mt-1">Edited</Badge>
                  )}
                </div>
              </div>

              {/* Subject Line (Email only) */}
              {currentMessage.subject_line && (
                <div className="space-y-1">
                  <label className="text-sm font-medium text-gray-700">Subject Line</label>
                  <div className="relative p-3 bg-gray-50 rounded border border-gray-200 group">
                    <p className="text-gray-900 font-medium pr-8">{currentMessage.subject_line}</p>
                    <button
                      onClick={() => handleCopy(currentMessage.subject_line!, `subject-${currentMessage.outreach_id}`)}
                      className="absolute top-2 right-2 p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded transition-colors opacity-0 group-hover:opacity-100"
                      title="Copy subject"
                    >
                      {copiedField === `subject-${currentMessage.outreach_id}` ? (
                        <ClipboardDocumentCheckIcon className="h-4 w-4 text-green-600" />
                      ) : (
                        <ClipboardDocumentIcon className="h-4 w-4" />
                      )}
                    </button>
                  </div>
                </div>
              )}

              {/* Message Body */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <label className="text-sm font-medium text-gray-700">Message</label>
                  <div className="flex gap-2">
                    {editingMessageId !== currentMessage.outreach_id && (
                      <>
                        <Button
                          onClick={() => handleEdit(currentMessage)}
                          variant="ghost"
                          size="sm"
                          leftIcon={<PencilIcon className="h-4 w-4" />}
                        >
                          Edit
                        </Button>
                        <Button
                          onClick={() => regenerateMutation.mutate(currentMessage.outreach_id)}
                          variant="secondary"
                          size="sm"
                          leftIcon={<ArrowPathIcon className="h-4 w-4" />}
                          isLoading={regenerateMutation.isPending}
                        >
                          Regenerate
                        </Button>
                      </>
                    )}
                  </div>
                </div>

                {editingMessageId === currentMessage.outreach_id ? (
                  <div className="space-y-2">
                    <textarea
                      value={editedText}
                      onChange={(e) => setEditedText(e.target.value)}
                      rows={12}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    />
                    <div className="flex gap-2">
                      <Button
                        onClick={() => handleSaveEdit(currentMessage.outreach_id)}
                        variant="primary"
                        size="sm"
                        leftIcon={<CheckIcon className="h-4 w-4" />}
                        isLoading={updateMutation.isPending}
                      >
                        Save Changes
                      </Button>
                      <Button
                        onClick={handleCancelEdit}
                        variant="secondary"
                        size="sm"
                        leftIcon={<XMarkIcon className="h-4 w-4" />}
                      >
                        Cancel
                      </Button>
                    </div>
                  </div>
                ) : (
                  <div className="relative p-4 bg-white border-2 border-gray-200 rounded-lg whitespace-pre-wrap font-sans text-gray-900 group">
                    <div className="pr-8">
                      {currentMessage.is_edited && currentMessage.edited_message
                        ? currentMessage.edited_message
                        : currentMessage.message_text}
                    </div>
                    <button
                      onClick={() => handleCopy(
                        currentMessage.is_edited && currentMessage.edited_message
                          ? currentMessage.edited_message
                          : currentMessage.message_text,
                        `message-${currentMessage.outreach_id}`
                      )}
                      className="absolute top-2 right-2 p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded transition-colors opacity-0 group-hover:opacity-100"
                      title="Copy message"
                    >
                      {copiedField === `message-${currentMessage.outreach_id}` ? (
                        <ClipboardDocumentCheckIcon className="h-4 w-4 text-green-600" />
                      ) : (
                        <ClipboardDocumentIcon className="h-4 w-4" />
                      )}
                    </button>
                  </div>
                )}
              </div>

              {/* Personalization Metadata */}
              <details className="group">
                <summary className="cursor-pointer text-sm font-medium text-gray-700 hover:text-primary-600 flex items-center gap-2">
                  <svg className="w-4 h-4 transition-transform group-open:rotate-90" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                  View Personalization Details
                </summary>
                <div className="mt-3 p-4 bg-gray-50 rounded-lg space-y-3 text-sm">
                  {currentMessage.personalization_metadata.referenced_repositories?.length > 0 && (
                    <div>
                      <p className="font-medium text-gray-700 mb-1">Referenced Repositories:</p>
                      <div className="flex flex-wrap gap-2">
                        {currentMessage.personalization_metadata.referenced_repositories.map((repo: string) => (
                          <Badge key={repo} variant="default">{repo}</Badge>
                        ))}
                      </div>
                    </div>
                  )}
                  {currentMessage.personalization_metadata.technical_details_mentioned?.length > 0 && (
                    <div>
                      <p className="font-medium text-gray-700 mb-1">Technical Details:</p>
                      <div className="flex flex-wrap gap-2">
                        {currentMessage.personalization_metadata.technical_details_mentioned.map((detail: string) => (
                          <Badge key={detail} variant="default">{detail}</Badge>
                        ))}
                      </div>
                    </div>
                  )}
                  {currentMessage.personalization_metadata.cliches_removed?.length > 0 && (
                    <div>
                      <p className="font-medium text-gray-700 mb-1">Clichés Removed:</p>
                      <p className="text-gray-600">{currentMessage.personalization_metadata.cliches_removed.length} generic phrases removed</p>
                    </div>
                  )}
                </div>
              </details>

              {/* Generate Follow-ups Button */}
              <div className="pt-4 border-t border-gray-200">
                <Button
                  onClick={() => generateFollowUpsMutation.mutate(currentMessage.outreach_id)}
                  variant="secondary"
                  size="sm"
                  leftIcon={<SparklesIcon className="h-4 w-4" />}
                  isLoading={generateFollowUpsMutation.isPending}
                  fullWidth
                >
                  Generate 3-Part Follow-Up Sequence
                </Button>
              </div>
            </div>
          )}
        </>
      )}
    </Card>
  );
};
