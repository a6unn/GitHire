# Module 006: Frontend App - Implementation Tasks

## Overview
Build a React-based frontend application with Tailwind CSS that provides a complete UI for recruiters to interact with the GitHire recruitment pipeline.

**Tech Stack:**
- React 18 with TypeScript
- Vite for build tooling
- React Router for navigation
- TanStack Query (React Query) for API state management
- Tailwind CSS for styling
- Vitest + React Testing Library for testing
- Axios for HTTP requests

**Test-Driven Development:**
- Write component tests before implementation
- Integration tests for user flows
- E2E tests for critical paths

---

## Phase 1: Project Setup & Configuration (8 tasks)

### Task 1.1: Initialize Vite React TypeScript Project
**Objective:** Set up the frontend project structure
- [ ] Create `frontend/` directory
- [ ] Initialize Vite project with React + TypeScript template
- [ ] Configure `tsconfig.json` with strict mode
- [ ] Set up `vite.config.ts` with proxy to backend API
- [ ] Update `.gitignore` for frontend artifacts
- [ ] Success: `npm run dev` starts development server

### Task 1.2: Install and Configure Dependencies
**Objective:** Install all required packages
- [ ] Install React Router DOM (`react-router-dom`)
- [ ] Install TanStack Query (`@tanstack/react-query`)
- [ ] Install Axios (`axios`)
- [ ] Install Tailwind CSS and configure
- [ ] Install dev dependencies (Vitest, Testing Library, etc.)
- [ ] Create `package.json` scripts for dev, build, test
- [ ] Success: All dependencies installed, no conflicts

### Task 1.3: Configure Tailwind CSS
**Objective:** Set up styling framework
- [ ] Initialize Tailwind CSS (`npx tailwindcss init -p`)
- [ ] Configure `tailwind.config.js` with content paths
- [ ] Create `src/index.css` with Tailwind directives
- [ ] Add custom color palette (primary, secondary, etc.)
- [ ] Test with sample styled component
- [ ] Success: Tailwind classes work in components

### Task 1.4: Set Up API Client
**Objective:** Create type-safe API client for backend
- [ ] Create `src/api/client.ts` with Axios instance
- [ ] Configure base URL and default headers
- [ ] Add request interceptor for auth tokens
- [ ] Add response interceptor for error handling
- [ ] Create `src/api/types.ts` for API response types
- [ ] Success: API client can make authenticated requests

### Task 1.5: Configure React Query
**Objective:** Set up API state management
- [ ] Create `src/lib/queryClient.ts`
- [ ] Configure default query options (staleTime, retry, etc.)
- [ ] Set up QueryClientProvider in App
- [ ] Create React Query DevTools setup
- [ ] Success: Queries can be created and cached

### Task 1.6: Set Up React Router
**Objective:** Configure client-side routing
- [ ] Create `src/routes/index.tsx` with route definitions
- [ ] Define routes: `/`, `/login`, `/register`, `/dashboard`, `/projects`, `/projects/:id`, `/settings`
- [ ] Create protected route wrapper component
- [ ] Set up `BrowserRouter` in main.tsx
- [ ] Success: Navigation between routes works

### Task 1.7: Configure Testing Environment
**Objective:** Set up Vitest and React Testing Library
- [ ] Configure `vitest.config.ts`
- [ ] Install `@testing-library/react`, `@testing-library/jest-dom`
- [ ] Create `src/test/setup.ts` with global test utilities
- [ ] Create `src/test/utils.tsx` with custom render function
- [ ] Add test scripts to package.json
- [ ] Success: `npm test` runs sample test

### Task 1.8: Create Project Structure
**Objective:** Organize code into logical directories
- [ ] Create `src/components/` for reusable components
- [ ] Create `src/pages/` for page components
- [ ] Create `src/hooks/` for custom hooks
- [ ] Create `src/api/` for API endpoints
- [ ] Create `src/types/` for TypeScript types
- [ ] Create `src/utils/` for utility functions
- [ ] Success: Directory structure is clear and organized

