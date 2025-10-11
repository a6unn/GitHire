# Implementation Tasks: Module 005 - Backend API

**Status**: Ready for Implementation
**Estimated Total Tasks**: 55
**Approach**: Test-Driven Development (TDD)

---

## Phase 1: Setup & Database (12 tasks)

### Task 1.1: Create Module Structure
- [ ] Create directory `src/backend_api/`
- [ ] Create `src/backend_api/__init__.py`
- [ ] Create `src/backend_api/main.py` (FastAPI app)
- [ ] Create `src/backend_api/routers/` directory
- [ ] Create `tests/backend_api/` directory structure

**Acceptance**: Directory structure matches plan

### Task 1.2: Install Dependencies
- [ ] Add FastAPI to project dependencies
- [ ] Add SQLAlchemy[asyncio] to dependencies
- [ ] Add python-jose[cryptography] (JWT)
- [ ] Add passlib[bcrypt] (password hashing)
- [ ] Add httpx (async test client)
- [ ] Add aiosqlite (async SQLite driver)

**Acceptance**: All dependencies installable via `pip install -e .`

### Task 1.3: Create Database Models
- [ ] Create `src/backend_api/models.py`
- [ ] Define `User` model (id, email, hashed_password, created_at, last_login)
- [ ] Define `Project` model (id, user_id, job_description_text, status, created_at, results_json)
- [ ] Define `Session` model (id, user_id, token, created_at, expires_at)
- [ ] Add indexes (user_id, email)

**Acceptance**: Models defined with proper relationships

### Task 1.4: Create Database Connection
- [ ] Create `src/backend_api/database.py`
- [ ] Define async SQLAlchemy engine (SQLite)
- [ ] Create async session maker
- [ ] Define `get_db()` dependency for FastAPI

**Acceptance**: Database connection module works

### Task 1.5: Create Database Init Script
- [ ] Add `init_db()` function in database.py
- [ ] Create tables on startup
- [ ] Handle database file creation

**Acceptance**: Database initialized successfully

### Task 1.6: Write Contract Tests for User Model
- [ ] Create `tests/backend_api/contract/test_models.py`
- [ ] Test User model creation
- [ ] Test email uniqueness constraint
- [ ] Test password field exists

**Acceptance**: 3-5 tests passing

### Task 1.7: Write Contract Tests for Project Model
- [ ] Test Project model creation
- [ ] Test foreign key relationship to User
- [ ] Test status enum values
- [ ] Test results_json field (JSONB)

**Acceptance**: 4-5 tests passing

### Task 1.8: Write Contract Tests for Session Model
- [ ] Test Session model creation
- [ ] Test foreign key to User
- [ ] Test token expiration logic

**Acceptance**: 3-4 tests passing

### Task 1.9: Test Database Initialization
- [ ] Test init_db() creates tables
- [ ] Test database file creation
- [ ] Test async session creation

**Acceptance**: 2-3 tests passing

### Task 1.10: Run Phase 1 Tests
- [ ] Execute `pytest tests/backend_api/contract/`
- [ ] Verify 12-17 tests passing

**Acceptance**: All contract tests green

### Task 1.11: Create Basic FastAPI App
- [ ] Initialize FastAPI app in main.py
- [ ] Add database startup/shutdown events
- [ ] Add health check endpoint `/health`

**Acceptance**: App starts and health check responds

### Task 1.12: Phase 1 Complete
- [ ] Review code quality
- [ ] Ensure all tests passing
- [ ] Commit Phase 1 work

**Acceptance**: Phase 1 checkpoint reached

---

## Phase 2: Authentication System (13 tasks)

### Task 2.1: Create Pydantic Schemas
- [ ] Create `src/backend_api/schemas.py`
- [ ] Define `RegisterRequest` schema (email, password)
- [ ] Define `LoginRequest` schema (email, password)
- [ ] Define `TokenResponse` schema (access_token, token_type)
- [ ] Define `UserResponse` schema (user_id, email, created_at)

