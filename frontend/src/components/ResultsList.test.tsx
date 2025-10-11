import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ResultsList } from './ResultsList';
import type { RankedCandidate, OutreachMessage } from '../types/pipeline';

describe('ResultsList', () => {
  const mockCandidates: RankedCandidate[] = [
    {
      github_username: 'dev1',
      total_score: 90.0,
      rank: 1,
      domain_score: 95.0,
      score_breakdown: {},
      strengths: [],
      concerns: [],
    },
    {
      github_username: 'dev2',
      total_score: 85.0,
      rank: 2,
      domain_score: 88.0,
      score_breakdown: {},
      strengths: [],
      concerns: [],
    },
  ];

  const mockMessages: OutreachMessage[] = [
    {
      github_username: 'dev1',
      message: 'Message for dev1',
      personalization_notes: 'Notes',
      subject: 'Subject 1',
    },
  ];

  it('renders candidate list with correct count', () => {
    render(
      <ResultsList candidates={mockCandidates} outreachMessages={mockMessages} />
    );

    expect(screen.getByText(/Top Candidates \(2\)/i)).toBeInTheDocument();
  });

  it('renders all candidates', () => {
    render(
      <ResultsList candidates={mockCandidates} outreachMessages={mockMessages} />
    );

    expect(screen.getByText('dev1')).toBeInTheDocument();
    expect(screen.getByText('dev2')).toBeInTheDocument();
  });

  it('shows empty state when no candidates', () => {
    render(<ResultsList candidates={[]} outreachMessages={[]} />);

    expect(screen.getByText('No Candidates Found')).toBeInTheDocument();
    expect(
      screen.getByText(/didn't find any candidates/i)
    ).toBeInTheDocument();
  });

  it('sorts candidates by rank', () => {
    const unsortedCandidates: RankedCandidate[] = [
      { ...mockCandidates[1], rank: 2 },
      { ...mockCandidates[0], rank: 1 },
    ];

    render(
      <ResultsList
        candidates={unsortedCandidates}
        outreachMessages={mockMessages}
      />
    );

    const ranks = screen.getAllByText(/^#\d+$/);
    expect(ranks[0]).toHaveTextContent('#1');
    expect(ranks[1]).toHaveTextContent('#2');
  });
});
