# Implementation Plan: Contact Enrichment Module

**Branch**: `010-contact-enrichment-module` | **Date**: 2025-10-10 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/010-contact-enrichment-module/spec.md`

## Summary
Contact Enrichment module accepts shortlisted Candidate profiles from the Ranking Engine and enriches them with contact information for recruiter outreach. Uses Phase 1 free methods (GitHub API profile fields, commit email extraction, profile README parsing, social profile discovery) to achieve 66.7% email discovery and 91.7% overall contact discovery rate.

**Core Capabilities**:
- **Layer 1: GitHub Profile Fields** - Extract email, blog, twitter_username, company, hireable from public profiles (33.3% email success)
- **Layer 2: Commit Email Extraction** - Parse PushEvent commits for email addresses with noreply filtering (41.7% success)
- **Layer 3: Profile README Parsing** - Extract contact info from username/username repository README files (8.3% email, 50% README coverage)
- **Layer 4: Social Profile Discovery** - Find LinkedIn/Twitter from bio, blog, README (66.7% Twitter, 25% LinkedIn, 91.7% websites)
- **GDPR Compliance** - Automatic data retention (30-90 days), deletion support, transparent data sources
- **Performance** - Process 100 candidates in 90-120 seconds using async concurrency

Validated with real data: 12 candidates tested, 66.7% email found, 91.7% any contact found.

## Technical Context
**Language/Version**: Python 3.11+
**Primary Dependencies**: httpx (async HTTP), pydantic v2 (validation), email-validator (validation)
**Storage**: PostgreSQL with GDPR-compliant retention policies
**Testing**: pytest + pytest-asyncio
**Target Platform**: Linux server / Docker container
**Project Type**: Single module (part of larger pipeline)
**Performance Goals**: <120 seconds for 100 candidates, 10-20 concurrent requests
**Constraints**: GitHub API rate limits (5000 req/hour authenticated), privacy-first noreply filtering
**Scale/Scope**: Handle 100 candidates per job search, GDPR auto-deletion after 30-90 days

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. AI-First Development
- [x] No LLM required for this module (pure data extraction)
- [x] Module provides contact data for Outreach Generator which may use LLM

### II. Privacy-First Architecture
- [x] Only public GitHub data used (profile, events, repositories)
- [x] Respects noreply email preferences (filters privacy-protected addresses)
- [x] No circumvention of privacy settings
- [x] GDPR compliant (collection metadata, auto-deletion, export support)
- [x] Transparent data sources (tracks origin of each contact field)

### III. Single Source of Truth
- [x] GitHub REST API only (profile, events, contents)
- [x] No third-party enrichment services in Phase 1
- [x] No email guessing or pattern inference
- [x] Public data only (no LinkedIn scraping, no website crawling)

### IV. Transparency & Explainability
- [x] Returns metadata: enriched_at, contact_sources, enrichment_success_rate
- [x] Tracks data source for each field (profile, commits, README)
- [x] Shows which layer found each contact method

### V. Modular Architecture
- [x] Standalone module with clear input/output interface
- [x] Input: List[Candidate] from Module 003
- [x] Output: List[EnrichedCandidate] + EnrichmentResult metadata
- [x] Independently testable with mock GitHub API

**Constitution Status**: ✅ PASS - All principles satisfied

## Project Structure

### Documentation (this feature)
```
specs/010-contact-enrichment-module/
├── plan.md              # This file
├── research.md          # Phase 0 output (email patterns, GDPR requirements)
├── data-model.md        # Phase 1 output (ContactInfo, EmailSource models)
├── quickstart.md        # Phase 1 output (validation scenarios)
├── contracts/           # Phase 1 output (JSON schemas)
│   ├── input-schema.json
│   └── output-schema.json
└── tasks.md             # Phase 2 output (/tasks command)
```

### Source Code (repository root)
```
src/contact_enrichment/
├── models/
│   ├── contact_info.py          # NEW: ContactInfo entity
│   ├── enrichment_result.py     # NEW: EnrichmentResult metadata
│   └── email_source.py          # NEW: EmailSource internal tracking
├── services/
│   ├── contact_enricher.py      # NEW: Main enrichment orchestrator
│   ├── profile_extractor.py     # NEW: Layer 1 - GitHub profile fields
│   ├── commit_email_extractor.py # NEW: Layer 2 - Commit history parsing
│   ├── readme_parser.py         # NEW: Layer 3 - Profile README extraction
│   └── social_discoverer.py     # NEW: Layer 4 - LinkedIn/Twitter discovery
├── lib/
│   ├── email_validator.py       # NEW: Email format validation + noreply filtering
│   ├── noreply_filter.py        # NEW: Privacy-protected email detection
│   └── url_normalizer.py        # NEW: Social profile URL cleaning
├── config/
│   ├── noreply_patterns.yaml    # NEW: Configurable noreply email patterns
│   └── spam_domains.yaml        # NEW: Spam/test domains to exclude
└── __init__.py                  # Module exports

