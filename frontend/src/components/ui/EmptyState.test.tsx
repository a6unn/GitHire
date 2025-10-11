import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { EmptyState } from './EmptyState';
import { FolderIcon } from '@heroicons/react/24/outline';

describe('EmptyState', () => {
  it('renders title', () => {
    render(<EmptyState title="No projects found" />);
    expect(screen.getByText('No projects found')).toBeInTheDocument();
  });

  it('renders description', () => {
    render(
      <EmptyState
        title="No projects found"
        description="Create your first project to get started"
      />
    );
    expect(screen.getByText('Create your first project to get started')).toBeInTheDocument();
  });

  it('renders icon', () => {
    render(
      <EmptyState
        title="No projects found"
        icon={<FolderIcon className="h-12 w-12" data-testid="folder-icon" />}
      />
    );
    expect(screen.getByTestId('folder-icon')).toBeInTheDocument();
  });

  it('renders action button and calls onClick', () => {
    const onClick = vi.fn();
    render(
      <EmptyState
        title="No projects found"
        action={{ label: 'Create Project', onClick }}
      />
    );

    const button = screen.getByRole('button', { name: 'Create Project' });
    expect(button).toBeInTheDocument();

    fireEvent.click(button);
    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it('renders without optional props', () => {
    render(<EmptyState title="No projects found" />);
    expect(screen.getByText('No projects found')).toBeInTheDocument();
    expect(screen.queryByRole('button')).not.toBeInTheDocument();
  });
});
