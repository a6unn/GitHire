import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import App from './App';

describe('App', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('renders without crashing', () => {
    render(<App />);
    // Should redirect to login when not authenticated
    expect(screen.getByText(/Sign in to continue to GitHire/i)).toBeInTheDocument();
  });
});
