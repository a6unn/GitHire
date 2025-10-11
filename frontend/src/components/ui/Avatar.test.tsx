import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { Avatar } from './Avatar';

describe('Avatar', () => {
  it('renders with image src', () => {
    render(<Avatar src="https://example.com/avatar.jpg" alt="John Doe" />);
    const img = screen.getByRole('img');
    expect(img).toHaveAttribute('src', 'https://example.com/avatar.jpg');
  });

  it('renders with initials when no src provided', () => {
    render(<Avatar initials="JD" />);
    expect(screen.getByText('JD')).toBeInTheDocument();
  });

  it('renders initials from alt text when no src or initials', () => {
    render(<Avatar alt="John Doe" />);
    expect(screen.getByText('JO')).toBeInTheDocument();
  });

  it('applies different sizes', () => {
    const { rerender, container } = render(<Avatar initials="JD" size="sm" />);
    expect(container.querySelector('.h-8')).toBeInTheDocument();

    rerender(<Avatar initials="JD" size="xl" />);
    expect(container.querySelector('.h-16')).toBeInTheDocument();
  });

  it('renders online status indicator', () => {
    render(<Avatar initials="JD" status="online" />);
    const status = screen.getByLabelText('online');
    expect(status).toHaveClass('bg-green-500');
  });

  it('renders offline status indicator', () => {
    render(<Avatar initials="JD" status="offline" />);
    const status = screen.getByLabelText('offline');
    expect(status).toHaveClass('bg-gray-400');
  });

  it('applies custom className', () => {
    const { container } = render(<Avatar initials="JD" className="custom-class" />);
    expect(container.firstChild).toHaveClass('custom-class');
  });
});
