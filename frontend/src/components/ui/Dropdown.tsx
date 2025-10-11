import React from 'react';
import { Menu, Transition } from '@headlessui/react';
import clsx from 'clsx';

export interface DropdownItem {
  label: string;
  onClick: () => void;
  icon?: React.ReactNode;
  disabled?: boolean;
  divider?: boolean;
}

export interface DropdownProps {
  trigger: React.ReactNode;
  items: DropdownItem[];
  align?: 'left' | 'right';
  className?: string;
}

export const Dropdown: React.FC<DropdownProps> = ({
  trigger,
  items,
  align = 'right',
  className = '',
}) => {
  return (
    <Menu as="div" className={clsx('relative inline-block text-left', className)}>
      <Menu.Button as={React.Fragment}>{trigger}</Menu.Button>

      <Transition
        as={React.Fragment}
        enter="transition ease-out duration-100"
        enterFrom="transform opacity-0 scale-95"
        enterTo="transform opacity-100 scale-100"
        leave="transition ease-in duration-75"
        leaveFrom="transform opacity-100 scale-100"
        leaveTo="transform opacity-0 scale-95"
      >
        <Menu.Items
          className={clsx(
            'absolute mt-2 w-56 origin-top-right rounded-lg bg-white shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none z-50',
            align === 'left' ? 'left-0' : 'right-0'
          )}
        >
          <div className="py-1">
            {items.map((item, index) => (
              <React.Fragment key={index}>
                {item.divider ? (
                  <div className="my-1 border-t border-gray-200" />
                ) : (
                  <Menu.Item disabled={item.disabled}>
                    {({ active }) => (
                      <button
                        onClick={item.onClick}
                        className={clsx(
                          'group flex w-full items-center gap-2 px-4 py-2 text-sm transition-colors',
                          active && !item.disabled
                            ? 'bg-primary-50 text-primary-700'
                            : 'text-gray-700',
                          item.disabled && 'opacity-50 cursor-not-allowed'
                        )}
                        disabled={item.disabled}
                      >
                        {item.icon && (
                          <span className="flex-shrink-0 w-5 h-5">{item.icon}</span>
                        )}
                        {item.label}
                      </button>
                    )}
                  </Menu.Item>
                )}
              </React.Fragment>
            ))}
          </div>
        </Menu.Items>
      </Transition>
    </Menu>
  );
};

export default Dropdown;
