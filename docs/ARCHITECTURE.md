# GitHire Architecture

## System Overview

GitHire is a full-stack AI-powered recruitment platform that sources, ranks, and helps you reach out to software developers using GitHub as the primary talent source.

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (React)                          │
│  - Dashboard UI                                                  │
│  - Project Management                                            │
│  - Candidate Browsing & Shortlisting                            │
│  - Outreach Message Generation                                  │
└─────────────────┬───────────────────────────────────────────────┘
                  │ REST API (HTTP/JSON)
┌─────────────────▼───────────────────────────────────────────────┐
│                    Backend API (FastAPI)                         │
│  - Authentication (JWT)                                          │
│  - Project Management                                            │
│  - Pipeline Orchestration                                        │
│  - Multi-Stage Workflow                                          │
└─────────────────┬───────────────────────────────────────────────┘
                  │
    ┌─────────────┼─────────────┬─────────────┬─────────────┐
    │             │             │             │             │
┌───▼────┐  ┌────▼────┐  ┌─────▼────┐  ┌────▼─────┐  ┌───▼────┐
│Module 1│  │Module 2 │  │Module 3  │  │Module 4  │  │Module 5│
│JD      │  │GitHub   │  │Ranking   │  │Outreach  │  │Contact │
│Parser  │  │Sourcer  │  │Engine    │  │Generator │  │Enricher│
└───┬────┘  └────┬────┘  └─────┬────┘  └────┬─────┘  └───┬────┘
    │             │             │             │             │
    └─────────────┴─────────────┴─────────────┴─────────────┘
                            │
              ┌─────────────┼──────────────┐
              │             │              │
         ┌────▼───┐    ┌───▼────┐    ┌───▼────┐
         │SQLite  │    │OpenAI  │    │GitHub  │
         │Database│    │API     │    │API     │
         └────────┘    └────────┘    └────────┘