**Acceptance**: Schemas validate correctly

### Task 2.2: Create Auth Utilities
- [ ] Create `src/backend_api/auth.py`
- [ ] Implement `hash_password(password: str) -> str` using bcrypt
- [ ] Implement `verify_password(plain: str, hashed: str) -> bool`
- [ ] Add unit tests for password hashing

**Acceptance**: Password hashing works, 2-3 tests passing

### Task 2.3: Implement JWT Token Generation
- [ ] Add `create_access_token(data: dict) -> str` in auth.py
- [ ] Use python-jose for JWT encoding
- [ ] Set expiration to 24 hours
- [ ] Add secret key configuration

**Acceptance**: JWT tokens generated correctly

### Task 2.4: Implement JWT Token Validation
- [ ] Add `decode_access_token(token: str) -> dict` in auth.py
- [ ] Handle token expiration
- [ ] Handle invalid tokens
- [ ] Add unit tests for JWT validation

**Acceptance**: Token validation works, 3-4 tests passing

### Task 2.5: Create Auth Dependency
- [ ] Add `get_current_user(token: str, db: Session)` dependency
- [ ] Validate JWT token
- [ ] Fetch user from database
- [ ] Raise HTTP 401 if invalid

**Acceptance**: Dependency works for protected routes

### Task 2.6: Create Auth Router
- [ ] Create `src/backend_api/routers/auth_router.py`
- [ ] Add `/auth/register` endpoint (POST)
- [ ] Add `/auth/login` endpoint (POST)
- [ ] Add `/auth/logout` endpoint (POST)

**Acceptance**: Router created with endpoint stubs

### Task 2.7: Implement Register Endpoint
- [ ] Validate email format
- [ ] Check if email already exists
- [ ] Hash password
- [ ] Create User record
- [ ] Return UserResponse

**Acceptance**: Registration works

### Task 2.8: Implement Login Endpoint
- [ ] Fetch user by email
- [ ] Verify password
- [ ] Create Session record
- [ ] Generate JWT token
- [ ] Return TokenResponse

**Acceptance**: Login works and returns JWT

### Task 2.9: Implement Logout Endpoint
- [ ] Validate JWT token
- [ ] Delete Session record
- [ ] Return success message

**Acceptance**: Logout invalidates session

### Task 2.10: Write Integration Tests for Registration
- [ ] Create `tests/backend_api/integration/test_auth.py`
- [ ] Test successful registration
- [ ] Test duplicate email rejection
- [ ] Test invalid email format
- [ ] Test weak password rejection

**Acceptance**: 4-5 tests passing

### Task 2.11: Write Integration Tests for Login
- [ ] Test successful login
- [ ] Test wrong password
- [ ] Test non-existent user
- [ ] Test token structure

**Acceptance**: 4-5 tests passing

### Task 2.12: Write Integration Tests for Protected Routes
- [ ] Test accessing protected route with valid token
- [ ] Test accessing without token (401)
- [ ] Test accessing with expired token (401)
- [ ] Test accessing with invalid token (401)

**Acceptance**: 4-5 tests passing

### Task 2.13: Phase 2 Complete
- [ ] Run `pytest tests/backend_api/integration/test_auth.py`
- [ ] Verify 15-20 tests passing total
- [ ] Commit Phase 2 work

**Acceptance**: Phase 2 checkpoint reached

---

## Phase 3: Pipeline Orchestration (10 tasks)

### Task 3.1: Create PipelineOrchestrator Class
- [ ] Create `src/backend_api/pipeline.py`
- [ ] Define `PipelineOrchestrator` class
- [ ] Add `__init__()` method

**Acceptance**: Class importable

### Task 3.2: Implement Module 001 Integration
- [ ] Add method `_execute_module_001(job_description: str) -> JobRequirement`
- [ ] Call `parse_jd` from Module 001
- [ ] Handle exceptions and log errors
- [ ] Return structured result

**Acceptance**: Module 001 integration works

