# GitHire Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-10-06

## Project Overview

**GitHire**: AI-powered recruitment platform that sources GitHub developers based on job requirements.

**Architecture**: Modular pipeline with 6 modules (001-006)
**Methodology**: Spec-It driven development (Research → Design → Tasks → Implementation)
**Constitution**: 5 core principles (AI-First, Privacy-First, Single Source, Transparency, Modular)

---

## Active Technologies

### Module 001: JD Parser
- **Language**: Python 3.11+
- **LLM**: OpenAI GPT-4o-mini with JSON mode
- **Validation**: Pydantic v2
- **Testing**: pytest 7.4+
- **Status**: ✅ Complete (24/24 tasks, 33/33 tests passing)

### Module 002: GitHub Sourcer
- **Language**: Python 3.11+
- **HTTP Client**: httpx (async)
- **Cache**: Redis 5.0+ (1-hour TTL, two-tier structure)
- **Validation**: Pydantic v2
- **Testing**: pytest + pytest-asyncio
- **Authentication**: GitHub Personal Access Token (PAT)
- **API**: GitHub REST API (`/search/users` + profile endpoints)
- **Status**: 🔨 In Progress (Phase 1: Design & Contracts)

---

## Project Structure

```
juicebox/
├── .specify/                           # Spec-It methodology files
│   ├── agents/
│   │   └── CLAUDE.md                   # This file
│   ├── memory/
│   │   └── constitution.md             # 5 core principles
│   └── templates/                      # Spec/plan/tasks templates
│
├── specs/                              # Feature specifications
│   ├── 001-jd-parser-module/          # Module 001 (COMPLETE)
│   │   ├── spec.md                    # Feature spec
│   │   ├── plan.md                    # Implementation plan
│   │   ├── research.md                # Phase 0 output
│   │   ├── data-model.md              # Phase 1 output
│   │   ├── tasks.md                   # Phase 2 output
│   │   ├── quickstart.md              # Manual test scenarios
│   │   └── contracts/                 # JSON schemas
│   │       ├── input-schema.json
│   │       └── output-schema.json
│   │
│   └── 002-github-sourcer-module/     # Module 002 (IN PROGRESS)
│       ├── spec.md
│       ├── plan.md
│       ├── research.md                # ✅ Complete
│       ├── data-model.md              # ✅ Complete
│       ├── quickstart.md              # ✅ Complete
│       └── contracts/                 # ✅ Complete
│           ├── input-schema.json
│           └── output-schema.json
│
├── src/                               # Source code
│   ├── jd_parser/                     # Module 001 (COMPLETE)
│   │   ├── models.py                  # JobRequirement, ConfidenceScore
│   │   ├── parser.py                  # Main JDParser class
│   │   ├── llm_client.py              # OpenAI/Anthropic abstraction
│   │   ├── skill_normalizer.py        # Skill mapping + LLM fallback
│   │   ├── validators.py              # Input/output validation
│   │   ├── cli.py                     # Command-line interface
│   │   └── prompts/
│   │       └── extraction_prompt.txt  # LLM prompt template
│   │
│   ├── github_sourcer/                # Module 002 (PENDING)
│   │   ├── models/                    # Candidate, SearchResult
│   │   ├── services/                  # GitHub client, search, cache
│   │   └── lib/                       # Rate limiter
│   │
│   └── config/
│       └── skill_mappings.json        # 40+ skill normalizations
│
├── tests/
│   ├── contract/                      # Schema validation tests
│   ├── integration/                   # End-to-end tests
│   └── unit/                          # Isolated component tests
│
├── .env                               # API keys (gitignored)
├── .gitignore
├── pyproject.toml                     # Dependencies
└── README.md
```

---

## Commands

### Development Workflow

```bash
# Install dependencies
pip install -e .

# Run all tests
pytest -v

# Run specific test category
pytest tests/contract/ -v
pytest tests/integration/ -v
pytest tests/unit/ -v

# Module 001: Parse job description
python -m src.jd_parser.cli "Looking for Senior Python dev with 5 years exp"
python -m src.jd_parser.cli --file jd.txt
echo "..." | python -m src.jd_parser.cli --stdin

# Module 002: Search GitHub (PENDING IMPLEMENTATION)
python -m src.github_sourcer.cli --input job_requirement.json
```

### Environment Setup

```bash
# Module 001: OpenAI API key
export OPENAI_API_KEY="sk-..."

# Module 002: GitHub PAT (PENDING)
export GITHUB_TOKEN="ghp_..."

# Module 002: Redis (PENDING)
redis-server
# Or via Docker:
docker run -d -p 6379:6379 redis:7-alpine
```

### Testing

```bash
# Run tests with coverage
pytest --cov=src --cov-report=term-missing

# Run only failing tests
pytest --lf

# Run with verbose output
pytest -vv -s
```

---

## Code Style

### Python Style Guidelines

1. **Type Hints**: Always use type hints (Python 3.11+ syntax)
   ```python
   def parse(self, jd_text: str) -> JobRequirement:
       ...
   ```

2. **Pydantic Models**: Use for all data validation
   ```python
   from pydantic import BaseModel, Field

   class Candidate(BaseModel):
       github_username: str = Field(..., min_length=1)
       languages: list[str] = Field(default_factory=list)
   ```

