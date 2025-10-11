import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { StatCard } from './StatCard';
import { UserIcon } from '@heroicons/react/24/outline';

describe('StatCard', () => {
  it('renders label and value', () => {
    render(<StatCard label="Total Users" value="1,234" />);
    expect(screen.getByText('Total Users')).toBeInTheDocument();
    expect(screen.getByText('1,234')).toBeInTheDocument();
  });

  it('renders with icon', () => {
    render(
      <StatCard
        label="Total Users"
        value="1,234"
        icon={<UserIcon className="h-6 w-6" data-testid="user-icon" />}
      />
    );
    expect(screen.getByTestId('user-icon')).toBeInTheDocument();
  });

  it('renders positive trend', () => {
    render(
      <StatCard
        label="Total Users"
        value="1,234"
        trend={{ value: 12.5, isPositive: true }}
      />
    );
    expect(screen.getByText(/12.5%/)).toBeInTheDocument();
    expect(screen.getByText(/vs last month/)).toBeInTheDocument();
  });

  it('renders negative trend', () => {
    render(
      <StatCard
        label="Total Users"
        value="1,234"
        trend={{ value: 5.2, isPositive: false }}
      />
    );
    expect(screen.getByText(/5.2%/)).toBeInTheDocument();
  });

  it('applies primary variant styles', () => {
    const { container } = render(
      <StatCard label="Total Users" value="1,234" variant="primary" />
    );
    const card = container.querySelector('.from-primary-50');
    expect(card).toBeInTheDocument();
  });

  it('applies secondary variant styles', () => {
    const { container } = render(
      <StatCard label="Total Users" value="1,234" variant="secondary" />
    );
    const card = container.querySelector('.from-secondary-50');
    expect(card).toBeInTheDocument();
  });

  it('applies custom className', () => {
    const { container } = render(
      <StatCard label="Total Users" value="1,234" className="custom-class" />
    );
    const card = container.querySelector('.custom-class');
    expect(card).toBeInTheDocument();
  });
});
