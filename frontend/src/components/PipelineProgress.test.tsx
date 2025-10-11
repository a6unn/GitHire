import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { PipelineProgress } from './PipelineProgress';

describe('PipelineProgress', () => {
  it('renders all pipeline stages', () => {
    render(
      <PipelineProgress
        currentStage="parsing"
        progressPercentage={25}
        status="running"
      />
    );

    expect(screen.getByText('Parsing Job Description')).toBeInTheDocument();
    expect(screen.getByText('Searching GitHub')).toBeInTheDocument();
    expect(screen.getByText('Ranking Candidates')).toBeInTheDocument();
    expect(screen.getByText('Generating Outreach')).toBeInTheDocument();
  });

  it('shows running status', () => {
    render(
      <PipelineProgress
        currentStage="searching"
        progressPercentage={50}
        status="running"
      />
    );

    expect(screen.getByText('Pipeline Running...')).toBeInTheDocument();
  });

  it('shows completed status', () => {
    render(
      <PipelineProgress
        currentStage={null}
        progressPercentage={100}
        status="completed"
      />
    );

    expect(screen.getByText('Pipeline Completed')).toBeInTheDocument();
  });

  it('shows failed status', () => {
    render(
      <PipelineProgress
        currentStage="ranking"
        progressPercentage={75}
        status="failed"
      />
    );

    expect(screen.getByText('Pipeline Failed')).toBeInTheDocument();
  });

  it('displays progress percentage', () => {
    render(
      <PipelineProgress
        currentStage="parsing"
        progressPercentage={35}
        status="running"
      />
    );

    expect(screen.getByText('35%')).toBeInTheDocument();
  });

  it('shows elapsed time when startedAt is provided', () => {
    const startTime = new Date(Date.now() - 30000).toISOString(); // 30 seconds ago

    render(
      <PipelineProgress
        currentStage="searching"
        progressPercentage={50}
        status="running"
        startedAt={startTime}
      />
    );

    expect(screen.getByText(/Elapsed:/)).toBeInTheDocument();
  });
});
