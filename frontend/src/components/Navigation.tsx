import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Bars3Icon, XMarkIcon, ArrowRightOnRectangleIcon, UserCircleIcon } from '@heroicons/react/24/outline';
import { useAuth } from '../contexts/AuthContext';
import { Logo } from './ui/Logo';
import { Avatar } from './ui/Avatar';
import { Dropdown } from './ui/Dropdown';
import clsx from 'clsx';

interface NavLinkProps {
  to: string;
  children: React.ReactNode;
  mobile?: boolean;
}

const NavLink: React.FC<NavLinkProps> = ({ to, children, mobile = false }) => {
  const location = useLocation();
  const isActive = location.pathname === to;

  if (mobile) {
    return (
      <Link
        to={to}
        className={clsx(
          'block px-4 py-3 text-base font-medium rounded-lg transition-colors',
          isActive
            ? 'bg-primary-50 text-primary-700'
            : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
        )}
      >
        {children}
      </Link>
    );
  }

  return (
    <Link
      to={to}
      className={clsx(
        'inline-flex items-center px-1 pt-1 text-sm font-medium border-b-2 transition-colors relative',
        isActive
          ? 'text-gray-900 border-primary-500'
          : 'text-gray-500 border-transparent hover:text-gray-700 hover:border-gray-300'
      )}
    >
      {children}
      {isActive && (
        <span className="absolute bottom-0 left-0 right-0 h-0.5 gradient-primary" />
      )}
    </Link>
  );
};

export const Navigation: React.FC = () => {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  if (!isAuthenticated) {
    return null;
  }

  const userMenuItems = [
    {
      label: 'Profile',
      onClick: () => navigate('/profile'),
      icon: <UserCircleIcon className="h-5 w-5" />,
    },
    {
      label: 'Sign out',
      onClick: handleLogout,
      icon: <ArrowRightOnRectangleIcon className="h-5 w-5" />,
    },
  ];

  return (
    <>
      <nav className="sticky top-0 z-40 glass border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            {/* Left side - Logo and navigation links */}
            <div className="flex">
              <div className="flex items-center">
                <Logo variant="full" size="md" linkTo="/dashboard" />
              </div>

              <div className="hidden sm:ml-8 sm:flex sm:space-x-8">
                <NavLink to="/dashboard">Dashboard</NavLink>
                <NavLink to="/projects">Projects</NavLink>
              </div>
            </div>

            {/* Right side - User menu */}
            <div className="flex items-center gap-4">
              {/* Desktop user menu */}
              <div className="hidden sm:block">
                <Dropdown
                  trigger={
                    <button className="flex items-center gap-2 rounded-full hover:opacity-80 transition-opacity focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500">
                      <Avatar
                        initials={(user?.name?.[0] || user?.email?.[0])?.toUpperCase() || 'U'}
                        alt={user?.name || user?.email || 'User'}
                        size="md"
                      />
                    </button>
                  }
                  items={userMenuItems}
                  align="right"
                />
              </div>

              {/* Mobile menu button */}
              <button
                onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                className="sm:hidden inline-flex items-center justify-center p-2 rounded-lg text-gray-500 hover:text-gray-700 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-primary-500 transition-colors"
                aria-label="Toggle menu"
              >
                {isMobileMenuOpen ? (
                  <XMarkIcon className="h-6 w-6" />
                ) : (
                  <Bars3Icon className="h-6 w-6" />
                )}
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Mobile menu */}
      {isMobileMenuOpen && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-30 bg-black bg-opacity-50 backdrop-blur-sm sm:hidden"
            onClick={() => setIsMobileMenuOpen(false)}
          />

          {/* Slide-out panel */}
          <div className="fixed inset-y-0 right-0 z-40 w-64 bg-white shadow-xl sm:hidden animate-slide-in">
            <div className="flex flex-col h-full">
              {/* Header */}
              <div className="flex items-center justify-between px-4 py-4 border-b">
                <Logo variant="full" size="sm" linkTo="/dashboard" />
                <button
                  onClick={() => setIsMobileMenuOpen(false)}
                  className="p-2 rounded-lg text-gray-500 hover:text-gray-700 hover:bg-gray-100"
                  aria-label="Close menu"
                >
                  <XMarkIcon className="h-6 w-6" />
                </button>
              </div>

              {/* User info */}
              <div className="px-4 py-4 border-b bg-gray-50">
                <div className="flex items-center gap-3">
                  <Avatar
                    initials={(user?.name?.[0] || user?.email?.[0])?.toUpperCase() || 'U'}
                    alt={user?.name || user?.email || 'User'}
                    size="lg"
                  />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {user?.name || user?.email}
                    </p>
                  </div>
                </div>
              </div>

              {/* Navigation links */}
              <div className="flex-1 px-4 py-4 space-y-1">
                <NavLink to="/dashboard" mobile>
                  Dashboard
                </NavLink>
                <NavLink to="/projects" mobile>
                  Projects
                </NavLink>
              </div>

              {/* Footer actions */}
              <div className="px-4 py-4 border-t space-y-1">
                <button
                  onClick={() => {
                    setIsMobileMenuOpen(false);
                    navigate('/profile');
                  }}
                  className="flex items-center gap-2 w-full px-4 py-3 text-base font-medium text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <UserCircleIcon className="h-5 w-5" />
                  Profile
                </button>
                <button
                  onClick={() => {
                    setIsMobileMenuOpen(false);
                    handleLogout();
                  }}
                  className="flex items-center gap-2 w-full px-4 py-3 text-base font-medium text-red-600 rounded-lg hover:bg-red-50 transition-colors"
                >
                  <ArrowRightOnRectangleIcon className="h-5 w-5" />
                  Sign out
                </button>
              </div>
            </div>
          </div>
        </>
      )}
    </>
  );
};
