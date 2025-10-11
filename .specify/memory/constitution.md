<!--
Sync Impact Report:
- Version: 0.0.0 → 1.0.0
- Rationale: Initial constitution creation for GitHire project
- Principles defined: 5 core principles
- Added sections: Data Privacy & Compliance, Development Workflow
- Templates: All templates aligned with new constitution
- Follow-up: None
-->

# GitHire Constitution

## Core Principles

### I. AI-First Development
Every feature leverages Large Language Models (LLMs) for intelligent automation:
- Job Description (JD) parsing MUST use LLM-based extraction for skills, experience, and requirements
- Personalized outreach generation MUST use LLMs to analyze candidate profiles and create contextual messages
- AI components MUST be modular and replaceable (support for different LLM providers)
- Prompts and AI interactions MUST be logged for debugging and improvement

**Rationale**: AI is the core differentiator; relying on regex or keyword matching would miss nuanced requirements and fail to generate authentic personalized outreach.

### II. Privacy-First Architecture
Only public data sources are used; no unauthorized data collection:
- MUST use only public GitHub APIs and publicly accessible profile information
- MUST NOT scrape private repositories, private profile data, or email addresses not publicly listed
- MUST provide clear opt-out mechanism for candidates who don't wish to be contacted
- MUST comply with GDPR for EU-based candidates (data minimization, right to erasure)

**Rationale**: Privacy violations destroy trust and create legal liability. GitHire builds on open-source principles and respects developer autonomy.

### III. Single Source of Truth
GitHub API is the exclusive candidate data source for this POC:
- MUST NOT integrate with LinkedIn, job boards, or other platforms in initial version
- All candidate data (repos, languages, contributions, bio) MUST come from GitHub REST/GraphQL API
- GitHub API rate limits MUST be respected (use authentication for 5000 req/hour)
- Caching strategy MUST be implemented to minimize redundant API calls

**Rationale**: Focusing on a single source reduces complexity, ensures data consistency, and allows rapid prototyping. GitHub provides rich technical signals for developer recruitment.

### IV. Transparency & Explainability
Users MUST understand how and why candidates are ranked:
- Ranking algorithm logic MUST be visible to users (show scoring breakdown)
- Each candidate score MUST show contributing factors (skill match %, activity level, domain relevance)
- AI-generated outreach MUST show which candidate attributes influenced the message
- No "black box" decisions - all automation is explainable

**Rationale**: Trust requires transparency. Recruiters need to understand recommendations to make informed hiring decisions and comply with anti-discrimination requirements.

### V. Modular Architecture
Clear separation of concerns enables independent development and testing:
- JD Parser: Standalone module (input: raw JD text → output: structured requirements)
- GitHub Sourcer: Independent service (input: requirements → output: candidate list with metadata)
- Ranking Engine: Pure function (input: candidates + JD → output: scored candidates)
- Outreach Generator: Isolated component (input: candidate profile + JD → output: personalized message)
- Each module MUST have well-defined interfaces (contracts)
- Each module MUST be independently testable with mocks

**Rationale**: Modularity enables parallel development, easier testing, and future extensibility (e.g., adding LinkedIn as a source later).

## Data Privacy & Compliance

### GDPR Compliance
- Data retention: Candidate data deleted after 30 days or when user deletes search
- Right to erasure: API endpoint to remove candidate from all searches
- Data minimization: Store only necessary fields (GitHub username, public profile data, repositories)
- Consent: Outreach messages must include opt-out link

### API Usage Policies
- GitHub API Terms of Service MUST be strictly followed
- Rate limiting MUST be implemented (max 5000 authenticated requests/hour)
- No bulk scraping or automated account creation
- Attribution: GitHub logo and "Powered by GitHub" on candidate profiles

## Development Workflow

### Test-Driven Development (TDD)
- All features start with failing tests
- Integration tests for AI components (mock LLM responses for deterministic tests)
- Contract tests for module interfaces
- E2E test: paste JD → receive ranked candidates with outreach messages

### Code Quality Gates
- All PRs require:
  - Passing tests (unit + integration)
  - Type checking (TypeScript strict mode or Python type hints)
  - Linting (ESLint/Prettier or ruff/black)
  - API rate limit validation (no hard-coded tokens, respect quotas)

### Documentation Requirements
- Each module: README with usage examples
- API endpoints: OpenAPI/Swagger documentation
- AI prompts: Version-controlled with changelog explaining modifications

## Governance

This constitution establishes non-negotiable principles for GitHire development. All features, refactors, and architectural decisions MUST align with these principles.

**Amendment Process**:
- Amendments require documented justification and impact analysis
- Version bump follows semantic versioning (MAJOR for principle changes)
- All templates and documentation updated to reflect amendments

**Compliance Verification**:
- Every PR must include constitution compliance checklist
- Weekly review of AI usage for bias and fairness
- Monthly GitHub API usage audit to ensure Terms of Service compliance

**Version**: 1.0.0 | **Ratified**: 2025-10-05 | **Last Amended**: 2025-10-05
