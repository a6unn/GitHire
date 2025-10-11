import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { Dropdown } from './Dropdown';

describe('Dropdown', () => {
  const mockItems = [
    { label: 'Option 1', onClick: vi.fn() },
    { label: 'Option 2', onClick: vi.fn() },
    { label: 'Option 3', onClick: vi.fn(), disabled: true },
  ];

  it('renders trigger button', () => {
    render(
      <Dropdown trigger={<button>Menu</button>} items={mockItems} />
    );
    expect(screen.getByText('Menu')).toBeInTheDocument();
  });

  it('shows menu items when trigger is clicked', async () => {
    render(
      <Dropdown trigger={<button>Menu</button>} items={mockItems} />
    );
    fireEvent.click(screen.getByText('Menu'));
    expect(screen.getByText('Option 1')).toBeInTheDocument();
    expect(screen.getByText('Option 2')).toBeInTheDocument();
  });

  it('calls onClick when menu item is clicked', async () => {
    render(
      <Dropdown trigger={<button>Menu</button>} items={mockItems} />
    );
    fireEvent.click(screen.getByText('Menu'));
    fireEvent.click(screen.getByText('Option 1'));
    expect(mockItems[0].onClick).toHaveBeenCalledTimes(1);
  });

  it('renders disabled menu item', async () => {
    render(
      <Dropdown trigger={<button>Menu</button>} items={mockItems} />
    );
    fireEvent.click(screen.getByText('Menu'));
    const disabledItem = screen.getByText('Option 3');
    expect(disabledItem.closest('button')).toBeDisabled();
  });

  it('renders menu items with icons', async () => {
    const itemsWithIcons = [
      { label: 'Option 1', onClick: vi.fn(), icon: <span data-testid="icon">🔧</span> },
    ];
    render(
      <Dropdown trigger={<button>Menu</button>} items={itemsWithIcons} />
    );
    fireEvent.click(screen.getByText('Menu'));
    expect(screen.getByTestId('icon')).toBeInTheDocument();
  });

  it('renders divider between items', async () => {
    const itemsWithDivider = [
      { label: 'Option 1', onClick: vi.fn() },
      { label: '', onClick: () => {}, divider: true },
      { label: 'Option 2', onClick: vi.fn() },
    ];
    render(
      <Dropdown trigger={<button>Menu</button>} items={itemsWithDivider} />
    );
    fireEvent.click(screen.getByText('Menu'));
    const dividers = document.querySelectorAll('.border-t');
    expect(dividers.length).toBeGreaterThan(0);
  });
});
