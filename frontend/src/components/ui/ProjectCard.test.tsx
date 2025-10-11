import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect, vi } from 'vitest';
import { ProjectCard } from './ProjectCard';

const renderWithRouter = (component: React.ReactElement) => {
  return render(<BrowserRouter>{component}</BrowserRouter>);
};

describe('ProjectCard', () => {
  const defaultProps = {
    id: 'project-1',
    title: 'Senior React Developer',
    description: 'Looking for experienced React developers',
    status: 'active' as const,
    createdAt: '2024-01-15T10:00:00Z',
  };

  it('renders project information', () => {
    renderWithRouter(<ProjectCard {...defaultProps} />);
    expect(screen.getByText('Senior React Developer')).toBeInTheDocument();
    expect(screen.getByText('Looking for experienced React developers')).toBeInTheDocument();
    expect(screen.getByText('Active')).toBeInTheDocument();
  });

  it('renders without description', () => {
    const { description, ...propsWithoutDesc } = defaultProps;
    renderWithRouter(<ProjectCard {...propsWithoutDesc} />);
    expect(screen.getByText('Senior React Developer')).toBeInTheDocument();
    expect(screen.queryByText('Looking for experienced React developers')).not.toBeInTheDocument();
  });

  it('displays candidates count', () => {
    renderWithRouter(<ProjectCard {...defaultProps} candidatesCount={25} />);
    expect(screen.getByText('25 candidates')).toBeInTheDocument();
  });

  it('displays average score', () => {
    renderWithRouter(<ProjectCard {...defaultProps} avgScore={85} />);
    expect(screen.getByText('Avg: 85%')).toBeInTheDocument();
  });

  it('renders different status badges', () => {
    const { rerender } = renderWithRouter(
      <ProjectCard {...defaultProps} status="active" />
    );
    expect(screen.getByText('Active')).toBeInTheDocument();

    rerender(
      <BrowserRouter>
        <ProjectCard {...defaultProps} status="completed" />
      </BrowserRouter>
    );
    expect(screen.getByText('Completed')).toBeInTheDocument();

    rerender(
      <BrowserRouter>
        <ProjectCard {...defaultProps} status="draft" />
      </BrowserRouter>
    );
    expect(screen.getByText('Draft')).toBeInTheDocument();
  });

  it('calls onClick when provided', () => {
    const onClick = vi.fn();
    renderWithRouter(<ProjectCard {...defaultProps} onClick={onClick} />);

    const button = screen.getByRole('button');
    fireEvent.click(button);

    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it('renders as link when onClick is not provided', () => {
    renderWithRouter(<ProjectCard {...defaultProps} />);

    const link = screen.getByRole('link');
    expect(link).toHaveAttribute('href', '/projects/project-1');
  });

  it('formats date correctly', () => {
    renderWithRouter(<ProjectCard {...defaultProps} />);
    expect(screen.getByText(/Jan/)).toBeInTheDocument();
    expect(screen.getByText(/2024/)).toBeInTheDocument();
  });
});
