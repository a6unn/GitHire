# Feature Specification: GitHire System Architecture

**Feature Branch**: `000-githire-system-architecture`
**Created**: 2025-10-05
**Status**: Draft - Master Blueprint
**Input**: User description: "GitHire System Architecture: Full-stack AI-powered recruitment platform with Next.js frontend, FastAPI backend orchestrating 4 AI modules (JD Parser, GitHub Sourcer, Ranking Engine, Outreach Generator), PostgreSQL database for user authentication and project persistence, NextAuth for auth, following modular architecture principles"

## Execution Flow (main)
```
1. Parse user description from Input ✓
2. Extract key concepts ✓
   → Actors: Recruiters (primary users)
   → Actions: Parse JD, Search candidates, Rank, Generate outreach
   → Data: Users, Projects, Candidates, Job Requirements
   → Constraints: Modular architecture, AI-first, Privacy-first
3. Mark unclear aspects ✓
   → See [NEEDS CLARIFICATION] markers below
4. Fill User Scenarios & Testing ✓
5. Generate Functional Requirements ✓
6. Identify Key Entities ✓
7. Run Review Checklist
   → WARN: 4 clarifications needed
8. Return: SUCCESS (spec ready for planning)
```

---

## ⚡ Quick Guidelines
- ✅ Focus on WHAT users need and WHY
- ❌ Avoid HOW to implement (no tech stack, APIs, code structure)
- 👥 Written for business stakeholders, not developers

---

## Clarifications

### Session 2025-10-05
- Q: Data retention period - 30 days? 90 days? User-controlled? → A: 1 year (long-term access, higher storage)
- Q: Full pipeline completion time - 30s? 1min? 2min? 5min? → A: 2 minutes (allows for thorough processing)
- Q: Per-module performance targets - strict limits or flexible? → A: No strict per-module limits, just 2min total (flexible allocation)
- Q: Concurrent user capacity - 10? 100? 1000? 10,000+? → A: 100 users (medium company, standard setup)

---

## User Scenarios & Testing *(mandatory)*

### Primary User Story

A recruiter needs to find software developers for an open position. They want to:
1. **Input** a job description in free text (no structured forms)
2. **Automatically extract** the key requirements (skills, experience, location)
3. **Search** GitHub for matching developers
4. **See ranked results** with scores explaining why each candidate is a good fit
5. **Get personalized outreach messages** for each candidate
6. **Save and revisit** their searches later

The system should handle the entire workflow end-to-end without requiring technical knowledge.

### Acceptance Scenarios

1. **Given** a new recruiter visits the platform, **When** they sign up with email/password, **Then** they are authenticated and see an empty dashboard

2. **Given** an authenticated recruiter, **When** they create a new project and paste a JD, **Then** the system extracts requirements and displays them with confidence scores

3. **Given** extracted job requirements, **When** the system searches GitHub, **Then** it returns a list of developer profiles matching the criteria

4. **Given** a list of candidate profiles, **When** the system ranks them, **Then** each candidate has a score (0-100) with breakdown showing skill match, activity level, and domain relevance

5. **Given** ranked candidates, **When** outreach messages are generated, **Then** each message is personalized based on the candidate's GitHub profile and projects

6. **Given** a completed search, **When** the recruiter navigates away and returns, **Then** the project and results are saved and can be resumed

7. **Given** a recruiter with multiple projects, **When** they view the dashboard, **Then** all projects are listed with metadata (name, date, candidate count)

8. **Given** a saved search, **When** the recruiter edits the JD text, **Then** the system re-runs the pipeline and updates results

### Edge Cases

- What happens when a user enters a JD with no technical skills?
  - System should return validation error with guidance

- What happens when GitHub API rate limit is exceeded?
  - System should return partial results with warning and suggested retry time

- What happens when the AI service (for JD parsing or outreach) fails?
  - System should retry and fall back to cached/default behavior if retry fails

- What happens when a user deletes their account?
  - All associated projects and candidate data must be permanently deleted (GDPR right to erasure)

- What happens when concurrent users search for the same role?
  - Each search is independent; results are not shared between users

## Requirements *(mandatory)*

### Functional Requirements

#### Core Features
- **FR-001**: System MUST allow users to register and log in with email/password
- **FR-002**: System MUST associate all searches with authenticated users (no anonymous access)
- **FR-003**: System MUST allow users to create multiple search projects
- **FR-004**: Each project MUST accept free-text job description input (no character limit)
- **FR-005**: System MUST extract structured candidate requirements from JD text using AI
- **FR-006**: System MUST search GitHub for developers matching extracted requirements
- **FR-007**: System MUST rank candidates with scores (0-100) based on fit to job requirements
- **FR-008**: System MUST generate personalized outreach messages for each candidate
- **FR-009**: System MUST save search results and allow users to resume later
- **FR-010**: System MUST list all user's projects on a dashboard

#### Data Requirements
- **FR-011**: System MUST store user accounts (email, password hash)
- **FR-012**: System MUST store project metadata (name, JD text, created date)
- **FR-013**: System MUST store extracted job requirements for each project
- **FR-014**: System MUST store candidate profiles (GitHub username, bio, repos)
- **FR-015**: System MUST store candidate scores and ranking explanations
- **FR-016**: System MUST store generated outreach messages

