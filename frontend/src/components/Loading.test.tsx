import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Loading } from './Loading';

describe('Loading', () => {
  it('renders with default message', () => {
    render(<Loading />);

    expect(screen.getByText('Loading...')).toBeInTheDocument();
    expect(document.querySelector('.animate-spin')).toBeInTheDocument();
  });

  it('renders with custom message', () => {
    render(<Loading message="Please wait..." />);

    expect(screen.getByText('Please wait...')).toBeInTheDocument();
  });
});