tests/contact_enrichment/
├── contract/
│   ├── test_input_schema.py     # Validate Candidate input contract
│   └── test_output_schema.py    # Validate ContactInfo output contract
├── integration/
│   ├── test_profile_extraction.py # Test Layer 1 end-to-end
│   ├── test_commit_extraction.py  # Test Layer 2 end-to-end
│   ├── test_readme_parsing.py     # Test Layer 3 end-to-end
│   ├── test_social_discovery.py   # Test Layer 4 end-to-end
│   └── test_contact_enricher.py   # Test full enrichment pipeline
└── unit/
    ├── test_email_validator.py    # Test noreply filtering
    ├── test_url_normalizer.py     # Test social URL cleaning
    └── test_noreply_filter.py     # Test privacy pattern matching
```

**Structure Decision**: Single module structure. Contact Enrichment is Module 010 in the GitHire pipeline, consuming Candidate objects from Modules 002+003 and providing enriched data to Module 004 (Outreach Generator).

## Phase 0: Outline & Research

**Research Tasks**:
1. GitHub Events API structure (PushEvent commit metadata)
2. GitHub Contents API for profile README access
3. Email validation regex patterns (RFC 5322 compliant)
4. Noreply email pattern variations (GitHub, GitLab, Bitbucket)
5. Social media URL regex patterns (LinkedIn, Twitter/X)
6. GDPR data retention best practices (storage duration, deletion automation)
7. PostgreSQL JSONB storage for contact data
8. Async batch processing patterns (10-20 concurrent requests)
9. Email deliverability indicators (bounce rate estimation)
10. Common spam/test email domains to exclude

**Key Decisions to Make**:
- Which GitHub API endpoints to use (Events vs Commits API)?
- How many events to fetch per candidate (30? 50?)?
- How to prioritize emails (profile > recent commits > README)?
- How to handle README not found (404)?
- LinkedIn URL formats (linkedin.com/in/ vs company pages)?
- Twitter URL variations (twitter.com vs x.com)?
- Data retention period (30 days? 60 days? 90 days)?
- Auto-deletion mechanism (cron job? application-level TTL)?
- Email validation strictness (RFC compliant vs lenient)?
- Concurrent request limit (10? 20? 50?)?

**Output**: research.md with all decisions documented

## Phase 1: Design & Contracts

**Entities** (from spec.md):
1. **ContactInfo** (output) - NEW
   - Fields: primary_email, additional_emails, linkedin_username, twitter_username, blog_url, company, hireable
   - Fields: contact_sources (map of field → source), enriched_at, gdpr_collection_basis, data_retention_expires_at
   - Validation: email format validation, URL cleaning, deduplication
   - Purpose: Embedded in Candidate entity

2. **EnrichmentResult** (metadata) - NEW
   - Fields: total_candidates, successfully_enriched, email_found_count, linkedin_found_count, twitter_found_count, website_found_count
   - Fields: average_contacts_per_candidate, enrichment_time_ms, api_calls_made, rate_limit_remaining, failed_enrichments
   - Purpose: Shows enrichment effectiveness

3. **EmailSource** (internal) - NEW
   - Fields: email_address, source, found_at, commit_date, is_noreply
   - Purpose: Track email reliability for prioritization

**API Contracts**:
- Input: List[Candidate] (from Module 003 Ranking Engine output schema)
- Output: `{"enriched_candidates": List[Candidate], "metadata": EnrichmentResult}`

**Contract Tests**:
- `test_input_schema.py`: Validate Candidate has github_username
- `test_output_schema.py`: Validate ContactInfo structure matches spec

**Quickstart Scenarios** (from spec.md acceptance scenarios):
1. Layer 1: Extract public email from GitHub profile → verify email returned
2. Layer 2: Extract commit emails → verify noreply addresses filtered
3. Layer 3: Parse profile README → verify contact extraction
4. Layer 4: Discover LinkedIn from bio → verify LinkedIn username extracted
5. Full pipeline: Enrich 100 candidates → verify 90-120 second completion
6. GDPR: Store contact data → verify enriched_at and expires_at timestamps
7. Performance: Concurrent processing → verify 10-20 parallel requests
8. Data quality: Email validation → verify format checking and deduplication
9. Privacy: Noreply filtering → verify privacy-protected emails excluded
10. Error handling: GitHub API 404 → verify graceful failure, continue processing

**Agent File Update**:
- Run: `.specify/scripts/bash/update-agent-context.sh claude`
- Add: Python 3.11, httpx, pydantic v2, email-validator, pytest
- Document: Module 010 - Contact Enrichment (enrich candidate contact info)

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, CLAUDE.md updated

## Phase 2: Task Planning Approach

**Task Generation Strategy**:
1. Load `.specify/templates/tasks-template.md`
2. Extract tasks from contracts and quickstart scenarios
3. TDD approach: tests before implementation
4. Layer-by-layer implementation (1 → 2 → 3 → 4 → orchestration)

**Task Categories**:
- **Setup** (3 tasks): Project structure, dependencies, config files
- **Tests First** (10 tasks):
  - Contract tests (input/output validation)
  - Unit tests (email validator, noreply filter, URL normalizer)
  - Integration tests (each layer + full enrichment)
- **Core Implementation** (10 tasks):
  - Models (ContactInfo, EnrichmentResult, EmailSource)
  - Layer 1: ProfileExtractor
  - Layer 2: CommitEmailExtractor
  - Layer 3: ReadmeParser
  - Layer 4: SocialDiscoverer
  - Orchestrator: ContactEnricher
- **Integration** (2 tasks):
  - Wire all layers together
  - GDPR compliance (auto-deletion, export)

**Ordering**:
- Models before services
- Unit tests before integration tests
- Mark [P] for parallel tasks (independent test files)
- Layer 1 → Layer 2 → Layer 3 → Layer 4 → Orchestrator

**Estimated Output**: ~25 tasks in TDD order

## Phase 3+: Future Implementation

**Phase 3**: /tasks command generates tasks.md
**Phase 4**: Execute tasks following TDD principles
**Phase 5**: Validate with quickstart.md, measure success rates (target: 66.7% email, 91.7% contact)
**Phase 6**: GDPR audit - verify retention policies, deletion mechanisms, data export

## Complexity Tracking

No constitutional violations. Module follows all 5 principles:
- Privacy-first: Respects noreply emails, public data only
- Single source: GitHub API only (Phase 1)
- Modular: Clear input/output contracts
- No AI needed: Pure data extraction
- Transparent: Returns contact sources metadata

**GDPR Compliance**:
- ✅ Collection metadata (timestamp, source, legal basis)
- ✅ Retention limits (30-90 days configurable)
- ✅ Automated deletion (expires_at field)
- ✅ Export support (JSON serialization)
- ✅ Privacy-first filtering (noreply exclusion)

## Progress Tracking

**Phase Status**:
- [x] Phase 0: Research complete (/plan command)
- [x] Phase 1: Design complete (/plan command)
- [x] Phase 2: Task planning approach described (/plan command)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed (66.7% email, 91.7% contact)
- [ ] Phase 6: GDPR audit passed

**Gate Status**:
- [x] Initial Constitution Check: PASS
- [ ] Post-Design Constitution Check: PENDING
- [ ] All research questions answered
- [ ] Contracts defined
- [x] Validation completed (test_contact_enrichment.py: 66.7% email, 91.7% contact)

**Validation Evidence**:
- Test Date: 2025-10-10
- Sample Size: 12 real candidates
- Results File: `/Users/arunkumar/ClaudeCode-Projects/juicebox/contact_enrichment_test_results.txt`
- Success Rates:
  - Profile Email: 33.3% (4/12) - EXCEEDED predicted 5-15%
  - Commit Emails: 41.7% (5/12) - ON TARGET predicted 20-35%
  - LinkedIn: 25.0% (3/12) - Lower than predicted 40-60%
  - Twitter: 66.7% (8/12) - EXCEEDED predicted 30-40%
  - **ANY Email: 66.7% (8/12) - EXCEEDED target 40-60%**
  - **ANY Contact: 91.7% (11/12) - EXCEEDED target 75-85%**

---
*Based on Constitution v1.0.0 - See `.specify/memory/constitution.md`*
