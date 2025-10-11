import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { CandidateCard } from './CandidateCard';
import type { RankedCandidate, OutreachMessage } from '../types/pipeline';

describe('CandidateCard', () => {
  const mockCandidate: RankedCandidate = {
    github_username: 'testdev',
    total_score: 85.5,
    rank: 1,
    domain_score: 90.0,
    score_breakdown: {
      skill_match: 90.0,
      experience: 85.0,
      activity: 82.0,
    },
    strengths: ['Strong Python skills', 'Active contributor'],
    concerns: ['Limited Django experience'],
  };

  const mockOutreach: OutreachMessage = {
    github_username: 'testdev',
    message: 'Hi! We have an exciting opportunity...',
    personalization_notes: 'Relevant FastAPI experience',
    subject: 'Senior Python Developer Opportunity',
  };

  beforeEach(() => {
    // Mock clipboard API
    Object.assign(navigator, {
      clipboard: {
        writeText: vi.fn().mockResolvedValue(undefined),
      },
    });
  });

  it('renders candidate information', () => {
    render(<CandidateCard candidate={mockCandidate} rank={1} />);

    expect(screen.getByText('testdev')).toBeInTheDocument();
    expect(screen.getByText(/85.5/)).toBeInTheDocument();
    expect(screen.getByText('#1')).toBeInTheDocument();
  });

  it('displays score breakdown', () => {
    render(<CandidateCard candidate={mockCandidate} rank={1} />);

    expect(screen.getByText('Score Breakdown:')).toBeInTheDocument();
    expect(screen.getByText(/skill match:/i)).toBeInTheDocument();
    expect(screen.getByText('90.0')).toBeInTheDocument();
    expect(screen.getByText('85.0')).toBeInTheDocument();
  });

  it('shows strengths', () => {
    render(<CandidateCard candidate={mockCandidate} rank={1} />);

    expect(screen.getByText('Strong Python skills')).toBeInTheDocument();
    expect(screen.getByText('Active contributor')).toBeInTheDocument();
  });

  it('shows concerns', () => {
    render(<CandidateCard candidate={mockCandidate} rank={1} />);

    expect(screen.getByText('Limited Django experience')).toBeInTheDocument();
  });

  it('displays outreach message when provided', () => {
    render(
      <CandidateCard
        candidate={mockCandidate}
        outreachMessage={mockOutreach}
        rank={1}
      />
    );

    expect(
      screen.getByText('Senior Python Developer Opportunity')
    ).toBeInTheDocument();
    expect(
      screen.getByText(/Hi! We have an exciting opportunity/)
    ).toBeInTheDocument();
  });

  it('copies outreach message to clipboard', async () => {
    render(
      <CandidateCard
        candidate={mockCandidate}
        outreachMessage={mockOutreach}
        rank={1}
      />
    );

    const copyButton = screen.getByRole('button', { name: /copy/i });
    fireEvent.click(copyButton);

    expect(navigator.clipboard.writeText).toHaveBeenCalledWith(
      mockOutreach.message
    );

    // Should show "Copied!" text
    expect(await screen.findByText('Copied!')).toBeInTheDocument();
  });

  it('renders GitHub profile link', () => {
    render(<CandidateCard candidate={mockCandidate} rank={1} />);

    const link = screen.getByRole('link', { name: /view github profile/i });
    expect(link).toHaveAttribute('href', 'https://github.com/testdev');
  });
});