**Phase 1 Tests:** 5-10 basic tests (config, API client, router setup)

---

## Phase 2: Authentication & User Management (12 tasks)

### Task 2.1: Create Auth API Endpoints
**Objective:** Define API functions for authentication
- [ ] Create `src/api/auth.ts`
- [ ] Implement `register(email, password)` function
- [ ] Implement `login(email, password)` function
- [ ] Implement `logout()` function
- [ ] Define TypeScript types for auth responses
- [ ] Success: Auth API functions typed and ready

### Task 2.2: Create Auth Context/Store
**Objective:** Manage authentication state globally
- [ ] Create `src/contexts/AuthContext.tsx`
- [ ] Implement `AuthProvider` with user state
- [ ] Create `useAuth()` hook for consuming auth context
- [ ] Add `login`, `logout`, `register` functions to context
- [ ] Store JWT token in localStorage
- [ ] Success: Auth state accessible from any component

### Task 2.3: Build Login Page UI
**Objective:** Create login form interface
- [ ] Create `src/pages/LoginPage.tsx`
- [ ] Build form with email and password inputs
- [ ] Add form validation (email format, required fields)
- [ ] Add loading state during login
- [ ] Display error messages for failed login
- [ ] Add link to registration page
- [ ] Success: Login form renders with all fields

### Task 2.4: Implement Login Functionality
**Objective:** Connect login form to API
- [ ] Create `useMutation` for login API call
- [ ] Handle successful login (store token, update context)
- [ ] Handle login errors (invalid credentials, network errors)
- [ ] Redirect to dashboard on successful login
- [ ] Success: User can log in successfully

### Task 2.5: Build Registration Page UI
**Objective:** Create registration form interface
- [ ] Create `src/pages/RegisterPage.tsx`
- [ ] Build form with email, password, confirm password
- [ ] Add password strength indicator
- [ ] Add password confirmation validation
- [ ] Display registration errors
- [ ] Add link to login page
- [ ] Success: Registration form renders with validation

### Task 2.6: Implement Registration Functionality
**Objective:** Connect registration form to API
- [ ] Create `useMutation` for register API call
- [ ] Handle successful registration (auto-login)
- [ ] Handle registration errors (duplicate email, etc.)
- [ ] Redirect to dashboard after registration
- [ ] Success: User can register and auto-login

### Task 2.7: Create Protected Route Component
**Objective:** Prevent unauthorized access to pages
- [ ] Create `src/components/ProtectedRoute.tsx`
- [ ] Check if user is authenticated
- [ ] Redirect to login if not authenticated
- [ ] Show loading state while checking auth
- [ ] Success: Unauthenticated users redirected to login

### Task 2.8: Implement Logout Functionality
**Objective:** Allow users to log out
- [ ] Add logout button to navigation
- [ ] Clear auth token from localStorage
- [ ] Clear user from auth context
- [ ] Redirect to login page
- [ ] Success: User can log out successfully

### Task 2.9: Create Navigation Component
**Objective:** Build top navigation bar
- [ ] Create `src/components/Navigation.tsx`
- [ ] Add logo and app name
- [ ] Add navigation links (Dashboard, Projects, Settings)
- [ ] Add user profile dropdown with logout
- [ ] Make responsive for mobile
- [ ] Success: Navigation works on all screen sizes

### Task 2.10: Implement Auto-Login on Page Load
**Objective:** Restore session if token exists
- [ ] Check localStorage for token on app mount
- [ ] Validate token with backend
- [ ] Restore user state if token valid
- [ ] Clear token if invalid/expired
- [ ] Success: User stays logged in after refresh

### Task 2.11: Add Form Components
**Objective:** Create reusable form inputs
- [ ] Create `src/components/Input.tsx` (text input)
- [ ] Create `src/components/Button.tsx` (button)
- [ ] Create `src/components/FormError.tsx` (error message)
- [ ] Add proper TypeScript props
- [ ] Success: Forms use consistent styled components