### Task 3.3: Implement Module 002 Integration (Async)
- [ ] Add async method `_execute_module_002(job_req: JobRequirement) -> dict`
- [ ] Call `search_github` from Module 002 (async)
- [ ] Extract candidates and metadata
- [ ] Handle exceptions

**Acceptance**: Module 002 integration works

### Task 3.4: Implement Module 003 Integration
- [ ] Add method `_execute_module_003(candidates, job_req) -> list[RankedCandidate]`
- [ ] Call `rank_candidates` from Module 003
- [ ] Handle exceptions

**Acceptance**: Module 003 integration works

### Task 3.5: Implement Module 004 Integration
- [ ] Add method `_execute_module_004(ranked, job_req) -> list[OutreachMessage]`
- [ ] Call `generate_outreach_batch` from Module 004
- [ ] Handle exceptions

**Acceptance**: Module 004 integration works

### Task 3.6: Implement Sequential Orchestration
- [ ] Add async method `execute_pipeline(job_description: str) -> dict`
- [ ] Call modules 001 → 002 → 003 → 004 in sequence
- [ ] Pass output of each module to next
- [ ] Track progress
- [ ] Return combined results

**Acceptance**: Full pipeline executes

### Task 3.7: Implement Progress Tracking
- [ ] Add `current_module` state tracking
- [ ] Calculate progress percentage (25% per module)
- [ ] Add estimated time remaining

**Acceptance**: Progress tracking works

### Task 3.8: Implement Error Handling
- [ ] Wrap each module call in try/except
- [ ] Create custom PipelineException
- [ ] Include which module failed in error
- [ ] Clean up partial results on failure

**Acceptance**: Errors handled gracefully

### Task 3.9: Write Integration Tests for Pipeline Orchestration
- [ ] Create `tests/backend_api/integration/test_pipeline_orchestrator.py`
- [ ] Mock all 4 modules
- [ ] Test successful pipeline execution
- [ ] Test failure at Module 001
- [ ] Test failure at Module 002
- [ ] Test failure at Module 003
- [ ] Test failure at Module 004

**Acceptance**: 7-10 tests passing

### Task 3.10: Phase 3 Complete
- [ ] Run pipeline orchestration tests
- [ ] Verify 20-25 tests passing
- [ ] Commit Phase 3 work

**Acceptance**: Phase 3 checkpoint reached

---

## Phase 4: Pipeline Router (8 tasks)

### Task 4.1: Create Pipeline Schemas
- [ ] Add `PipelineRunRequest` schema in schemas.py (job_description_text)
- [ ] Add `PipelineRunResponse` schema (project_id, status, candidates, messages, metadata)
- [ ] Add `PipelineStatusResponse` schema (project_id, current_module, progress, status)

**Acceptance**: Schemas defined

### Task 4.2: Create Pipeline Router
- [ ] Create `src/backend_api/routers/pipeline_router.py`
- [ ] Define router with `/pipeline` prefix
- [ ] Add authentication dependency

**Acceptance**: Router created

### Task 4.3: Implement /pipeline/run Endpoint
- [ ] Add `POST /pipeline/run` endpoint
- [ ] Accept PipelineRunRequest
- [ ] Create Project record (status=running)
- [ ] Execute PipelineOrchestrator
- [ ] Update Project with results
- [ ] Return PipelineRunResponse

**Acceptance**: Endpoint executes pipeline

### Task 4.4: Implement /pipeline/status/{project_id} Endpoint
- [ ] Add `GET /pipeline/status/{project_id}` endpoint
- [ ] Fetch Project by ID
- [ ] Return current module and progress
- [ ] Handle non-existent project

**Acceptance**: Status endpoint works

### Task 4.5: Add Authorization Checks
- [ ] Verify user owns the project before returning results
- [ ] Return 403 if unauthorized
- [ ] Add tests for authorization

**Acceptance**: Authorization works

