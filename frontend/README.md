# GitHire Frontend

React-based frontend application for GitHire - AI-Powered GitHub Developer Recruitment Platform.

## Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite 7.1.9** - Build tool and dev server
- **React Router DOM 6.30.1** - Client-side routing
- **TanStack Query 5.90.2** - Server state management
- **Axios 1.12.2** - HTTP client
- **Tailwind CSS 4.1.14** - Styling
- **Vitest 3.2.4** - Testing framework
- **React Testing Library 16.3.0** - Component testing

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Backend API running on `http://localhost:8000` (or configure `VITE_API_BASE_URL`)

### Installation

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Copy environment variables
cp .env.example .env

# Edit .env and configure API URL if needed
# VITE_API_BASE_URL=http://localhost:8000/api
```

### Development

```bash
# Start development server (http://localhost:5173)
npm run dev

# Run tests
npm test

# Run tests in watch mode
npm run test:watch

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

## Environment Variables

Create a `.env` file in the `frontend/` directory:

```env
# API Base URL (default: /api for proxy setup)
VITE_API_BASE_URL=/api
```

**Note:** In development, Vite proxy is configured to forward `/api/*` requests to `http://localhost:8000/api/*`.

## Features

### Authentication
- User registration with password strength validation
- Login with email/password
- Auto-login from localStorage
- Protected routes
- Session persistence

### Dashboard
- Job description input with character/word count
- Pipeline execution with real-time progress
- Results display with ranked candidates
- Outreach message generation

### Project Management
- List all projects with status filtering
- Project details view
- Delete projects with confirmation
- Export project results as JSON

### Error Handling
- Global error boundary
- Toast notifications for success/error feedback
- User-friendly error messages
- Network error handling

### UI/UX
- Responsive design (mobile, tablet, desktop)
- Loading states
- Empty states
- 404 page
- Accessible components (ARIA labels, keyboard navigation)

## Testing

The project includes comprehensive test coverage:

- **98 tests** across unit, integration, and component tests
- Coverage areas: Authentication flows, Pipeline execution, Project management, Error handling, Component rendering, Form validation

Run tests:
```bash
npm test                  # Run all tests
npm run test:watch       # Watch mode
```

## Building for Production

```bash
# Create production build
npm run build

# Output in dist/ directory
# Serve with any static file server
```

## Status

**All phases complete!** 98 tests passing.

See `../specs/006-frontend-app-module/tasks.md` for implementation details.