### Task 2.12: Write Authentication Tests
**Objective:** Test auth flows
- [ ] Write tests for login page rendering
- [ ] Write tests for registration page rendering
- [ ] Write tests for successful login flow
- [ ] Write tests for failed login flow
- [ ] Write tests for logout functionality
- [ ] Write tests for protected routes
- [ ] Success: 10-15 authentication tests passing

**Phase 2 Tests:** 10-15 tests (login, register, logout, protected routes)

---

## Phase 3: Dashboard & Pipeline Execution (15 tasks)

### Task 3.1: Create Dashboard Page Layout
**Objective:** Build main dashboard UI
- [ ] Create `src/pages/DashboardPage.tsx`
- [ ] Add page header with title
- [ ] Create two-column layout (input + results)
- [ ] Make responsive (stack on mobile)
- [ ] Success: Dashboard page renders with layout

### Task 3.2: Build Job Description Input Component
**Objective:** Create text area for JD input
- [ ] Create `src/components/JobDescriptionInput.tsx`
- [ ] Add large textarea with placeholder
- [ ] Add character/word count display
- [ ] Add validation for empty input
- [ ] Style with Tailwind (similar to Juicebox)
- [ ] Success: JD input component works

### Task 3.3: Create Pipeline API Endpoints
**Objective:** Define API functions for pipeline
- [ ] Create `src/api/pipeline.ts`
- [ ] Implement `runPipeline(jobDescription)` function
- [ ] Implement `getPipelineStatus(projectId)` function
- [ ] Define TypeScript types for pipeline responses
- [ ] Success: Pipeline API functions ready

### Task 3.4: Build "Find Candidates" Button
**Objective:** Create CTA button to start pipeline
- [ ] Add prominent button below textarea
- [ ] Disable when textarea empty
- [ ] Show loading spinner when clicked
- [ ] Trigger pipeline API call
- [ ] Success: Button triggers pipeline execution

### Task 3.5: Create Pipeline Progress Component
**Objective:** Build real-time progress indicator
- [ ] Create `src/components/PipelineProgress.tsx`
- [ ] Show 4 stages: Parsing → Searching → Ranking → Outreach
- [ ] Display current stage with highlight
- [ ] Show progress percentage per stage
- [ ] Add estimated time remaining
- [ ] Success: Progress UI renders all stages

### Task 3.6: Implement Progress Polling
**Objective:** Auto-update progress from API
- [ ] Create custom hook `usePipelineProgress(projectId)`
- [ ] Use React Query with polling interval (2 seconds)
- [ ] Update progress state automatically
- [ ] Stop polling when pipeline completes
- [ ] Handle polling errors gracefully
- [ ] Success: Progress updates in real-time

### Task 3.7: Build Pipeline Status States
**Objective:** Show different UI states
- [ ] Create "Idle" state (before pipeline starts)
- [ ] Create "Running" state (progress indicator visible)
- [ ] Create "Completed" state (show results)
- [ ] Create "Failed" state (error message)
- [ ] Success: All states render correctly

### Task 3.8: Handle Pipeline Errors
**Objective:** Display meaningful error messages
- [ ] Show error message with failed stage name
- [ ] Add "Try Again" button
- [ ] Log errors for debugging
- [ ] Success: Pipeline errors displayed clearly

### Task 3.9: Create Candidate Card Component
**Objective:** Build card for displaying candidate
- [ ] Create `src/components/CandidateCard.tsx`
- [ ] Display rank badge, username, match score
- [ ] Show GitHub profile link
- [ ] Display top skills as badges
- [ ] Show relevant repositories
- [ ] Success: Candidate card renders all data

### Task 3.10: Build Outreach Message Display
**Objective:** Show personalized message in card
- [ ] Add message text with formatting
- [ ] Add "Copy to Clipboard" button
- [ ] Show personalization details (transparency)
- [ ] Display copy confirmation toast
- [ ] Success: Outreach message copyable

### Task 3.11: Create Results List Component
**Objective:** Display all ranked candidates
- [ ] Create `src/components/ResultsList.tsx`
- [ ] Map candidates to CandidateCard components
- [ ] Sort by rank (highest score first)
- [ ] Add empty state for zero candidates
- [ ] Success: Results list renders candidates

