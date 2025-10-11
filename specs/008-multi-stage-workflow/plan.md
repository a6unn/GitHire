# Implementation Plan: Multi-Stage Project Workflow

**Branch**: `008-multi-stage-workflow` | **Date**: 2025-10-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/008-multi-stage-workflow/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path ✓
2. Fill Technical Context ✓
   → Project Type: full-stack (backend + frontend refactor)
   → Structure Decision: modify existing backend API + frontend pages
3. Fill Constitution Check section ✓
4. Evaluate Constitution Check section ✓
   → Initial check: PASS (all principles aligned)
5. Execute Phase 0 → research.md ✓
6. Execute Phase 1 → contracts, data-model.md, quickstart.md ✓
7. Re-evaluate Constitution Check ✓
   → Post-Design check: PASS (no violations)
8. Plan Phase 2 → Task generation approach documented ✓
9. STOP - Ready for /tasks command ✓
```

## Summary

**Primary Requirement**: Redesign GitHire workflow from single-step pipeline to multi-stage project-based approach where users create projects, manually progress through sourcing → ranking → shortlisting → enrichment → outreach stages with explicit control at each step.

**Technical Approach**:
- **Backend**: Add database tables for shortlisting + outreach, create new staged API endpoints (POST /projects/{id}/source, POST /projects/{id}/rank, POST /projects/{id}/shortlist), add project status field for workflow state machine
- **Frontend**: Refactor ProjectDetailPage to render UI based on project.status, add CreateProjectModal, remove Dashboard pipeline section, implement shortlisting checkboxes and per-candidate action buttons
- **Data Model**: Extend Project entity with name + status fields, add ShortlistedCandidate and OutreachMessage tables, maintain backward compatibility with existing results_json structure
- **Migration Strategy**: Phased rollout - Phase 1 (database + APIs), Phase 2 (frontend project creation), Phase 3 (staged UI), Phase 4 (shortlisting), Phase 5 (enrichment + outreach)

**Key Clarifications Resolved**:
- Users can re-run sourcing/ranking if not satisfied (confirmation dialog required)
- Enrichment is optional (can skip straight to outreach)
- Shortlist persists in database across sessions
- Process continues if browser closed (status saved in DB)
- Project name/JD not editable in MVP (add in future)

## Technical Context

**Language/Version**:
- Backend: Python 3.11+ (FastAPI, SQLAlchemy, Pydantic)
- Frontend: TypeScript 5.x, React 18, Vite 7

**Primary Dependencies**:
- Backend: Existing modules (jd_parser, github_sourcer, ranking_engine, outreach_generator), asyncpg for database
- Frontend: React Query, React Router, Heroicons, Tailwind CSS 4

**Storage**:
- PostgreSQL database with new tables: `shortlisted_candidates`, `outreach_messages`
- Modify existing `projects` table to add `name` and `status` columns

**Testing**:
- Backend: pytest for new endpoints, integration tests for status transitions
- Frontend: Manual testing for workflow progression, state management validation

**Target Platform**:
- Web application (existing architecture)
- Database migrations required

**Project Type**: full-stack (backend API + frontend refactor)

**Performance Goals**:
- Project creation: <500ms response time
- Status transitions: <200ms (just DB update)
- Sourcing: 10-30 seconds (existing Module 002 performance)
- Ranking: 30-60 seconds (existing Module 003 performance)
- Enrichment: 5-15 seconds per candidate (GitHub API calls)
- Outreach: 3-5 seconds per candidate (LLM generation)

**Constraints**:
- Must maintain backward compatibility with existing projects
- Cannot break existing pipeline endpoint (deprecate but don't remove)
- Database migrations must be idempotent
- Frontend must handle async state transitions gracefully

**Scale/Scope**:
- 9 functional requirements
- 4 key entities
- 10+ new API endpoints
- 5+ new React components
- 2 new database tables
- Estimated 35-45 hours total implementation time

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. AI-First Development
- [x] Existing LLM modules (JD Parser, Ranking, Outreach) unchanged
- [x] AI interactions remain transparent (no changes to prompting logic)
- [ ] N/A: No new AI features in this refactor (workflow only)
- [x] Outreach generation preserved as per-candidate action

### II. Privacy-First Architecture
- [x] No new data scraping (uses existing GitHub Sourcer module)
- [x] No additional personal data collected (same data as before)
- [x] Shortlist data user-scoped (project_id tied to user_id)
- [x] Outreach messages private to project owner

### III. Single Source of Truth
- [x] GitHub API integration unchanged (existing Sourcer module)
- [x] No new external dependencies
- [x] Status field in database is single source of truth for workflow state
- [x] Candidate data stored once in results_json, referenced by shortlist

### IV. Transparency & Explainability
- [x] Workflow stages explicitly named and visible to user
- [x] Status badges show current stage clearly
- [x] User makes explicit decisions at each transition (no auto-progression)
- [x] Ranking scores and explanations still visible
- [x] Outreach personalization notes preserved

### V. Modular Architecture
- [x] Existing modules (001-004) remain independent
- [x] New API endpoints thin wrappers around existing modules
- [x] Frontend components decoupled by stage
- [x] Database tables have clear relationships (FK constraints)
- [x] Status transitions enforced at API level, not frontend

**Constitution Status**: ✅ PASS - All principles aligned, no violations

---

## Phase 0: Research & Discovery

*Goal: Understand existing codebase structure and identify integration points.*

### Research Questions
1. How is project data currently stored in `projects` table?
2. What is the current structure of `results_json` field?
3. How does frontend ProjectDetailPage currently fetch project data?
4. Are there any existing status or workflow state fields?
5. What database migration tool is being used (Alembic)?

### Research Tasks
- [x] Read `src/backend_api/models.py` - Project model structure
- [x] Read `src/backend_api/routers/projects_router.py` - Existing API endpoints
- [x] Read `frontend/src/pages/ProjectDetailPage.tsx` - Current UI structure
- [x] Read `frontend/src/api/projects.ts` - Frontend API client
- [x] Check `src/backend_api/database.py` - Database setup and migration approach

### Research Findings
*Documented in [research.md](./research.md)*

---

## Phase 1: Technical Design

*Goal: Define contracts, data models, and component architecture.*

### Deliverables
1. **contracts/** - API endpoint specifications
   - `POST_projects.md` - Create project contract
   - `POST_projects_id_source.md` - Sourcing endpoint contract
   - `POST_projects_id_rank.md` - Ranking endpoint contract
   - `POST_projects_id_shortlist.md` - Shortlisting endpoint contract
   - `POST_projects_id_candidates_username_enrich.md` - Enrichment contract
   - `POST_projects_id_candidates_username_outreach.md` - Outreach generation contract

2. **data-model.md** - Database schema changes
   - Projects table modifications (add `name`, `status`)
   - ShortlistedCandidate table structure
   - OutreachMessage table structure
   - Migration scripts outline

3. **quickstart.md** - Developer guide
   - How to run database migrations
   - How to test new endpoints
   - How to test frontend workflow progression
   - Sample curl commands for each stage

4. **CLAUDE.md** - AI assistant context
   - Project structure overview
   - Key files and their purposes
   - Workflow state machine diagram
   - Common tasks and commands

---

## Phase 2: Task Breakdown

*Generated by /tasks command - see [tasks.md](./tasks.md)*

### Task Categories
1. **Database & Migrations** (Backend)
   - Modify projects table
   - Create shortlisted_candidates table
   - Create outreach_messages table
   - Write migration scripts

2. **Backend Models & Schemas** (Backend)
   - Update Project model
   - Create ShortlistedCandidate model
   - Create OutreachMessage model
   - Create Pydantic request/response schemas

3. **Backend API Endpoints** (Backend)
   - POST /projects with name field
   - POST /projects/{id}/source
   - POST /projects/{id}/rank
   - POST /projects/{id}/shortlist
   - GET /projects/{id}/shortlist
   - DELETE /projects/{id}/shortlist/{username}
   - POST /projects/{id}/candidates/{username}/enrich
   - POST /projects/{id}/candidates/{username}/outreach
   - PUT /projects/{id}/candidates/{username}/outreach
   - POST /projects/{id}/candidates/{username}/outreach/mark-sent

4. **Frontend Components** (Frontend)
   - CreateProjectModal component
   - Status-based ProjectDetailPage refactor
   - CandidateTable component (sourced view)
   - RankedCandidatesList component (with checkboxes)
   - ShortlistPanel component
   - EnrichmentSection component
   - OutreachMessageCard component

5. **Frontend API Integration** (Frontend)
   - Update projects API client
   - Add candidates API client
   - Add shortlist API client
   - Add outreach API client

6. **UI Cleanup** (Frontend)
   - Remove Dashboard pipeline section
   - Update Dashboard to show "Create Project" CTA
   - Update Projects list with status filters
   - Remove old ResultsList from Dashboard

7. **Testing & Validation**
   - Backend endpoint tests (pytest)
   - Frontend workflow tests (manual)
   - Migration rollback tests
   - Backward compatibility tests

8. **Bug Fixes**
   - Fix RankedCandidate serialization (flatten nested structure)
   - Fix project_id undefined issue
   - Fix candidate cards showing blank data
   - Remove debug logging from DashboardPage

---

## Dependencies & Sequencing

### Critical Path
```
Phase 1: Database + Models → Phase 2: Source/Rank APIs → Phase 3: Frontend Project Creation → Phase 4: Status-based UI → Phase 5: Shortlisting → Phase 6: Enrichment/Outreach
```

### Parallel Work Opportunities
- Backend database migrations can happen independently
- Frontend components can be built while backend APIs are in progress (use mocks)
- Bug fixes (flatten RankedCandidate) can be done anytime
- Documentation can be written alongside development

### Blocking Dependencies
- ❌ Cannot build frontend status UI without backend status field
- ❌ Cannot implement shortlisting without backend shortlist table + APIs
- ❌ Cannot test enrichment without shortlisting complete
- ❌ Cannot test outreach without shortlisting complete

---

## Risk Assessment

### High Risk
- **Database Migration Failure**: Projects table has existing data
  - Mitigation: Test migration on copy of production DB first
  - Mitigation: Make status field nullable initially, backfill with 'completed'

- **Backward Compatibility Breaking**: Old projects may not have 'name' field
  - Mitigation: Make 'name' nullable, default to 'Untitled Project'
  - Mitigation: Keep old pipeline endpoint working (deprecate but don't remove)

### Medium Risk
- **State Machine Bugs**: Users may try to skip stages
  - Mitigation: Enforce status transitions at API level with validation
  - Mitigation: Frontend disables buttons for invalid states

- **Data Inconsistency**: Shortlist referencing deleted candidates
  - Mitigation: Add ON DELETE CASCADE constraints
  - Mitigation: Validate candidate exists before shortlisting

### Low Risk
- **UI Complexity**: Status-based rendering may be hard to maintain
  - Mitigation: Use clear switch/case or component map pattern
  - Mitigation: Document state transitions in CLAUDE.md

---

## Success Metrics

### Phase Completion Criteria
- [x] Phase 0: Research complete, existing code understood
- [ ] Phase 1: All contracts, data models, and guides written
- [ ] Phase 2: All tasks defined in tasks.md
- [ ] Phase 3: Database migrations applied successfully
- [ ] Phase 4: Backend APIs functional and tested
- [ ] Phase 5: Frontend components render correctly
- [ ] Phase 6: End-to-end workflow tested (create → source → rank → shortlist → outreach)

### User Acceptance
- [ ] User can create a named project
- [ ] User can source candidates (separate from ranking)
- [ ] User can rank candidates (separate from sourcing)
- [ ] User can manually shortlist specific candidates
- [ ] User can generate outreach for individual candidates
- [ ] All data persists across browser refresh
- [ ] Old Dashboard pipeline removed
- [ ] No blank candidate cards
- [ ] No undefined URLs

---

## Next Steps

Run `/tasks` command to generate detailed task breakdown with:
- Specific file paths to create/modify
- Code snippets for each change
- Test cases to write
- Time estimates per task
- Task dependencies and ordering