### Task 4.6: Write API Tests for /pipeline/run
- [ ] Create `tests/backend_api/api/test_pipeline_router.py`
- [ ] Test successful pipeline run with mocked modules
- [ ] Test authentication required (401 without token)
- [ ] Test invalid job description

**Acceptance**: 3-5 tests passing

### Task 4.7: Write API Tests for /pipeline/status
- [ ] Test status for running pipeline
- [ ] Test status for completed pipeline
- [ ] Test status for non-existent project (404)
- [ ] Test unauthorized access (403)

**Acceptance**: 4-5 tests passing

### Task 4.8: Phase 4 Complete
- [ ] Run pipeline router tests
- [ ] Verify 15-20 tests passing
- [ ] Commit Phase 4 work

**Acceptance**: Phase 4 checkpoint reached

---

## Phase 5: Projects Router (8 tasks)

### Task 5.1: Create Project Schemas
- [ ] Add `ProjectListResponse` schema (list of projects with summary)
- [ ] Add `ProjectDetailResponse` schema (full project with all results)

**Acceptance**: Schemas defined

### Task 5.2: Create Projects Router
- [ ] Create `src/backend_api/routers/projects_router.py`
- [ ] Define router with `/projects` prefix
- [ ] Add authentication dependency

**Acceptance**: Router created

### Task 5.3: Implement GET /projects Endpoint
- [ ] Add `GET /projects` endpoint
- [ ] Fetch all projects for authenticated user
- [ ] Return ProjectListResponse
- [ ] Support pagination (optional for MVP)

**Acceptance**: Endpoint lists user projects

### Task 5.4: Implement GET /projects/{project_id} Endpoint
- [ ] Add `GET /projects/{project_id}` endpoint
- [ ] Fetch project by ID
- [ ] Verify user owns project
- [ ] Return ProjectDetailResponse

**Acceptance**: Endpoint returns project details

### Task 5.5: Implement DELETE /projects/{project_id} Endpoint
- [ ] Add `DELETE /projects/{project_id}` endpoint
- [ ] Verify user owns project
- [ ] Delete project from database
- [ ] Return success message

**Acceptance**: Endpoint deletes project

### Task 5.6: Implement GET /projects/{project_id}/export Endpoint
- [ ] Add `GET /projects/{project_id}/export` endpoint
- [ ] Verify user owns project
- [ ] Return results_json as downloadable JSON file
- [ ] Set appropriate headers

**Acceptance**: Endpoint exports project data

### Task 5.7: Write API Tests for Projects Endpoints
- [ ] Create `tests/backend_api/api/test_projects_router.py`
- [ ] Test listing projects
- [ ] Test getting project details
- [ ] Test deleting project
- [ ] Test export
- [ ] Test unauthorized access (403)
- [ ] Test non-existent project (404)

**Acceptance**: 10-15 tests passing

### Task 5.8: Phase 5 Complete
- [ ] Run projects router tests
- [ ] Verify 15-20 tests passing
- [ ] Commit Phase 5 work

**Acceptance**: Phase 5 checkpoint reached

---

## Phase 6: Error Handling & Logging (6 tasks)

### Task 6.1: Create Custom Exceptions
- [ ] Create `src/backend_api/exceptions.py`
- [ ] Define `PipelineException` (module_name, error_message)
- [ ] Define `AuthenticationException`
- [ ] Define `AuthorizationException`

**Acceptance**: Exceptions defined

### Task 6.2: Implement Global Exception Handler
- [ ] Add exception handlers in main.py
- [ ] Handle PipelineException → 500 with details
- [ ] Handle HTTPException → preserve status code
- [ ] Handle generic Exception → 500 generic message

**Acceptance**: All exceptions return JSON

### Task 6.3: Add Logging Middleware
- [ ] Create logging middleware
- [ ] Log request method, path, user_id, timestamp
- [ ] Log response status code, duration
- [ ] Add correlation ID to each request

**Acceptance**: All requests logged