3. **Async/Await**: Use for I/O-bound operations (Module 002+)
   ```python
   async def fetch_profile(self, username: str) -> Candidate:
       async with httpx.AsyncClient() as client:
           response = await client.get(f"https://api.github.com/users/{username}")
   ```

4. **Error Handling**: Graceful degradation for external services
   ```python
   try:
       profile = await fetch_profile(username)
   except Exception as e:
       logger.warning(f"Failed to fetch {username}: {e}")
       # Continue with partial results
   ```

5. **Logging**: Use structured logging
   ```python
   import logging
   logger = logging.getLogger(__name__)
   logger.info(f"Parsed JD with {len(skills)} skills")
   ```

6. **Configuration**: Use environment variables
   ```python
   import os
   OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
   ```

---

## Data Models

### Module 001: JobRequirement (Output)

```python
{
  "role": "Senior Python Developer",
  "required_skills": ["Python", "FastAPI", "PostgreSQL"],
  "preferred_skills": ["Docker", "Kubernetes"],
  "years_of_experience": {
    "min": 5,
    "max": null,
    "range_text": "5+ years"
  },
  "seniority_level": "Senior",
  "location_preferences": ["India", "Remote"],
  "domain": "FinTech",
  "confidence_scores": {
    "role": {"score": 0.95, "source": "explicit"}
  },
  "original_input": "...",
  "schema_version": "1.0.0"
}
```

### Module 002: Candidate (Output - PENDING)

```python
{
  "github_username": "torvalds",
  "name": "Linus Torvalds",
  "bio": "Creator of Linux and Git",
  "location": "Portland, OR",
  "top_repos": [
    {
      "name": "linux",
      "stars": 150000,
      "languages": ["C", "Assembly"],
      "url": "https://github.com/torvalds/linux"
    }
  ],
  "languages": ["C", "Assembly", "Shell"],
  "contribution_count": 2500,
  "account_age_days": 5000,
  "followers": 200000,
  "profile_url": "https://github.com/torvalds",
  "fetched_at": "2025-10-06T10:30:00Z"
}
```

---

## Recent Changes

### Module 001: JD Parser (2025-10-06) - ✅ COMPLETE
**What**: Parses unstructured job descriptions into structured JobRequirement JSON
**Added**:
- OpenAI GPT-4o-mini integration with JSON mode
- Pydantic v2 models with validation
- Skill normalization (40+ mappings + LLM fallback)
- CLI with file/stdin/inline input support
- 33 tests (15 contract + 18 integration) - all passing

**Key Files**:
- `src/jd_parser/models.py` - JobRequirement, ConfidenceScore
- `src/jd_parser/parser.py` - Main orchestration
- `src/jd_parser/llm_client.py` - OpenAI/Anthropic abstraction
- `src/config/skill_mappings.json` - Skill normalization

**Usage**:
```bash
python -m src.jd_parser.cli "Senior Python dev, 5 yrs exp"
```

---

### Module 002: GitHub Sourcer (2025-10-06) - 🔨 IN PROGRESS
**What**: Searches GitHub API for developers matching JobRequirement
**Phase Status**: Phase 1 (Design & Contracts) - Nearly Complete

**Research Decisions Made**:
1. REST `/search/users` API over GraphQL (simpler for POC)
2. Personal Access Token authentication (5000 req/hour)
3. httpx async client (sync/async flexibility)
4. Two-tier Redis caching: `search:{hash}` → usernames, `profile:{username}` → data
5. Rate limit: Proactive tracking + exponential backoff + partial results

**Data Models Designed**:
- `Candidate` - GitHub developer profile with repos, languages, activity
- `SearchCriteria` - Internal mapping from JobRequirement to GitHub query
- `SearchResult` - Metadata (total found, returned count, rate limits, cache hit)

**Contracts Created**:
- `contracts/input-schema.json` - Validates JobRequirement input
- `contracts/output-schema.json` - Validates Candidate + SearchResult output

**Next Steps**:
- Generate tasks.md (Phase 2)
- Implement GitHub client, search service, cache service (Phase 3)
- Validate with 7 quickstart scenarios (Phase 5)

---

### Module 003-006: Ranking, Contact, Outreach, Analytics (PENDING)
**Status**: Specifications created, clarifications resolved, implementation pending

---

## Constitution Compliance

All modules must follow 5 core principles:

1. **AI-First Development**: Use LLMs for core logic (Module 001: parsing, Module 003: ranking)
2. **Privacy-First Architecture**: Only public data, no scraping, GDPR compliant
3. **Single Source of Truth**: GitHub only, no LinkedIn/job board mixing
4. **Transparency & Explainability**: Return metadata (confidence scores, rate limits, cache status)
5. **Modular Architecture**: Clear input/output contracts, independently testable

**Gate Check**: Each module verifies constitution compliance before Phase 0 research.

---

## Testing Strategy

1. **Contract Tests**: Validate JSON schemas match specification
2. **Unit Tests**: Mock all external dependencies (LLM, GitHub API, Redis)
3. **Integration Tests**: End-to-end tests with real services (limited calls)
4. **TDD Approach**: Write failing tests before implementation

**Coverage Goal**: >80% line coverage, 100% contract coverage

---

<!-- MANUAL ADDITIONS START -->
<!-- Add project-specific notes here -->
<!-- MANUAL ADDITIONS END -->
