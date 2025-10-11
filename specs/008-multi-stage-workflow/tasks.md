# Tasks: Multi-Stage Project Workflow

**Input**: Design documents from `/specs/008-multi-stage-workflow/`
**Prerequisites**: plan.md, spec.md

## Execution Flow (main)
```
1. Load plan.md from feature directory ✓
2. Load spec.md for functional requirements ✓
   → 9 functional requirements identified
   → 4 key entities extracted
3. Generate tasks by category ✓
   → Database: 6 tasks
   → Backend Models: 8 tasks
   → Backend APIs: 14 tasks
   → Frontend Components: 12 tasks
   → Frontend API Integration: 4 tasks
   → UI Cleanup: 4 tasks
   → Bug Fixes: 3 tasks
   → Testing: 5 tasks
4. Apply task rules ✓
   → Different files = [P] parallel execution
   → Same file = sequential
   → Database before backend, backend before frontend
5. Number tasks sequentially (T001-T056)
6. Generate dependency graph ✓
7. Create parallel execution examples ✓
8. Validate task completeness ✓
9. Return: SUCCESS (56 tasks ready for execution)
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions
- Estimated time in hours appended

## Path Conventions
- **Backend**: `src/backend_api/` for Python modules
- **Frontend**: `frontend/src/` for TypeScript/React
- **Database**: `src/backend_api/migrations/` for Alembic migrations
- **Tests**: `tests/` for backend, manual testing for frontend in MVP

---

## Phase 1: Database & Migrations (Backend)
**Goal**: Set up new database tables and modify existing schema

- [ ] **T001** [P] Create Alembic migration script to add `name` column (VARCHAR 255, nullable) to `projects` table in `src/backend_api/migrations/versions/add_project_name.py` (0.5h)
- [ ] **T002** [P] Create Alembic migration script to add `status` column (VARCHAR 50, default 'draft') to `projects` table in `src/backend_api/migrations/versions/add_project_status.py` (0.5h)
- [ ] **T003** Create Alembic migration script to create `shortlisted_candidates` table in `src/backend_api/migrations/versions/create_shortlisted_candidates.py` with columns: id (UUID PK), project_id (UUID FK), github_username (VARCHAR), candidate_data (JSONB), enriched_data (JSONB nullable), enrichment_status (VARCHAR nullable), enriched_at (TIMESTAMP nullable), created_at (TIMESTAMP), UNIQUE(project_id, github_username) (1h)
- [ ] **T004** Create Alembic migration script to create `outreach_messages` table in `src/backend_api/migrations/versions/create_outreach_messages.py` with columns: id (UUID PK), project_id (UUID FK), github_username (VARCHAR), subject (VARCHAR 500), message (TEXT), personalization_notes (TEXT), edited_message (TEXT nullable), status (VARCHAR default 'draft'), sent_at (TIMESTAMP nullable), created_at (TIMESTAMP), updated_at (TIMESTAMP), UNIQUE(project_id, github_username) (1h)
- [ ] **T005** Run database migrations and verify tables created correctly with `alembic upgrade head` (0.25h)
- [ ] **T006** [P] Create migration rollback test script to verify `alembic downgrade -1` works for all migrations (0.5h)

---

## Phase 2: Backend Models & Schemas (Backend)
**Goal**: Update SQLAlchemy models and create Pydantic schemas

- [ ] **T007** Update `Project` model in `src/backend_api/models.py` to add `name` (String, nullable=True) and `status` (String, default='draft') fields with status enum validation (0.5h)
- [ ] **T008** [P] Create `ShortlistedCandidate` model in `src/backend_api/models.py` with all fields from T003 migration, add relationship to Project (1h)
- [ ] **T009** [P] Create `OutreachMessage` model in `src/backend_api/models.py` with all fields from T004 migration, add relationships to Project and ShortlistedCandidate (1h)
- [ ] **T010** [P] Create Pydantic schema `ProjectCreate` in `src/backend_api/schemas.py` with fields: name (str), job_title (str), job_description_text (str) - all required (0.5h)
- [ ] **T011** [P] Create Pydantic schema `ProjectResponse` in `src/backend_api/schemas.py` extending existing with name, status, shortlist_count fields (0.5h)
- [ ] **T012** [P] Create Pydantic schema `ShortlistRequest` in `src/backend_api/schemas.py` with field: candidate_usernames (list[str]) (0.25h)
- [ ] **T013** [P] Create Pydantic schema `OutreachResponse` in `src/backend_api/schemas.py` with fields: subject, message, personalization_notes, status, sent_at (0.5h)
- [ ] **T014** [P] Create Pydantic schema `OutreachUpdateRequest` in `src/backend_api/schemas.py` with field: edited_message (str) (0.25h)

---

## Phase 3: Backend API Endpoints (Backend)
**Goal**: Create new staged workflow endpoints

### Project Creation & Management
- [ ] **T015** Update `POST /projects` endpoint in `src/backend_api/routers/projects_router.py` to accept `name` field from ProjectCreate schema, set initial status='draft' (0.5h)
- [ ] **T016** Update `GET /projects/{id}` endpoint in `src/backend_api/routers/projects_router.py` to include name, status, shortlist_count in response (0.5h)
- [ ] **T017** [P] Add query param filtering to `GET /projects` endpoint in `src/backend_api/routers/projects_router.py` to filter by status (e.g., ?status=draft) (0.5h)

### Sourcing Endpoint
- [ ] **T018** Create `POST /projects/{project_id}/source` endpoint in `src/backend_api/routers/projects_router.py` that validates status='draft', runs Module 001 + 002, stores candidates in results_json['candidates'], updates status='sourced', returns {candidates, count} (2h)

### Ranking Endpoint
- [ ] **T019** Create `POST /projects/{project_id}/rank` endpoint in `src/backend_api/routers/projects_router.py` that validates status='sourced', retrieves candidates from results_json, runs Module 003, stores ranked_candidates in results_json, updates status='ranked', returns {ranked_candidates} (2h)

### Shortlisting Endpoints
- [ ] **T020** Create `POST /projects/{project_id}/shortlist` endpoint in `src/backend_api/routers/projects_router.py` that validates status='ranked', accepts ShortlistRequest, creates ShortlistedCandidate records, updates status='shortlisted', returns {shortlisted_count} (1.5h)
- [ ] **T021** Create `GET /projects/{project_id}/shortlist` endpoint in `src/backend_api/routers/projects_router.py` that returns all shortlisted candidates with full RankedCandidate data (1h)
- [ ] **T022** Create `DELETE /projects/{project_id}/shortlist/{username}` endpoint in `src/backend_api/routers/projects_router.py` that removes candidate from shortlist (0.5h)

### Enrichment Endpoint
- [ ] **T023** Create `POST /projects/{project_id}/candidates/{username}/enrich` endpoint in new file `src/backend_api/routers/candidates_router.py` that validates candidate is shortlisted, fetches additional GitHub data, stores in enriched_data field, updates enrichment_status='completed', returns {enriched_data} (2h)

### Outreach Endpoints
- [ ] **T024** Create `POST /projects/{project_id}/candidates/{username}/outreach` endpoint in `src/backend_api/routers/candidates_router.py` that validates candidate is shortlisted, runs Module 004 for single candidate, creates OutreachMessage record, returns {subject, message, personalization_notes} (2h)
- [ ] **T025** Create `PUT /projects/{project_id}/candidates/{username}/outreach` endpoint in `src/backend_api/routers/candidates_router.py` that updates edited_message field in OutreachMessage, returns updated message (0.5h)
- [ ] **T026** Create `POST /projects/{project_id}/candidates/{username}/outreach/mark-sent` endpoint in `src/backend_api/routers/candidates_router.py` that updates status='sent', sets sent_at timestamp, returns {status, sent_at} (0.5h)
- [ ] **T027** Create `GET /projects/{project_id}/outreach` endpoint in `src/backend_api/routers/candidates_router.py` that returns all outreach messages for project (0.5h)

### Router Registration
- [ ] **T028** Register candidates_router in `src/backend_api/main.py` with `app.include_router(candidates_router.router)` (0.25h)

---

## Phase 4: Fix RankedCandidate Serialization (Backend Bug Fix)
**Goal**: Flatten nested candidate object so frontend receives correct structure

- [ ] **T029** Add custom serialization method to `RankedCandidate` model in `src/ranking_engine/models.py` that flattens nested `candidate` object fields (github_username, profile_url, etc.) to top level when calling `.model_dump(mode='json')` (1h)
- [ ] **T030** Update pipeline_router.py and projects_router.py to ensure all ranked_candidates are properly serialized before returning to frontend (0.5h)
- [ ] **T031** [P] Test API response manually with curl/Postman to verify ranked_candidates have github_username at top level, not nested (0.5h)

---

## Phase 5: Frontend - Project Creation (Frontend)
**Goal**: Allow users to create projects with name + JD

- [ ] **T032** Create `CreateProjectModal.tsx` component in `frontend/src/components/modals/` with form fields: name (input), job_title (input), job_description_text (textarea), validation, loading state, error handling (2h)
- [ ] **T033** Update `src/api/projects.ts` to modify `createProject` function to accept name field in request body (0.25h)
- [ ] **T034** Update `DashboardPage.tsx` in `frontend/src/pages/` to remove old "Find Candidates" section, add "Create New Project" button that opens CreateProjectModal, show recent projects list (1h)
- [ ] **T035** [P] Update `ProjectsPage.tsx` in `frontend/src/pages/` to add "Create New Project" button at top that opens CreateProjectModal (0.5h)

---

## Phase 6: Frontend - Project Detail Refactor (Frontend)
**Goal**: Multi-stage workflow UI based on project.status

- [ ] **T036** Create `ProjectStatus` type in `frontend/src/types/project.ts` with enum: 'draft' | 'sourcing' | 'sourced' | 'ranking' | 'ranked' | 'shortlisted' (0.25h)
- [ ] **T037** Refactor `ProjectDetailPage.tsx` to add status-based conditional rendering structure with switch/case or component map pattern (1h)
- [ ] **T038** Implement Draft Status View in `ProjectDetailPage.tsx`: Display project info, show "Find Candidates" button, add loading state during sourcing, call `POST /projects/{id}/source` (1.5h)
- [ ] **T039** Implement Sourced Status View in `ProjectDetailPage.tsx`: Display candidates table with basic info (username, location, bio, repos, languages), show "Rank Candidates" button, call `POST /projects/{id}/rank` (2h)
- [ ] **T040** Create `CandidateTable.tsx` component in `frontend/src/components/` to display sourced candidates in table format with columns: Username, Location, Bio, Repositories, Languages (1.5h)
- [ ] **T041** Implement Ranked Status View in `ProjectDetailPage.tsx`: Display ranked candidates sorted by score, show rank number, total score, score breakdown, matched/missing skills, checkboxes for selection, "Shortlist Selected" button (2.5h)
- [ ] **T042** Update `CandidateCard.tsx` to add checkbox prop and selection state, display score breakdown properly (filter numeric values), show matched_skills and missing_skills if available (1h)

---

## Phase 7: Frontend - Shortlisting (Frontend)
**Goal**: Select and manage shortlisted candidates

- [ ] **T043** Add multi-select state management to ProjectDetailPage.tsx ranked view: track selected candidate usernames in state, update on checkbox change, show count (1h)
- [ ] **T044** Implement "Shortlist Selected" button handler in ProjectDetailPage.tsx: validate at least 1 selected, call `POST /projects/{id}/shortlist`, update project status on success (0.5h)
- [ ] **T045** Implement Shortlisted Status View in ProjectDetailPage.tsx: Create tab view with "All Candidates" and "Shortlisted" tabs, fetch shortlisted candidates with `GET /projects/{id}/shortlist` (1.5h)
- [ ] **T046** Create `ShortlistPanel.tsx` component in `frontend/src/components/` to display shortlisted candidates with action buttons: "Enrich Profile", "Generate Outreach", "Remove from Shortlist" (2h)
- [ ] **T047** Implement remove from shortlist handler: call `DELETE /projects/{id}/shortlist/{username}`, remove from UI on success, show confirmation dialog (1h)

---

## Phase 8: Frontend - Enrichment & Outreach (Frontend)
**Goal**: Per-candidate enrichment and outreach generation UI

- [ ] **T048** Create `EnrichmentSection.tsx` component in `frontend/src/components/` that shows "Enrich Profile" button, loading state, displays enriched data (repos, contributions, skills) after completion, shows timestamp (2h)
- [ ] **T049** Add enrichment API calls to new file `frontend/src/api/candidates.ts`: `enrichCandidate(projectId, username)` calling `POST /projects/{id}/candidates/{username}/enrich` (0.5h)
- [ ] **T050** Create `OutreachMessageCard.tsx` component in `frontend/src/components/` that shows "Generate Outreach" button, displays message in modal/expandable section with subject, body, personalization notes, "Copy" button, "Edit" inline editor, "Save" button, "Regenerate" button, "Mark as Sent" button, status badge (3h)
- [ ] **T051** Add outreach API calls to `frontend/src/api/candidates.ts`: `generateOutreach(projectId, username)`, `updateOutreach(projectId, username, editedMessage)`, `markOutreachSent(projectId, username)`, `getProjectOutreach(projectId)` (1h)
- [ ] **T052** Integrate EnrichmentSection and OutreachMessageCard into ShortlistPanel.tsx, manage state for enrichment/outreach per candidate (1.5h)

---

## Phase 9: Frontend - UI Cleanup (Frontend)
**Goal**: Remove old pipeline workflow

- [ ] **T053** Remove pipeline-related code from DashboardPage.tsx: delete JobDescriptionInput section, remove usePipelineProgress hook usage, remove PipelineProgress component, remove handleRunPipeline function, remove pipeline mutation (1h)
- [ ] **T054** Remove debug logging from DashboardPage.tsx: delete console.log for pipeline completion, remove debug message div (0.25h)
- [ ] **T055** [P] Update Dashboard to show stats overview (total projects, total candidates, avg score) using data from `GET /projects`, add prominent "Create New Project" CTA button (1h)
- [ ] **T056** [P] Update Projects list page UI to show project status badges (Draft/Sourced/Ranked/Shortlisted) with color coding, add status filter dropdown (1h)

---

## Dependencies

### Phase Order (Must be sequential)
```
Phase 1 (Database) → Phase 2 (Models) → Phase 3 (APIs) → Phase 4 (Bug Fix) → Phase 5-9 (Frontend)
```

### Parallel Execution Opportunities

**Database (Phase 1)**: T001, T002 can run in parallel. T003, T004 can run in parallel after T001/T002 complete.

**Models (Phase 2)**: T008, T009, T010, T011, T012, T013, T014 can all run in parallel after T007 completes.

**APIs (Phase 3)**: T017 parallel with T015/T016. T023-T027 can run in parallel (different files).

**Frontend Components (Phases 5-8)**: T032 (CreateProjectModal), T040 (CandidateTable), T046 (ShortlistPanel), T048 (EnrichmentSection), T050 (OutreachMessageCard) can be built in parallel as separate components.

**UI Cleanup (Phase 9)**: T053, T054 sequential (same file). T055, T056 parallel (different concerns).

---

## Critical Path (Longest dependency chain)

```
T001-T006 (Database: 3.75h)
  ↓