#### Privacy & Security
- **FR-017**: System MUST only access public GitHub data (no private repos or emails)
- **FR-018**: System MUST isolate user data (users cannot see others' projects)
- **FR-019**: System MUST automatically delete user data (projects, candidates, search results) after 1 year of inactivity
- **FR-020**: System MUST provide data deletion on user request (GDPR right to erasure)

#### Integration & Pipeline
- **FR-021**: System MUST orchestrate AI modules in sequence: JD Parser → GitHub Sourcer → Ranker → Outreach Generator
- **FR-022**: System MUST complete full pipeline (parse → search → rank → outreach) within 2 minutes
- **FR-023**: System MUST cache GitHub API responses to avoid redundant calls
- **FR-024**: System MUST respect GitHub API rate limits (5000 req/hour for authenticated users)

#### User Experience
- **FR-025**: System MUST show confidence scores for extracted job requirements (how certain the AI is)
- **FR-026**: System MUST show ranking breakdown for each candidate (why they scored X points)
- **FR-027**: System MUST allow editing JD text and re-running the pipeline
- **FR-028**: System MUST show loading states during AI processing
- **FR-029**: System MUST display user-friendly error messages when failures occur

### Key Entities

#### User
- Represents a recruiter using the platform
- Attributes: email, password (hashed), registration date
- Relationships: owns multiple Projects

#### Project (Search)
- Represents a single recruitment search
- Attributes: name, job description text, creation date, last updated
- Relationships: belongs to User, has one JobRequirement, has many Candidates

#### JobRequirement
- Represents structured requirements extracted from JD
- Attributes: role/title, required skills list, preferred skills list, years of experience, seniority level, location preferences, domain/industry
- Relationships: belongs to Project

#### Candidate
- Represents a GitHub developer profile
- Attributes: GitHub username, name, bio, location, programming languages, top repositories
- Relationships: belongs to Project, has one CandidateScore, has one OutreachMessage

#### CandidateScore
- Represents ranking score and explanation
- Attributes: total score (0-100), skill match score, activity score, experience score, domain score, score breakdown (explanation)
- Relationships: belongs to Candidate

#### OutreachMessage
- Represents personalized outreach content
- Attributes: message text, personalization factors (which repos/skills mentioned)
- Relationships: belongs to Candidate

---

## Module Boundaries *(architectural)*

The system is composed of **6 independent modules**:

### Module 001: JD Parser ✅ (Already Spec'd)
- **What it does**: Extracts structured candidate requirements from free-text JD
- **Input**: Job description text (string)
- **Output**: JobRequirement (role, skills, experience, etc.)
- **Dependencies**: AI service (for NLP extraction)

### Module 002: GitHub Sourcer
- **What it does**: Searches GitHub for developers matching job requirements
- **Input**: JobRequirement (from Module 001)
- **Output**: List of Candidate profiles
- **Dependencies**: GitHub API

### Module 003: Ranking Engine
- **What it does**: Scores and ranks candidates based on fit to job requirements
- **Input**: JobRequirement + Candidate list (from Module 002)
- **Output**: Ranked Candidate list with scores
- **Dependencies**: None (pure algorithm)

### Module 004: Outreach Generator
- **What it does**: Creates personalized outreach messages for candidates
- **Input**: Candidate profile + JobRequirement + Score
- **Output**: Personalized message text
- **Dependencies**: AI service (for message generation)

### Module 005: Backend API
- **What it does**: Orchestrates all AI modules, manages data persistence, enforces authentication
- **Input**: HTTP requests from frontend
- **Output**: JSON responses
- **Dependencies**: Database, Modules 001-004

### Module 006: Frontend Application
- **What it does**: User interface for recruiters to input JD, view results, manage projects
- **Input**: User interactions
- **Output**: Visual display of data
- **Dependencies**: Module 005 (Backend API)

---

## System Flow

```
1. User logs in (Frontend → Backend → Database)
2. User creates project and pastes JD (Frontend → Backend → Database)
3. Backend triggers pipeline:
   a. JD Parser extracts requirements (Module 001)
   b. GitHub Sourcer finds candidates (Module 002)
   c. Ranking Engine scores candidates (Module 003)
   d. Outreach Generator creates messages (Module 004)
4. Backend saves results to Database
5. Frontend displays results to user
6. User can save, edit, or create new searches
```

---

## Performance Requirements

- **PR-001**: Full pipeline (all modules combined) must complete within 2 minutes
- **PR-002**: Individual modules should be optimized but no strict per-module limits (flexible time allocation)
- **PR-003**: System must support 100 concurrent users (medium company scale)

---

## Review & Acceptance Checklist
*GATE: Automated checks run during main() execution*

### Content Quality
- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

### Requirement Completeness
- [x] No [NEEDS CLARIFICATION] markers remain (all 4 clarifications completed)
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

---

## Execution Status
*Updated by main() during processing*

- [x] User description parsed
- [x] Key concepts extracted (actors, actions, data, constraints)
- [x] Ambiguities marked and resolved (4 clarifications completed)
- [x] User scenarios defined
- [x] Requirements generated (29 functional requirements)
- [x] Entities identified (6 entities)
- [x] Review checklist passed (all requirements clear)

---

## Dependencies

- **Module 001** (JD Parser): Already spec'd, tasks generated
- **Module 002** (GitHub Sourcer): Depends on Module 001 output format
- **Module 003** (Ranking Engine): Depends on Module 002 output format
- **Module 004** (Outreach Generator): Depends on Modules 002 + 003
- **Module 005** (Backend API): Depends on Modules 001-004
- **Module 006** (Frontend): Depends on Module 005

---

## Next Steps

1. **Clarify architecture spec** → Resolve 4 [NEEDS CLARIFICATION] items
2. **Spec each module individually**:
   - Module 001 ✅ Done
   - Module 002: GitHub Sourcer
   - Module 003: Ranking Engine
   - Module 004: Outreach Generator
   - Module 005: Backend API
   - Module 006: Frontend App
3. **Build modules in dependency order**
4. **Integrate and deploy**