```

## Tech Stack

### Frontend
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State Management**: React Query (TanStack Query)
- **Routing**: React Router v6
- **HTTP Client**: Axios
- **Icons**: Heroicons

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: JWT (JSON Web Tokens)
- **API Documentation**: Auto-generated OpenAPI/Swagger
- **Async Runtime**: asyncio

### Core Modules
- **LLM Integration**: OpenAI GPT-4 (JD parsing, skill matching, outreach generation)
- **GitHub Integration**: GitHub REST API + GraphQL
- **Caching**: Redis (optional, for GitHub API responses)

## Module Architecture

### Module 001: JD Parser
**Purpose**: Parse natural language job descriptions into structured data

**Input**: Raw job description text
**Output**: Structured `JobRequirement` object

```python
JobRequirement {
    role: str
    required_skills: List[str]
    experience_years: Optional[int]
    location: Optional[str]
    preferred_skills: List[str]
    confidence_scores: Dict[str, float]
}
```

**Key Components**:
- `JDParser`: Main orchestrator
- `LLMClient`: OpenAI API wrapper
- `SkillNormalizer`: Skill mapping and normalization
- `Validators`: Input/output validation

**LLM Strategy**:
- Model: GPT-4o-mini
- Mode: JSON output with structured schema
- Fallback: Skill normalization with predefined mappings

### Module 002: GitHub Sourcer
**Purpose**: Search GitHub for developers matching job requirements

**Input**: `JobRequirement` from Module 001
**Output**: List of `Candidate` objects

```python
Candidate {
    github_username: str
    profile_url: str
    bio: Optional[str]
    location: Optional[str]
    email: Optional[str]
    company: Optional[str]
    public_repos: int
    followers: int
    following: int
    created_at: datetime
    detected_skills: Dict[str, SkillConfidence]
    top_languages: List[str]
    top_repositories: List[Repository]
}
```

**Key Components**:
- `SearchService`: Main orchestrator
- `GitHubClient`: GitHub API wrapper (REST + GraphQL)
- `ProfileEnricher`: Parallel async profile enrichment
- `SkillDetector`: Multi-signal skill detection
- `LocationParser`: Hierarchical location parsing
- `CacheService`: Redis-based two-tier caching

**Performance Optimizations**:
- Async parallel profile enrichment (25 profiles in ~4 seconds)
- Two-tier caching (search results + individual profiles)
- GraphQL batching for reduced API calls
- Rate limiting with exponential backoff

### Module 003: Ranking Engine
**Purpose**: Score and rank candidates based on job requirements

**Input**: List of `Candidate` + `JobRequirement`
**Output**: List of `RankedCandidate` (sorted by score)

```python
RankedCandidate {
    ...all Candidate fields...
    rank: int
    total_score: float  # 0-100
    skill_match_score: float
    experience_score: float
    activity_score: float
    domain_score: float
    score_breakdown: ScoreBreakdown
}
```

**Scoring Dimensions** (configurable weights):
- **Skills** (40%): LLM semantic matching + percentage calculation
- **Experience** (20%): Account age + stars + repo count
- **Activity** (20%): Followers + contributions + active repos
- **Domain** (20%): LLM-based project relevance

**Key Components**:
- `Ranker`: Main orchestrator
- `SkillMatcher`: LLM-based semantic skill matching
- `SkillScorer`: Skills scoring logic
- `ExperienceScorer`: Experience scoring
- `ActivityScorer`: Activity scoring
- `DomainScorer`: Domain relevance scoring

### Module 004: Outreach Generator
**Purpose**: Generate personalized outreach messages

**Input**: `RankedCandidate` + `JobRequirement`
**Output**: `OutreachMessage`

```python
OutreachMessage {
    candidate_username: str
    rank: int
    channel: str  # email, linkedin, twitter
    subject_line: Optional[str]  # email only
    message_text: str
    personalization_score: float  # 0-100
    personalization_metadata: Dict
    tokens_used: int
    stage_breakdown: Dict
    confidence_score: float
    tone: str  # formal, casual
}
```

**Multi-Channel Support**:
- Email (with subject line)
- LinkedIn
- Twitter/X

**Personalization Strategy**:
- **Deep** (rank 1-5): Detailed repo analysis, specific contributions
- **Medium** (rank 6-15): General repo mentions, tech stack
- **Surface** (rank 16+): Generic skills-based message

**Key Components**:
- `OutreachGenerator`: Main orchestrator
- `PersonalizationEngine`: Repo selection & depth determination
- `ContentValidator`: Safety and quality checks
- `PromptTemplates`: Formal and casual tone templates

### Module 005: Backend API
**Purpose**: REST API for frontend integration

**Endpoints**:
- `POST /auth/register` - User registration
- `POST /auth/login` - User authentication
- `POST /auth/logout` - Session invalidation
- `GET /auth/me` - Get current user profile
- `PUT /auth/me` - Update user profile
- `POST /projects` - Create new project
- `GET /projects` - List user's projects
- `GET /projects/{id}` - Get project details
- `DELETE /projects/{id}` - Delete project
- `POST /projects/{id}/source` - Source candidates
- `POST /projects/{id}/rank` - Rank candidates
- `POST /projects/{id}/shortlist` - Shortlist candidates
- `GET /projects/{id}/shortlisted` - Get shortlisted candidates
- `POST /projects/{id}/enrich/{username}` - Enrich candidate
- `POST /outreach/{project_id}/{username}` - Generate outreach
- `PUT /outreach/{id}` - Update outreach message
- `POST /outreach/{id}/send` - Mark as sent
- `POST /outreach/{id}/followups` - Generate follow-ups

**Authentication**:
- JWT-based authentication
- Bearer token in Authorization header
- 24-hour token expiration
- Session management in database

**Key Components**:
- `AuthRouter`: Authentication endpoints
- `ProjectsRouter`: Project management
- `WorkflowRouter`: Multi-stage pipeline
- `OutreachRouter`: Outreach generation
- `Database`: SQLAlchemy async ORM

## Database Schema

```sql
-- Users table
CREATE TABLE users (
    user_id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    created_at DATETIME NOT NULL,
    last_login DATETIME
);

