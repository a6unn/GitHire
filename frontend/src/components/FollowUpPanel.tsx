import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  ClockIcon,
  ChatBubbleLeftRightIcon,
  SparklesIcon,
  CheckCircleIcon,
  ClipboardDocumentIcon,
  ClipboardDocumentCheckIcon,
} from '@heroicons/react/24/outline';
import { projectsApi } from '../api/projects';
import { Card } from './ui/Card';
import { Badge } from './ui/Badge';
import type { OutreachMessage } from '../types/outreach';

interface FollowUpPanelProps {
  projectId: string;
  githubUsername: string;
  outreachMessages: OutreachMessage[];
  selectedChannel?: 'email' | 'linkedin' | 'twitter';
}

const ANGLE_CONFIG: Record<string, { icon: string; label: string; color: string; description: string }> = {
  reminder: {
    icon: '🔔',
    label: 'Reminder',
    color: 'blue',
    description: 'Brief reminder with different repo mention',
  },
  technical_challenge: {
    icon: '💻',
    label: 'Technical Challenge',
    color: 'purple',
    description: 'Technical problem preview',
  },
  career_growth: {
    icon: '📈',
    label: 'Career Growth',
    color: 'green',
    description: 'Growth opportunity focus',
  },
  soft_close: {
    icon: '🤝',
    label: 'Soft Close',
    color: 'orange',
    description: 'Gentle opt-out option',
  },
};