T007 (Update Project model: 0.5h)
  ↓
T015 (Update POST /projects: 0.5h)
  ↓
T018 (Source endpoint: 2h)
  ↓
T019 (Rank endpoint: 2h)
  ↓
T020 (Shortlist endpoint: 1.5h)
  ↓
T029-T030 (Fix serialization: 1.5h)
  ↓
T032 (CreateProjectModal: 2h)
  ↓
T037-T038 (ProjectDetail refactor + Draft view: 2.5h)
  ↓
T039-T040 (Sourced view + CandidateTable: 3.5h)
  ↓
T041-T042 (Ranked view + CandidateCard: 3.5h)
  ↓
T043-T047 (Shortlisting UI: 5.5h)
  ↓
T048-T052 (Enrichment + Outreach UI: 8h)
```

**Total Critical Path Time**: ~37 hours

---

## Execution Strategy

### Week 1: Backend Foundation (T001-T031)
- **Day 1-2**: Database migrations + models (T001-T014) = 8h
- **Day 3-4**: API endpoints (T015-T028) = 12h
- **Day 5**: Bug fixes + testing (T029-T031) = 2h

### Week 2: Frontend Core (T032-T042)
- **Day 1**: Project creation UI (T032-T035) = 4h
- **Day 2-3**: Project detail refactor (T036-T039) = 5.25h
- **Day 4-5**: Candidate views (T040-T042) = 7h

### Week 3: Advanced Features (T043-T052)
- **Day 1-2**: Shortlisting (T043-T047) = 6.5h
- **Day 3-5**: Enrichment + Outreach (T048-T052) = 8h

### Week 4: Cleanup & Polish (T053-T056)
- **Day 1**: UI cleanup (T053-T056) = 3.25h
- **Day 2-5**: Testing, bug fixes, documentation

---

## Testing Checklist (Manual for MVP)

After completing all tasks, verify:

- [ ] User can create project with name + JD
- [ ] Project appears in list with "Draft" status
- [ ] "Find Candidates" button works (sources ~25 candidates)
- [ ] Status changes to "Sourced", candidates displayed
- [ ] "Rank Candidates" button works (scores all candidates)
- [ ] Status changes to "Ranked", candidates sorted by score
- [ ] Checkboxes work, can select multiple candidates
- [ ] "Shortlist Selected" works (minimum 1 required)
- [ ] Status changes to "Shortlisted", tab view appears
- [ ] "Enrich Profile" works for individual candidate
- [ ] Enriched data displays correctly
- [ ] "Generate Outreach" works for individual candidate
- [ ] Outreach message displays with copy/edit/send buttons
- [ ] "Mark as Sent" updates status
- [ ] Data persists after browser refresh
- [ ] No blank candidate cards (github_username visible)
- [ ] No undefined URLs (profile links work)
- [ ] Old Dashboard pipeline section removed

---

## Success Criteria

- [x] 56 tasks identified and numbered
- [x] Dependencies mapped (critical path identified)
- [x] Parallel execution opportunities noted
- [x] Time estimates included (total: ~60-70 hours with testing)
- [x] File paths specified for every task
- [x] Testing checklist included

**Status**: ✅ Ready for Implementation