-- Projects table
CREATE TABLE projects (
    project_id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    name VARCHAR(255),
    job_title VARCHAR(255),
    job_description_text TEXT NOT NULL,
    location VARCHAR(500),
    status VARCHAR(50) NOT NULL,  -- draft, sourcing, sourced, ranking, ranked, shortlisted
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    pipeline_start_time DATETIME,
    pipeline_end_time DATETIME,
    candidate_count INTEGER DEFAULT 0,
    avg_score FLOAT,
    results_json JSON,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Shortlisted candidates table
CREATE TABLE shortlisted_candidates (
    shortlist_id VARCHAR(36) PRIMARY KEY,
    project_id VARCHAR(36) NOT NULL,
    github_username VARCHAR(255) NOT NULL,
    candidate_data JSON NOT NULL,
    enriched_data JSON,
    enrichment_status VARCHAR(50) NOT NULL,  -- pending, in_progress, completed, failed
    enriched_at DATETIME,
    created_at DATETIME NOT NULL,
    FOREIGN KEY (project_id) REFERENCES projects(project_id),
    UNIQUE(project_id, github_username)
);

-- Outreach messages table
CREATE TABLE outreach_messages (
    outreach_id VARCHAR(36) PRIMARY KEY,
    project_id VARCHAR(36) NOT NULL,
    github_username VARCHAR(255) NOT NULL,
    channel VARCHAR(50) NOT NULL,  -- email, linkedin, twitter
    subject_line VARCHAR(500),
    message_text TEXT NOT NULL,
    personalization_score FLOAT NOT NULL,
    personalization_metadata JSON NOT NULL,
    tokens_used INTEGER NOT NULL,
    stage_breakdown JSON NOT NULL,
    is_edited BOOLEAN DEFAULT FALSE,
    edited_message TEXT,
    edited_at DATETIME,
    status VARCHAR(50) NOT NULL,  -- draft, sent
    sent_at DATETIME,
    generated_at DATETIME NOT NULL,
    FOREIGN KEY (project_id) REFERENCES projects(project_id),
    UNIQUE(project_id, github_username, channel)
);

-- Follow-up sequences table
CREATE TABLE follow_up_sequences (
    followup_id VARCHAR(36) PRIMARY KEY,
    outreach_message_id VARCHAR(36) NOT NULL,
    sequence_number INTEGER NOT NULL,  -- 1, 2, 3
    scheduled_days_after INTEGER NOT NULL,  -- 3, 7, 14
    message_text TEXT NOT NULL,
    angle VARCHAR(50) NOT NULL,  -- reminder, technical_challenge, career_growth, soft_close
    generated_at DATETIME NOT NULL,
    sent_at DATETIME,
    FOREIGN KEY (outreach_message_id) REFERENCES outreach_messages(outreach_id)
);

-- Sessions table
CREATE TABLE sessions (
    session_id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    token TEXT NOT NULL,
    created_at DATETIME NOT NULL,
    expires_at DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

## Data Flow

### Complete Pipeline Flow

```
1. User Input (Frontend)
   ↓
2. POST /projects (Create project)
   ↓
3. POST /projects/{id}/source
   ├─→ Module 001: JD Parser
   │   └─→ Extract job requirements
   ├─→ Module 002: GitHub Sourcer
   │   ├─→ Build search query
   │   ├─→ Search GitHub API
   │   ├─→ Enrich profiles (async)
   │   └─→ Return candidates
   └─→ Save to database (status: sourced)
   ↓
4. POST /projects/{id}/rank
   ├─→ Module 003: Ranking Engine
   │   ├─→ Score each candidate
   │   └─→ Sort by total score
   └─→ Save to database (status: ranked)
   ↓
5. User Reviews & Shortlists (Frontend)
   ├─→ POST /projects/{id}/shortlist
   └─→ Save to shortlisted_candidates table
   ↓
6. POST /projects/{id}/enrich/{username}
   ├─→ Module 005: Contact Enrichment
   │   └─→ Fetch additional profile data
   └─→ Update enriched_data field
   ↓
7. POST /outreach/{project_id}/{username}
   ├─→ Module 004: Outreach Generator
   │   ├─→ Analyze candidate profile
   │   ├─→ Generate personalized message
   │   └─→ Validate content
   └─→ Save to outreach_messages table
   ↓
8. POST /outreach/{id}/followups
   ├─→ Generate 3 follow-up sequences
   └─→ Save to follow_up_sequences table
   ↓
9. User Edits & Sends (Frontend)
   ├─→ PUT /outreach/{id} (edit)
   └─→ POST /outreach/{id}/send (mark as sent)
```

## Frontend Architecture

### Component Structure

```
src/
├── components/
│   ├── ui/                      # Reusable UI components
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   ├── StatCard.tsx
│   │   ├── Avatar.tsx
│   │   ├── Dropdown.tsx
│   │   └── Logo.tsx
│   ├── dashboard/               # Dashboard-specific
│   │   ├── QuickActions.tsx
│   │   └── PipelineVisualization.tsx
│   ├── Navigation.tsx           # Main navigation
│   ├── CreateProjectModal.tsx  # Project creation
│   ├── OutreachPanel.tsx       # Outreach generation
│   └── FollowUpPanel.tsx       # Follow-up sequences
├── pages/
│   ├── DashboardPage.tsx       # Main dashboard
│   ├── ProjectsPage.tsx        # Projects list
│   ├── ProjectDetailPage.tsx   # Project details
│   ├── ShortlistPage.tsx       # Candidate shortlisting
│   ├── ShortlistedCandidatesPage.tsx  # Shortlisted view
│   ├── ProfilePage.tsx         # User profile
│   ├── LoginPage.tsx           # Login
│   └── RegisterPage.tsx        # Registration
├── contexts/
│   ├── AuthContext.tsx         # Authentication state
│   └── ToastContext.tsx        # Toast notifications
├── api/
│   ├── client.ts               # Axios instance
│   ├── auth.ts                 # Auth API methods
│   ├── projects.ts             # Projects API methods
│   ├── workflow.ts             # Workflow API methods
│   └── outreach.ts             # Outreach API methods
└── types/
    ├── auth.ts                 # Auth types
    ├── project.ts              # Project types
    └── outreach.ts             # Outreach types
```

### State Management

- **React Query**: Server state caching and synchronization
- **Context API**: Authentication and global UI state
- **Local State**: Component-specific state with useState/useReducer

### Routing

```typescript
/                           → Redirect to /dashboard
/login                      → Public (LoginPage)
/register                   → Public (RegisterPage)
/dashboard                  → Protected (DashboardPage)
/projects                   → Protected (ProjectsPage)
/projects/:projectId        → Protected (ProjectDetailPage)
/projects/:projectId/shortlist → Protected (ShortlistPage)
/projects/:projectId/shortlisted → Protected (ShortlistedCandidatesPage)
/profile                    → Protected (ProfilePage)
```

## Security Considerations

### Authentication
- JWT tokens with 24-hour expiration
- Passwords hashed with bcrypt (12 rounds)
- Session invalidation on logout
- Protected routes with authentication middleware

### API Security
- CORS enabled for frontend origin only
- Rate limiting (to be implemented)
- Input validation with Pydantic
- SQL injection prevention with ORM

### Data Privacy
- Only public GitHub data accessed
- User data encrypted at rest (to be implemented)
- GDPR compliance considerations
- No third-party analytics (privacy-first)

## Performance Optimizations

### Backend
- Async/await for I/O operations
- Parallel profile enrichment (asyncio.gather)
- Redis caching for GitHub API responses
- GraphQL batching to reduce API calls
- Connection pooling for database

### Frontend
- Code splitting with React.lazy
- Image optimization
- React Query caching
- Virtualized lists for large datasets (to be implemented)
- Debounced search inputs

## Monitoring & Logging

### Current Implementation
- FastAPI automatic request logging
- Error stack traces in development
- Basic console logging

### Future Enhancements
- Structured logging with correlation IDs
- Application Performance Monitoring (APM)
- Error tracking (Sentry)
- Metrics collection (Prometheus)
- Distributed tracing

## Scalability Considerations

### Current Architecture
- SQLite database (suitable for POC and small deployments)
- Single-server deployment
- Synchronous task execution

### Future Scaling Path
1. **Database**: Migrate to PostgreSQL for concurrent writes
2. **Caching**: Redis for session storage and API caching
3. **Queue**: Celery/RQ for background jobs (pipeline execution)
4. **Load Balancing**: Multiple FastAPI instances behind nginx
5. **CDN**: Static asset delivery
6. **Microservices**: Split modules into separate services (if needed)

## Development Workflow

1. **Local Development**: Vite dev server + FastAPI uvicorn with hot reload
2. **Testing**: pytest for backend, vitest for frontend
3. **Linting**: ruff (Python), ESLint (TypeScript)
4. **Type Checking**: mypy (Python), TypeScript compiler
5. **CI/CD**: GitHub Actions (to be implemented)
6. **Deployment**: Docker containers (to be implemented)

---

**Last Updated**: 2025-10-10
