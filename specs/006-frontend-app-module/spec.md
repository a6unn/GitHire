# Feature Specification: Frontend App Module

**Feature Branch**: `006-frontend-app-module`
**Created**: 2025-10-06
**Status**: Clarified
**Input**: User description: "User interface for recruiters to register/login, submit job descriptions, monitor real-time pipeline execution, view ranked candidates with outreach messages, and manage past projects"

## User Scenarios & Testing

### Primary User Story
A recruiter visits GitHire for the first time, creates an account, and lands on a clean dashboard. They paste a job description into a text area (similar to Juicebox's free-text input), click "Find Candidates", and watch a progress indicator showing which stage the pipeline is at (Parsing JD → Searching GitHub → Ranking → Generating Outreach). After 2 minutes, they see a ranked list of candidates with personalized outreach messages, profile links, and match scores. They can save this project, return later to view history, and copy outreach messages for use.

### Acceptance Scenarios
1. **Given** a new user visits the homepage, **When** they click "Sign Up" and enter credentials, **Then** they are registered and redirected to the dashboard
2. **Given** an authenticated user on the dashboard, **When** they paste a job description and click "Find Candidates", **Then** the pipeline initiates and a progress indicator appears
3. **Given** a pipeline is running, **When** the user views the progress screen, **Then** they see current stage (e.g., "Searching GitHub - 45%") with estimated time remaining
4. **Given** a pipeline completes successfully, **When** results load, **Then** the user sees ranked candidates with scores, GitHub profiles, and personalized outreach messages
5. **Given** a user has 5 past projects, **When** they navigate to "Projects" page, **Then** they see a list with date, job title/summary, and candidate count for each project

### Edge Cases
- What happens when the user navigates away mid-pipeline (does progress persist)?
- How does the UI handle zero candidates returned from search?
- What happens when a pipeline fails at any stage?
- How does the UI display candidates when outreach generation partially fails (e.g., 8 of 10 succeed)?
- What happens when session expires while viewing results?

## Requirements

### Functional Requirements

**Authentication & User Management**
- **FR-001**: Application MUST provide registration form with email and password fields
- **FR-002**: Application MUST provide login form with email and password fields
- **FR-003**: Application MUST store authentication tokens and maintain user session
- **FR-004**: Application MUST redirect unauthenticated users to login page
- **FR-005**: Application MUST provide logout functionality
- **FR-006**: Application MUST support basic password reset using security question (no email verification)

**Job Description Input**
- **FR-007**: Application MUST provide a text area for pasting job descriptions (free-text input like Juicebox)
- **FR-008**: Application MUST allow unlimited text length in job description input
- **FR-009**: Application MUST display character/word count for job description input
- **FR-010**: Application MUST provide clear call-to-action button to initiate pipeline (e.g., "Find Candidates")
- **FR-011**: Application MUST validate that job description is not empty before submission

**Pipeline Execution & Progress**
- **FR-012**: Application MUST display real-time progress indicator showing current pipeline stage
- **FR-013**: Application MUST show stage names: "Parsing Job Description" → "Searching GitHub" → "Ranking Candidates" → "Generating Outreach"
- **FR-014**: Application MUST display progress percentage or completion status for each stage
- **FR-015**: Application MUST show estimated time remaining for pipeline completion
- **FR-016**: Application MUST update progress automatically without requiring page refresh
- **FR-017**: Application MUST allow users to navigate away and return to view ongoing pipeline execution
- **FR-018**: Application MUST handle pipeline failures with clear error messages indicating which stage failed

**Results Display**
- **FR-019**: Application MUST display ranked candidates in order of match score (highest first)
- **FR-020**: Application MUST show each candidate's: GitHub username, profile link, match score, top skills, and relevant repositories
- **FR-021**: Application MUST display personalized outreach message for each candidate
- **FR-022**: Application MUST provide copy-to-clipboard functionality for outreach messages
- **FR-023**: Application MUST indicate which candidate attributes were used for personalization (transparency per constitution)
- **FR-024**: Application MUST handle zero-candidate results with helpful message
- **FR-025**: Application MUST flag candidates with partial data or low confidence scores

**Project Management**
- **FR-026**: Application MUST save completed pipelines as projects automatically
- **FR-027**: Application MUST provide "Projects" page listing all past projects
- **FR-028**: Application MUST display project metadata: creation date, job description summary, candidate count, status
- **FR-029**: Application MUST allow users to click on a project to view full results
- **FR-030**: Application MUST provide delete functionality for projects
- **FR-031**: Application MUST support date filtering and keyword search for projects (search job descriptions)

**User Experience & Design**
- **FR-032**: Application MUST be fully responsive (mobile 320px+, tablet, desktop)
- **FR-033**: Application MUST provide clear navigation between Dashboard, Projects, and Settings pages
- **FR-034**: Application MUST display loading states for all async operations
- **FR-035**: Application MUST show meaningful error messages for network failures or API errors
- **FR-036**: Application MUST use light mode only (single theme, faster MVP)

**Data Export & Privacy**
- **FR-037**: Application MUST provide data export functionality per GDPR requirements (Module 005 dependency)
- **FR-038**: Application MUST provide account deletion functionality with clear warnings
- **FR-039**: Application MUST not expose sensitive user data in URLs or browser storage

### Key Entities

- **View/Page**: Represents distinct UI screens
  - Pages: Login, Registration, Dashboard (JD input + pipeline progress), Results (candidate list), Projects (history), Settings (account management)
  - Navigation: Top navigation bar with user profile dropdown

- **PipelineProgressState**: UI representation of pipeline execution
  - Attributes: current_stage (parsing/searching/ranking/outreach), progress_percentage, estimated_time_remaining, status (running/completed/failed)
  - Updates: Real-time via polling or WebSocket

- **CandidateResultCard**: UI component for displaying candidate information
  - Attributes: rank_position, match_score, github_username, profile_url, top_skills, relevant_repos, outreach_message, personalization_details
  - Actions: Copy outreach message, view GitHub profile (external link)

- **ProjectListItem**: UI component for project history
  - Attributes: project_id, created_date, job_title_summary, candidate_count, status
  - Actions: Click to view full results, delete project

---

## Review & Acceptance Checklist

### Content Quality
- [ ] No implementation details (languages, frameworks, APIs)
- [ ] Focused on user value and business needs
- [ ] Written for non-technical stakeholders
- [ ] All mandatory sections completed

### Requirement Completeness
- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

---

## Execution Status

- [x] User description parsed
- [x] Key concepts extracted
- [x] Ambiguities marked and resolved
- [x] User scenarios defined
- [x] Requirements generated
- [x] Entities identified
- [x] Review checklist passed

---

## Dependencies
- **Consumes Module 005**: Backend API (all endpoints for auth, pipeline, projects)
- **References Module 000**: System Architecture (2-minute pipeline, user experience goals)
- **UX Inspiration**: Juicebox interface (free-text JD input pattern)

## Clarifications Resolved

1. **Password Reset**: Basic reset using security question (no email verification)
2. **Project Filtering**: Date filtering and keyword search (search job descriptions)
3. **Mobile Support**: Full responsive design (mobile 320px+, tablet, desktop)
4. **Theme Customization**: Light mode only (single theme, faster MVP)

## Next Steps

1. **Plan implementation** → Design UI components and responsive layouts
2. **Generate tasks** → TDD task list
3. **Build module** → Responsive frontend with API integration