### Task 6.4: Add Validation Error Handling
- [ ] Handle Pydantic ValidationError
- [ ] Return user-friendly field error messages
- [ ] Test with invalid inputs

**Acceptance**: Validation errors are clear

### Task 6.5: Write Tests for Error Handling
- [ ] Create `tests/backend_api/integration/test_error_handling.py`
- [ ] Test pipeline failure returns 500 with module info
- [ ] Test validation error returns 422 with field details
- [ ] Test authentication error returns 401
- [ ] Test authorization error returns 403

**Acceptance**: 5-10 tests passing

### Task 6.6: Phase 6 Complete
- [ ] Run error handling tests
- [ ] Verify 10-15 tests passing
- [ ] Commit Phase 6 work

**Acceptance**: Phase 6 checkpoint reached

---

## Phase 7: Integration Testing & Documentation (8 tasks)

### Task 7.1: Write End-to-End Test (Happy Path)
- [ ] Create `tests/backend_api/e2e/test_full_journey.py`
- [ ] Test: Register → Login → Run Pipeline → List Projects → Get Project → Export
- [ ] Use real modules (not mocked)
- [ ] Verify full data flow

**Acceptance**: 1-2 E2E tests passing

### Task 7.2: Test Concurrent Pipeline Executions
- [ ] Create test for 2 users running pipelines simultaneously
- [ ] Verify no data leakage between users
- [ ] Verify both complete successfully

**Acceptance**: 1-2 concurrency tests passing

### Task 7.3: Test Pipeline with Module 002 Returning Zero Candidates
- [ ] Mock Module 002 to return empty candidate list
- [ ] Verify pipeline handles gracefully
- [ ] Verify appropriate message in results

**Acceptance**: 1 test passing

### Task 7.4: Generate OpenAPI Documentation
- [ ] Verify FastAPI auto-generates /docs endpoint
- [ ] Test Swagger UI loads
- [ ] Add docstrings to endpoints for better docs

**Acceptance**: /docs endpoint works

### Task 7.5: Update README with API Examples
- [ ] Add "Backend API" section to README
- [ ] Include curl examples for auth
- [ ] Include curl examples for pipeline
- [ ] Include example responses

**Acceptance**: README has API docs

### Task 7.6: Create Example Usage Script
- [ ] Create `example_api_usage.py`
- [ ] Demonstrate register, login, run pipeline, get results
- [ ] Include comments explaining each step

**Acceptance**: Script runs successfully

### Task 7.7: Run Full Test Suite
- [ ] Execute `pytest tests/backend_api/`
- [ ] Verify 80-100 tests passing
- [ ] Check test coverage

**Acceptance**: All tests green

### Task 7.8: Phase 7 Complete
- [ ] Update README with Module 005 status
- [ ] Update project structure in README
- [ ] Commit Phase 7 work

**Acceptance**: Module 005 complete

---

## Summary

| Phase | Tasks | Estimated Tests |
|-------|-------|-----------------|
| Phase 1: Setup & Database | 12 | 12-17 |
| Phase 2: Authentication | 13 | 15-20 |
| Phase 3: Pipeline Orchestration | 10 | 20-25 |
| Phase 4: Pipeline Router | 8 | 15-20 |
| Phase 5: Projects Router | 8 | 15-20 |
| Phase 6: Error Handling | 6 | 10-15 |
| Phase 7: Integration & Docs | 8 | 5-10 |
| **Total** | **65** | **92-127** |

## Execution Approach

1. Work through phases sequentially (1 → 7)
2. Within each phase, complete tasks in order
3. Write tests before implementation (TDD)
4. Run tests after each task/group of tasks
5. Commit at end of each phase
6. Final E2E test with real module integration

## Success Criteria

- ✅ All ~90-120 tests passing for Module 005
- ✅ Full pipeline execution works via API
- ✅ Authentication and authorization working
- ✅ Users can register, login, run pipelines, view projects
- ✅ API documentation auto-generated
- ✅ Total project tests: ~290-320