### Task 3.12: Implement Copy to Clipboard
**Objective:** Allow copying outreach messages
- [ ] Create `src/utils/clipboard.ts` utility
- [ ] Implement copy function with fallback
- [ ] Add toast notification on copy
- [ ] Handle copy errors
- [ ] Success: Messages copy to clipboard

### Task 3.13: Add Loading Skeletons
**Objective:** Show loading placeholders
- [ ] Create `src/components/Skeleton.tsx`
- [ ] Add skeleton for candidate cards
- [ ] Add skeleton for progress indicator
- [ ] Success: Loading states look polished

### Task 3.14: Handle Zero Candidates Result
**Objective:** Show helpful message when no candidates
- [ ] Create empty state component
- [ ] Display friendly message
- [ ] Suggest trying different JD
- [ ] Success: Zero candidates handled gracefully

### Task 3.15: Write Dashboard Tests
**Objective:** Test pipeline execution flow
- [ ] Write tests for JD input component
- [ ] Write tests for pipeline button
- [ ] Write tests for progress indicator
- [ ] Write tests for results display
- [ ] Write tests for candidate cards
- [ ] Write tests for clipboard functionality
- [ ] Success: 15-20 dashboard tests passing

**Phase 3 Tests:** 15-20 tests (JD input, pipeline, progress, results)

---

## Phase 4: Project Management (12 tasks)

### Task 4.1: Create Projects API Endpoints
**Objective:** Define API functions for projects
- [ ] Create `src/api/projects.ts`
- [ ] Implement `getProjects()` function
- [ ] Implement `getProject(id)` function
- [ ] Implement `deleteProject(id)` function
- [ ] Implement `exportProject(id)` function
- [ ] Success: Projects API functions ready

### Task 4.2: Build Projects List Page
**Objective:** Create page for viewing all projects
- [ ] Create `src/pages/ProjectsPage.tsx`
- [ ] Add page header with title
- [ ] Build table/grid layout for projects
- [ ] Make responsive (cards on mobile)
- [ ] Success: Projects page renders

### Task 4.3: Create Project List Item Component
**Objective:** Build component for each project
- [ ] Create `src/components/ProjectListItem.tsx`
- [ ] Display creation date, job title summary
- [ ] Show candidate count and status
- [ ] Add click handler to view details
- [ ] Add delete button
- [ ] Success: Project item renders all data

### Task 4.4: Implement Get Projects Query
**Objective:** Fetch and display all projects
- [ ] Create custom hook `useProjects()`
- [ ] Use React Query to fetch projects
- [ ] Handle loading and error states
- [ ] Display projects in list
- [ ] Success: Projects list fetches and displays

### Task 4.5: Build Project Detail Page
**Objective:** Show full results for a project
- [ ] Create `src/pages/ProjectDetailPage.tsx`
- [ ] Fetch project by ID from URL params
- [ ] Display full job description
- [ ] Show complete results (all candidates)
- [ ] Add back button to projects list
- [ ] Success: Project details page works

### Task 4.6: Implement Delete Project
**Objective:** Allow deleting projects
- [ ] Add delete button with confirmation modal
- [ ] Create `useDeleteProject()` mutation hook
- [ ] Invalidate projects query after delete
- [ ] Show success message
- [ ] Success: Projects can be deleted

### Task 4.7: Create Confirmation Modal
**Objective:** Build reusable confirmation dialog
- [ ] Create `src/components/Modal.tsx`
- [ ] Add confirm/cancel buttons
- [ ] Make accessible (focus trap, ESC key)
- [ ] Style with Tailwind
- [ ] Success: Modal component reusable

### Task 4.8: Implement Export Functionality
**Objective:** Allow exporting project results
- [ ] Add "Export" button to project detail
- [ ] Call export API endpoint
- [ ] Download JSON file
- [ ] Show download confirmation
- [ ] Success: Projects can be exported as JSON

