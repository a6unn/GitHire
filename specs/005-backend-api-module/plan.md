# Implementation Plan: Module 005 - Backend API

**Feature Branch**: `005-backend-api-module`
**Created**: 2025-10-06
**Status**: Planning

## Overview

Module 005 provides a REST API layer that orchestrates all core modules (JD Parser, GitHub Sourcer, Ranking Engine, Outreach Generator), manages user authentication, and persists project data. This is the user-facing backend that ties the entire GitHire system together.

## Architecture Design

### Technology Stack

- **Framework**: FastAPI (Python async web framework)
- **Database**: SQLite for MVP (easy setup, file-based, supports async)
- **Authentication**: JWT tokens (session-based)
- **ORM**: SQLAlchemy 2.0 (async)
- **Validation**: Pydantic (already used throughout project)
- **Testing**: pytest + httpx (async client)

### Core Components

```
src/backend_api/
├── __init__.py              # FastAPI app initialization
├── main.py                  # App entry point
├── models.py                # SQLAlchemy database models
├── schemas.py               # Pydantic request/response schemas
├── auth.py                  # Authentication & JWT handling
├── database.py              # Database connection & session
├── pipeline.py              # Pipeline orchestration logic
└── routers/
    ├── auth_router.py       # /auth/* endpoints
    ├── pipeline_router.py   # /pipeline/* endpoints
    └── projects_router.py   # /projects/* endpoints
```

### Database Schema

**users** table:
- user_id (PK, UUID)
- email (unique, indexed)
- hashed_password
- created_at
- last_login

**projects** table:
- project_id (PK, UUID)
- user_id (FK to users)
- job_description_text
- status (enum: running, completed, failed)
- created_at
- pipeline_start_time
- pipeline_end_time
- candidate_count
- results_json (JSONB storing all module outputs)

**sessions** table:
- session_id (PK, UUID)
- user_id (FK to users)
- token (JWT string)
- created_at
- expires_at

### API Endpoints

**Authentication** (`/auth`)
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get JWT token
- `POST /auth/logout` - Invalidate session token

**Pipeline** (`/pipeline`)
- `POST /pipeline/run` - Submit JD and run full pipeline (synchronous, 2 min)
- `GET /pipeline/status/{execution_id}` - Get pipeline execution status

**Projects** (`/projects`)
- `GET /projects` - List all user projects
- `GET /projects/{project_id}` - Get specific project details
- `DELETE /projects/{project_id}` - Delete project
- `GET /projects/{project_id}/export` - Export project data

## Implementation Phases

### Phase 1: Setup & Database (Foundation)
**Objective**: Set up FastAPI app, database models, and migrations

**Tasks**:
1. Create `src/backend_api/` directory structure
2. Define SQLAlchemy database models (User, Project, Session)
3. Create database connection and session management
4. Set up async database engine (SQLite)
5. Create database initialization script
6. Write contract tests for database models

**Acceptance Criteria**:
- Database tables created successfully
- Models validate correctly
- 5-10 contract tests passing

### Phase 2: Authentication System
**Objective**: Implement user registration, login, and JWT authentication

**Tasks**:
1. Create Pydantic schemas for auth (RegisterRequest, LoginRequest, TokenResponse)
2. Implement password hashing (bcrypt)
3. Implement JWT token generation and validation
4. Create auth router with register/login endpoints
5. Create authentication dependency (for protected routes)
6. Write integration tests for auth flow

**Acceptance Criteria**:
- User can register with email/password
- User can login and receive JWT
- JWT validation works for protected routes
- 15-20 integration tests passing

### Phase 3: Pipeline Orchestration
**Objective**: Coordinate execution of Modules 001-004 in sequence

**Tasks**:
1. Create `PipelineOrchestrator` class
2. Implement sequential module execution:
   - Call Module 001 (parse_jd)
   - Call Module 002 (search_github) with async
   - Call Module 003 (rank_candidates)
   - Call Module 004 (generate_outreach_batch)
3. Implement progress tracking logic
4. Handle module failures gracefully
5. Create Pydantic schemas for pipeline responses
6. Write integration tests with mocked modules

**Acceptance Criteria**:
- Pipeline executes all 4 modules in sequence
- Errors in any module are caught and reported
- Progress tracking works
- 20-25 integration tests passing

### Phase 4: Pipeline Router
**Objective**: Expose pipeline endpoints

**Tasks**:
1. Create `/pipeline/run` endpoint (POST)
   - Accept job description
   - Create Project record
   - Execute pipeline orchestrator
   - Update Project with results
   - Return full results
2. Create `/pipeline/status/{execution_id}` endpoint (GET)
   - Return current module being executed
   - Return progress percentage
3. Add authentication middleware to pipeline routes
4. Write API tests for pipeline endpoints

**Acceptance Criteria**:
- `/pipeline/run` successfully executes full pipeline
- Status endpoint returns accurate progress
- Only authenticated users can access
- 15-20 API tests passing

### Phase 5: Projects Router
**Objective**: Expose project management endpoints

