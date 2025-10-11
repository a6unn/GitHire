import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { JobDescriptionInput } from './JobDescriptionInput';

describe('JobDescriptionInput', () => {
  it('renders with label', () => {
    const onChange = vi.fn();
    render(<JobDescriptionInput value="" onChange={onChange} />);

    expect(screen.getByLabelText(/job description/i)).toBeInTheDocument();
  });

  it('displays character and word count', async () => {
    const onChange = vi.fn();
    const { container } = render(<JobDescriptionInput value="Hello world test" onChange={onChange} />);

    // Wait for useEffect to run
    await new Promise((resolve) => setTimeout(resolve, 0));

    // Check that count text is present in the document
    const countText = container.textContent;
    expect(countText).toMatch(/17 characters|3 words/);
  });

  it('calls onChange when text is entered', () => {
    const onChange = vi.fn();
    render(<JobDescriptionInput value="" onChange={onChange} />);

    const textarea = screen.getByLabelText(/job description/i);
    fireEvent.change(textarea, { target: { value: 'New job description' } });

    expect(onChange).toHaveBeenCalledWith('New job description');
  });

  it('shows error message when provided', () => {
    const onChange = vi.fn();
    render(
      <JobDescriptionInput
        value=""
        onChange={onChange}
        error="This field is required"
      />
    );

    expect(screen.getByText('This field is required')).toBeInTheDocument();
  });

  it('can be disabled', () => {
    const onChange = vi.fn();
    render(<JobDescriptionInput value="" onChange={onChange} disabled />);

    const textarea = screen.getByLabelText(/job description/i);
    expect(textarea).toBeDisabled();
  });

  it('updates word count correctly', () => {
    const onChange = vi.fn();
    const { rerender } = render(
      <JobDescriptionInput value="" onChange={onChange} />
    );

    expect(screen.getByText(/0 words/i)).toBeInTheDocument();

    rerender(<JobDescriptionInput value="One two three" onChange={onChange} />);

    expect(screen.getByText(/3 words/i)).toBeInTheDocument();
  });
});