export const FollowUpPanel: React.FC<FollowUpPanelProps> = ({
  projectId,
  githubUsername,
  outreachMessages,
  selectedChannel = 'email',
}) => {
  const [copiedId, setCopiedId] = useState<string | null>(null);

  // Show follow-ups for the selected channel's message
  const primaryMessage = outreachMessages?.find(m => m.channel === selectedChannel) || outreachMessages?.[0];

  const { data: followUps, isLoading } = useQuery({
    queryKey: ['follow-ups', projectId, githubUsername, primaryMessage?.outreach_id],
    queryFn: () => primaryMessage ? projectsApi.getFollowUps(projectId, githubUsername, primaryMessage.outreach_id) : Promise.resolve([]),
    enabled: !!primaryMessage,
  });

  const handleCopy = async (text: string, id: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedId(id);
      setTimeout(() => setCopiedId(null), 2000);
    } catch (err) {
      console.error('Failed to copy text:', err);
    }
  };

  if (!primaryMessage) {
    return (
      <Card variant="bordered" padding="lg" className="bg-gray-50">
        <div className="flex items-start gap-3">
          <div className="flex-shrink-0">
            <ChatBubbleLeftRightIcon className="h-6 w-6 text-gray-400" />
          </div>
          <div>
            <h4 className="font-semibold text-gray-700 mb-1">No Follow-Ups Yet</h4>
            <p className="text-sm text-gray-600">
              Generate an outreach message first, then create a follow-up sequence.
            </p>
          </div>
        </div>
      </Card>
    );
  }

  if (isLoading) {
    return (
      <Card variant="elevated" padding="lg">
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
          <p className="text-sm text-gray-600 mt-2">Loading follow-ups...</p>
        </div>
      </Card>
    );
  }

  if (!followUps || followUps.length === 0) {
    return (
      <Card variant="bordered" padding="lg" className="bg-gray-50">
        <div className="flex items-start gap-3">
          <div className="flex-shrink-0">
            <ChatBubbleLeftRightIcon className="h-6 w-6 text-gray-400" />
          </div>
          <div>
            <h4 className="font-semibold text-gray-700 mb-1">No Follow-Ups Generated</h4>
            <p className="text-sm text-gray-600">
              Click "Generate 3-Part Follow-Up Sequence" in the Outreach panel to create follow-ups.
            </p>
          </div>
        </div>
      </Card>
    );
  }

  return (
    <Card variant="elevated" padding="lg" className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <ChatBubbleLeftRightIcon className="h-6 w-6 text-primary-600" />
          <h3 className="text-xl font-bold text-gray-900">Follow-Up Sequence</h3>
        </div>
        <Badge variant="default">{followUps.length}-Part Sequence</Badge>
      </div>

      <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-4 rounded-lg border border-blue-200">
        <div className="flex items-start gap-3">
          <div className="p-2 bg-white rounded-full shadow-sm">
            <SparklesIcon className="h-5 w-5 text-blue-600" />
          </div>
          <div>
            <p className="text-sm font-medium text-gray-900 mb-1">Research-Backed Timing</p>
            <p className="text-xs text-gray-700">
              Follow-ups scheduled for days 3, 7, and 14 based on optimal response patterns.
              Each message uses a different angle to maintain engagement.
            </p>
          </div>
        </div>
      </div>

      {/* Timeline */}
      <div className="relative space-y-8">
        {/* Timeline Line */}
        <div className="absolute left-6 top-6 bottom-6 w-0.5 bg-gradient-to-b from-blue-200 via-purple-200 to-orange-200"></div>

        {followUps.map((followUp: any, index: number) => {
          const config = ANGLE_CONFIG[followUp.angle] || ANGLE_CONFIG.reminder;
          const isLast = index === followUps.length - 1;
          const isCopied = copiedId === followUp.followup_id;

          return (
            <div key={followUp.followup_id} className="relative pl-16">
              {/* Timeline Dot */}
              <div className={`absolute left-3.5 top-6 w-5 h-5 rounded-full bg-white border-2 border-${config.color}-500 shadow-lg flex items-center justify-center z-10`}>
                <div className={`w-2 h-2 rounded-full bg-${config.color}-500`}></div>
              </div>

              {/* Follow-up Card */}
              <Card variant="bordered" padding="md" className={`hover:shadow-md transition-shadow bg-gradient-to-br from-white to-${config.color}-50`}>
                <div className="space-y-3">
                  {/* Header */}
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex items-center gap-2">
                      <span className="text-2xl">{config.icon}</span>
                      <div>
                        <h4 className="font-semibold text-gray-900">{config.label}</h4>
                        <p className="text-xs text-gray-600">{config.description}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <ClockIcon className="h-4 w-4 text-gray-500" />
                      <span className="text-sm font-medium text-gray-700">
                        Day {followUp.scheduled_days_after}
                      </span>
                    </div>
                  </div>

                  {/* Message Preview */}
                  <div className="relative p-3 bg-white rounded border border-gray-200 group">
                    <p className="text-sm text-gray-800 leading-relaxed pr-8">
                      {followUp.message_text}
                    </p>
                    <button
                      onClick={() => handleCopy(followUp.message_text, followUp.followup_id)}
                      className="absolute top-2 right-2 p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded transition-colors opacity-0 group-hover:opacity-100"
                      title="Copy message"
                    >
                      {isCopied ? (
                        <ClipboardDocumentCheckIcon className="h-4 w-4 text-green-600" />
                      ) : (
                        <ClipboardDocumentIcon className="h-4 w-4" />
                      )}
                    </button>
                  </div>

                  {/* Footer */}
                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <span>Sequence {followUp.sequence_number} of {followUps.length}</span>
                    <div className="flex items-center gap-1">
                      <CheckCircleIcon className="h-4 w-4 text-green-500" />
                      <span className="text-green-600 font-medium">Ready to send</span>
                    </div>
                  </div>
                </div>
              </Card>

              {/* Connection Line Indicator */}
              {!isLast && (
                <div className="absolute left-6 -bottom-4 text-center">
                  <div className="text-xs text-gray-500 bg-white px-2 py-0.5 rounded-full border border-gray-200 shadow-sm">
                    ↓ {followUps[index + 1].scheduled_days_after - followUp.scheduled_days_after} days
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Info Footer */}
      <div className="pt-4 border-t border-gray-200">
        <p className="text-xs text-gray-600 text-center">
          💡 Tip: Follow-ups are automatically timed to maximize response rates while respecting candidate's time.
          Each message uses a different angle to avoid repetition.
        </p>
      </div>
    </Card>
  );
};