### Task 4.9: Add Project Filtering
**Objective:** Filter projects by date/keyword
- [ ] Add search input for job description
- [ ] Add date range filter
- [ ] Filter projects locally
- [ ] Success: Projects can be filtered

### Task 4.10: Create Empty State Component
**Objective:** Show message when no projects
- [ ] Create `src/components/EmptyState.tsx`
- [ ] Display friendly message
- [ ] Add CTA to create first project
- [ ] Success: Empty state looks good

### Task 4.11: Add Pagination (Optional)
**Objective:** Paginate long project lists
- [ ] Add pagination component
- [ ] Implement client-side pagination
- [ ] Success: Projects paginated

### Task 4.12: Write Project Management Tests
**Objective:** Test project features
- [ ] Write tests for projects list page
- [ ] Write tests for project detail page
- [ ] Write tests for delete functionality
- [ ] Write tests for export functionality
- [ ] Write tests for filtering
- [ ] Success: 10-15 project tests passing

**Phase 4 Tests:** 10-15 tests (project list, detail, delete, export)

---

## Phase 5: Error Handling & Polish (10 tasks)

### Task 5.1: Create Error Boundary Component
**Objective:** Catch React errors gracefully
- [ ] Create `src/components/ErrorBoundary.tsx`
- [ ] Show friendly error message
- [ ] Add "Reload Page" button
- [ ] Log errors for debugging
- [ ] Success: App doesn't crash on errors

### Task 5.2: Build Toast Notification Component
**Objective:** Show temporary success/error messages
- [ ] Create `src/components/Toast.tsx`
- [ ] Support success, error, info types
- [ ] Auto-dismiss after 3 seconds
- [ ] Stack multiple toasts
- [ ] Success: Toasts display notifications

### Task 5.3: Create Loading Component
**Objective:** Show global loading indicator
- [ ] Create `src/components/Loading.tsx`
- [ ] Add spinner animation
- [ ] Center on screen
- [ ] Success: Loading indicator polished

### Task 5.4: Implement Network Error Handling
**Objective:** Handle API failures gracefully
- [ ] Intercept network errors in Axios
- [ ] Show user-friendly error messages
- [ ] Add retry button for failed requests
- [ ] Success: Network errors handled well

### Task 5.5: Add Form Validation Helpers
**Objective:** Create reusable validation functions
- [ ] Create `src/utils/validation.ts`
- [ ] Add email validation
- [ ] Add password validation (min 8 chars)
- [ ] Add required field validation
- [ ] Success: Validation utils reusable

### Task 5.6: Implement Responsive Design
**Objective:** Ensure mobile-friendly UI
- [ ] Test on mobile (320px width)
- [ ] Test on tablet (768px width)
- [ ] Test on desktop (1024px+ width)
- [ ] Fix any layout issues
- [ ] Success: App fully responsive

### Task 5.7: Add Accessibility Features
**Objective:** Make app accessible
- [ ] Add ARIA labels to buttons/inputs
- [ ] Ensure keyboard navigation works
- [ ] Add focus indicators
- [ ] Test with screen reader
- [ ] Success: Basic accessibility implemented

### Task 5.8: Create 404 Not Found Page
**Objective:** Handle invalid routes
- [ ] Create `src/pages/NotFoundPage.tsx`
- [ ] Display friendly 404 message
- [ ] Add link back to dashboard
- [ ] Success: 404 page renders

### Task 5.9: Add Settings Page (Basic)
**Objective:** Create user settings page
- [ ] Create `src/pages/SettingsPage.tsx`
- [ ] Display user email
- [ ] Add account deletion button
- [ ] Success: Settings page basic version

### Task 5.10: Polish UI/UX
**Objective:** Final touches
- [ ] Consistent spacing and colors
- [ ] Smooth transitions
- [ ] Improve button hover states
- [ ] Success: UI feels polished

**Phase 5 Tests:** 8-12 tests (error handling, validation, responsive)

---

## Phase 6: Integration & E2E Testing (8 tasks)

### Task 6.1: Write E2E Test: User Registration
**Objective:** Test complete registration flow
- [ ] User fills registration form
- [ ] Submits and sees dashboard
- [ ] Success: E2E registration test passes