**Tasks**:
1. Create `/projects` endpoint (GET) - list all user projects
2. Create `/projects/{project_id}` endpoint (GET) - get project details
3. Create `/projects/{project_id}` endpoint (DELETE) - delete project
4. Create `/projects/{project_id}/export` endpoint (GET) - export JSON
5. Add authorization checks (user can only access their projects)
6. Write API tests for project endpoints

**Acceptance Criteria**:
- Users can list their projects
- Users can retrieve project details
- Users can delete their projects
- Users cannot access other users' projects
- 15-20 API tests passing

### Phase 6: Error Handling & Logging
**Objective**: Implement comprehensive error handling and logging

**Tasks**:
1. Create custom exception classes
2. Implement global exception handler
3. Add structured logging (request ID, user ID, timestamps)
4. Add request/response logging middleware
5. Implement validation error handling
6. Write tests for error scenarios

**Acceptance Criteria**:
- All errors return structured JSON responses
- Logs include context (user, request ID)
- Validation errors are user-friendly
- 10-15 error handling tests passing

### Phase 7: Integration Testing & Documentation
**Objective**: End-to-end testing and API documentation

**Tasks**:
1. Write end-to-end API tests (register → login → run pipeline → list projects)
2. Test concurrent pipeline executions
3. Test pipeline with real module calls (integration mode)
4. Generate OpenAPI/Swagger documentation
5. Update README with API usage examples
6. Create Postman collection or curl examples

**Acceptance Criteria**:
- Full user journey works end-to-end
- API documentation auto-generated
- README includes API examples
- All ~80-100 tests passing

## Testing Strategy

### Test Categories

1. **Contract Tests** (Phase 1): 5-10 tests
   - Database model validation
   - Schema validation

2. **Integration Tests** (Phases 2-6): 70-90 tests
   - Auth flow (register, login, protected routes)
   - Pipeline orchestration with mocked modules
   - API endpoints with test database
   - Error handling scenarios

3. **End-to-End Tests** (Phase 7): 5-10 tests
   - Full user journeys with real modules
   - Concurrent executions

4. **Mock Strategy**:
   - Mock Module 001-004 for fast pipeline tests
   - Use in-memory SQLite for tests
   - Mock external dependencies (GitHub API via Module 002 mocks)

### Performance Targets

- Single pipeline execution: < 2 minutes (per requirements)
- API response time: < 200ms (excluding pipeline execution)
- Support 100 concurrent users (per requirements)
- Database queries optimized (indexes on user_id, project_id)

## Key Design Decisions

### 1. Synchronous Pipeline Execution
**Decision**: `/pipeline/run` is synchronous (blocks for 2 minutes)
**Rationale**: Simpler for MVP; user waits for results rather than polling

### 2. SQLite for MVP
**Decision**: Use SQLite instead of PostgreSQL
**Rationale**: Faster setup, file-based, no external dependencies, sufficient for 100 users

### 3. Store Results as JSON
**Decision**: Store module outputs in `results_json` JSONB column
**Rationale**: Flexible schema, no need for separate tables for candidates/messages

### 4. JWT Session Tokens
**Decision**: Use JWT instead of database sessions
**Rationale**: Stateless, easier to scale, standard approach

### 5. No Rate Limiting for MVP
**Decision**: No rate limiting on API endpoints
**Rationale**: Per spec clarification, trust users for MVP

### 6. FastAPI Framework
**Decision**: Use FastAPI instead of Flask/Django
**Rationale**: Async support, auto docs, Pydantic integration, modern Python

## Dependencies

### Internal
- Module 001 (JD Parser): parse_jd
- Module 002 (GitHub Sourcer): search_github (async)
- Module 003 (Ranking Engine): rank_candidates
- Module 004 (Outreach Generator): generate_outreach_batch

### External
- FastAPI (web framework)
- SQLAlchemy 2.0 (async ORM)
- pydantic (schemas)
- python-jose (JWT)
- passlib (password hashing)
- httpx (test client)

## Success Metrics

- ✅ 80-100 tests passing for Module 005
- ✅ Full pipeline execution < 2 minutes
- ✅ All API endpoints working with auth
- ✅ Users can register, login, run pipelines, view projects
- ✅ Error handling comprehensive and user-friendly
- ✅ API documentation auto-generated
- ✅ Total project tests: ~280-300

## Risks & Mitigations

### Risk 1: Pipeline Timeout (> 2 minutes)
**Mitigation**: Optimize module calls; use caching in Module 002; monitor execution times

### Risk 2: Database Concurrency Issues
**Mitigation**: Use async SQLAlchemy; proper transaction handling; database locks

### Risk 3: JWT Security
**Mitigation**: Use strong secret key; short expiration (24h); HTTPS only in production

### Risk 4: Large Result Sets
**Mitigation**: Paginate project lists; limit candidates returned per pipeline

## Next Steps

1. ✅ Plan created → **Ready for /tasks**
2. Generate detailed task list (tasks.md)
3. Implement Phase 1 (Setup & Database)
4. Proceed through phases 2-7 with TDD approach
