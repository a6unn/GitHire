import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ConfirmationModal } from './ConfirmationModal';

describe('ConfirmationModal', () => {
  const defaultProps = {
    isOpen: true,
    title: 'Test Title',
    message: 'Test message',
    onConfirm: vi.fn(),
    onCancel: vi.fn(),
  };

  it('renders when open', () => {
    render(<ConfirmationModal {...defaultProps} />);

    expect(screen.getByText('Test Title')).toBeInTheDocument();
    expect(screen.getByText('Test message')).toBeInTheDocument();
  });

  it('does not render when closed', () => {
    render(<ConfirmationModal {...defaultProps} isOpen={false} />);

    expect(screen.queryByText('Test Title')).not.toBeInTheDocument();
  });

  it('calls onConfirm when confirm button is clicked', () => {
    const onConfirm = vi.fn();
    render(<ConfirmationModal {...defaultProps} onConfirm={onConfirm} />);

    const confirmButton = screen.getByRole('button', { name: /confirm/i });
    fireEvent.click(confirmButton);

    expect(onConfirm).toHaveBeenCalledTimes(1);
  });

  it('calls onCancel when cancel button is clicked', () => {
    const onCancel = vi.fn();
    render(<ConfirmationModal {...defaultProps} onCancel={onCancel} />);

    const cancelButton = screen.getByRole('button', { name: /cancel/i });
    fireEvent.click(cancelButton);

    expect(onCancel).toHaveBeenCalledTimes(1);
  });

  it('renders custom button labels', () => {
    render(
      <ConfirmationModal
        {...defaultProps}
        confirmLabel="Delete Forever"
        cancelLabel="Go Back"
      />
    );

    expect(screen.getByRole('button', { name: 'Delete Forever' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Go Back' })).toBeInTheDocument();
  });

  it('applies danger variant styles', () => {
    render(<ConfirmationModal {...defaultProps} variant="danger" />);

    const confirmButton = screen.getByRole('button', { name: /confirm/i });
    expect(confirmButton.className).toContain('bg-red-600');
  });

  it('applies warning variant styles', () => {
    render(<ConfirmationModal {...defaultProps} variant="warning" />);

    const confirmButton = screen.getByRole('button', { name: /confirm/i });
    expect(confirmButton.className).toContain('bg-yellow-600');
  });

  it('applies info variant styles', () => {
    render(<ConfirmationModal {...defaultProps} variant="info" />);

    const confirmButton = screen.getByRole('button', { name: /confirm/i });
    expect(confirmButton.className).toContain('bg-blue-600');
  });
});