### Task 6.2: Write E2E Test: Login Flow
**Objective:** Test complete login flow
- [ ] User enters credentials
- [ ] Logs in and sees dashboard
- [ ] Success: E2E login test passes

### Task 6.3: Write E2E Test: Pipeline Execution
**Objective:** Test complete pipeline flow
- [ ] User enters job description
- [ ] Clicks "Find Candidates"
- [ ] Sees progress, then results
- [ ] Success: E2E pipeline test passes

### Task 6.4: Write E2E Test: View Projects
**Objective:** Test project management flow
- [ ] User views projects list
- [ ] Clicks on project to see details
- [ ] Success: E2E projects test passes

### Task 6.5: Write E2E Test: Delete Project
**Objective:** Test delete flow
- [ ] User deletes a project
- [ ] Confirms deletion
- [ ] Project removed from list
- [ ] Success: E2E delete test passes

### Task 6.6: Write Integration Tests
**Objective:** Test component integration
- [ ] Test API client with mock server
- [ ] Test React Query hooks
- [ ] Test auth context integration
- [ ] Success: 10-15 integration tests passing

### Task 6.7: Test Error Scenarios
**Objective:** Test error handling
- [ ] Test network failure scenarios
- [ ] Test API error responses
- [ ] Test validation errors
- [ ] Success: Error scenarios covered

### Task 6.8: Run Full Test Suite
**Objective:** Verify all tests pass
- [ ] Run all unit tests
- [ ] Run all integration tests
- [ ] Run all E2E tests
- [ ] Fix any failing tests
- [ ] Success: All tests passing

**Phase 6 Tests:** 20-30 tests (E2E flows, integration tests)

---

## Phase 7: Documentation & Deployment Prep (6 tasks)

### Task 7.1: Create Frontend README
**Objective:** Document frontend setup
- [ ] Add installation instructions
- [ ] Document available scripts
- [ ] Add environment variables guide
- [ ] Success: README complete

### Task 7.2: Add Component Documentation
**Objective:** Document main components
- [ ] Add JSDoc comments to components
- [ ] Document props and usage
- [ ] Success: Components documented

### Task 7.3: Create .env.example
**Objective:** Document required env variables
- [ ] Add `VITE_API_BASE_URL`
- [ ] Add any other required variables
- [ ] Success: .env.example created

### Task 7.4: Optimize Build
**Objective:** Prepare for production
- [ ] Configure production build settings
- [ ] Test production build locally
- [ ] Check bundle size
- [ ] Success: Production build works

### Task 7.5: Add Error Logging (Optional)
**Objective:** Log errors for debugging
- [ ] Add console error logging
- [ ] Consider error tracking service
- [ ] Success: Errors logged

### Task 7.6: Final Manual Testing
**Objective:** Test all features manually
- [ ] Test registration/login flows
- [ ] Test pipeline execution
- [ ] Test project management
- [ ] Test on different browsers
- [ ] Test responsive design
- [ ] Success: All features work

**Phase 7 Tests:** 5-10 final tests (build, deployment)

---

## Summary

**Total Tasks:** 98 tasks across 7 phases
**Estimated Tests:** 80-120 tests

**Phases:**
1. **Phase 1:** Project Setup (8 tasks, 5-10 tests)
2. **Phase 2:** Authentication (12 tasks, 10-15 tests)
3. **Phase 3:** Dashboard & Pipeline (15 tasks, 15-20 tests)
4. **Phase 4:** Project Management (12 tasks, 10-15 tests)
5. **Phase 5:** Error Handling (10 tasks, 8-12 tests)
6. **Phase 6:** Integration Testing (8 tasks, 20-30 tests)
7. **Phase 7:** Documentation (6 tasks, 5-10 tests)

**Key Deliverables:**
- Fully functional React frontend with TypeScript
- Complete authentication system
- Real-time pipeline execution with progress
- Project management interface
- Responsive design (mobile, tablet, desktop)
- Comprehensive test coverage
- Production-ready build
