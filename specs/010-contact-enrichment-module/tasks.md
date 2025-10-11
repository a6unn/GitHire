# Tasks: Contact Enrichment Module

**Input**: Design documents from `/specs/010-contact-enrichment-module/`
**Prerequisites**: ✅ plan.md, ✅ spec.md, ✅ validation (66.7% email, 91.7% contact)

---

## Overview

**Module**: 010-contact-enrichment-module (NEW)
**Total Tasks**: 25
**Estimated Duration**: 12-16 hours
**Approach**: TDD (Tests First, Implementation Second)

**Technology Stack**:
- Python 3.11+
- httpx (async HTTP client)
- pydantic v2 (validation)
- email-validator (email format validation)
- pytest + pytest-asyncio (testing)
- pyyaml (config management)

**Core Features**:
- Layer 1: GitHub profile fields extraction (33.3% email success)
- Layer 2: Commit email extraction with noreply filtering (41.7% success)
- Layer 3: Profile README parsing (50% README coverage)
- Layer 4: Social profile discovery (66.7% Twitter, 25% LinkedIn)
- GDPR compliance (auto-deletion, transparent sources)

**Validated Success Rates** (Real Data):
- Email discovery: 66.7% (8/12 candidates)
- Overall contact: 91.7% (11/12 candidates)

---

## Phase 3.1: Setup (3 tasks)

- [ ] **T001** Create project structure for Contact Enrichment module
  - Create: `src/contact_enrichment/` directory
  - Create subdirectories: `models/`, `services/`, `lib/`, `config/`
  - Create: `tests/contact_enrichment/contract/`, `tests/contact_enrichment/integration/`, `tests/contact_enrichment/unit/`
  - Verify: Directory structure matches plan.md

- [ ] **T002** Add Module 010 dependencies to pyproject.toml
  - Add: `httpx >= 0.24.0` (async HTTP client)
  - Add: `email-validator >= 2.0.0` (email format validation)
  - Add: `pyyaml >= 6.0` (config file parsing)
  - Verify: `pip install -e .` succeeds
  - Run: `pytest --collect-only` to verify async support

- [ ] **T003** [P] Create configuration files for contact enrichment
  - Create: `src/contact_enrichment/config/noreply_patterns.yaml` with GitHub noreply patterns
  - Create: `src/contact_enrichment/config/spam_domains.yaml` with test/spam domains to exclude
  - Add patterns: `noreply.github.com`, `users.noreply.github.com`, `no-reply`, `noreply@`
  - Add spam domains: `example.com`, `test.com`, `localhost.localdomain`
  - Verify: All config files parse correctly (YAML validation)

---

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3

**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

### Contract Tests (2 tasks)

- [ ] **T004** [P] Contract test for input schema in tests/contact_enrichment/contract/test_input_schema.py
  - Load: Candidate schema from Module 002/003
  - Test: Valid Candidate with github_username passes validation
  - Test: Missing github_username fails validation
  - Test: List[Candidate] structure is valid
  - Expected: All tests FAIL (ContactEnricher not imported yet)

- [ ] **T005** [P] Contract test for output schema in tests/contact_enrichment/contract/test_output_schema.py
  - Test: Valid ContactInfo object passes schema validation
  - Test: Valid EnrichmentResult metadata passes schema validation
  - Test: ContactInfo has required fields (primary_email can be null, contact_sources required)
  - Test: enriched_at and data_retention_expires_at are valid timestamps
  - Expected: All tests FAIL (ContactInfo model doesn't exist)

### Unit Tests (5 tasks)

- [ ] **T006** [P] Unit test for email validation in tests/contact_enrichment/unit/test_email_validator.py
  - Test: Valid email "test@gmail.com" passes validation
  - Test: Invalid email "notanemail" fails validation
  - Test: Email without @ symbol fails validation
  - Test: Email without domain fails validation
  - Test: Empty string returns False
  - Expected: All tests FAIL (EmailValidator not implemented)

- [ ] **T007** [P] Unit test for noreply filtering in tests/contact_enrichment/unit/test_noreply_filter.py
  - Test: "user@noreply.github.com" is filtered (returns True for is_noreply)
  - Test: "123+user@users.noreply.github.com" is filtered
  - Test: "no-reply@example.com" is filtered
  - Test: "user@gmail.com" is NOT filtered
  - Test: Load patterns from noreply_patterns.yaml config
  - Expected: All tests FAIL (NoreplyFilter not implemented)

- [ ] **T008** [P] Unit test for URL normalization in tests/contact_enrichment/unit/test_url_normalizer.py
  - Test: "https://linkedin.com/in/username" → extracts "username"
  - Test: "linkedin.com/in/username/" → extracts "username" (trailing slash)
  - Test: "@twitteruser" → extracts "twitteruser" (removes @)
  - Test: "https://twitter.com/username" → extracts "username"
  - Test: "https://x.com/username" → extracts "username" (Twitter rebrand)
  - Expected: All tests FAIL (URLNormalizer not implemented)

- [ ] **T009** [P] Unit test for spam domain filtering in tests/contact_enrichment/unit/test_spam_filter.py
  - Test: "test@example.com" is filtered (spam domain)
  - Test: "user@test.com" is filtered
  - Test: "admin@localhost.localdomain" is filtered
  - Test: "user@gmail.com" is NOT filtered
  - Test: Load spam domains from spam_domains.yaml config
  - Expected: All tests FAIL (SpamFilter not implemented)

- [ ] **T010** [P] Unit test for email deduplication in tests/contact_enrichment/unit/test_email_deduplicator.py
  - Test: ["test@gmail.com", "test@gmail.com"] → ["test@gmail.com"] (deduplicated)
  - Test: ["TEST@GMAIL.COM", "test@gmail.com"] → ["test@gmail.com"] (case-insensitive)
  - Test: Prioritize profile email over commit emails
  - Test: Sort emails by source priority (profile > recent commits > old commits > README)
  - Expected: All tests FAIL (EmailDeduplicator not implemented)

### Integration Tests (5 tasks)

- [ ] **T011** [P] Integration test for Layer 1 (profile extraction) in tests/contact_enrichment/integration/test_profile_extraction.py
  - Mock: GitHub `/users/{username}` API response with email, blog, twitter_username
  - Test: Extract email from profile → returns email in ContactInfo
  - Test: Extract blog/website → returns blog_url in ContactInfo
  - Test: Extract twitter_username → returns twitter_username in ContactInfo
  - Test: Extract company and hireable → returns in ContactInfo
  - Test: Profile with no email → returns null for primary_email
  - Expected: All tests FAIL (ProfileExtractor not implemented)

- [ ] **T012** [P] Integration test for Layer 2 (commit extraction) in tests/contact_enrichment/integration/test_commit_extraction.py
  - Mock: GitHub `/users/{username}/events/public` API response with PushEvent commits
  - Test: Extract emails from commits → returns list of emails
  - Test: Filter noreply addresses → excludes "user@noreply.github.com"
  - Test: Deduplicate emails → returns unique emails only
  - Test: Limit to 5 most recent emails → returns max 5 emails
  - Test: No PushEvents → returns empty list
  - Expected: All tests FAIL (CommitEmailExtractor not implemented)

- [ ] **T013** [P] Integration test for Layer 3 (README parsing) in tests/contact_enrichment/integration/test_readme_parsing.py
  - Mock: GitHub `/repos/{username}/{username}/contents/README.md` API response
  - Test: README with email → extracts email address
  - Test: README with LinkedIn URL → extracts LinkedIn username
  - Test: README with Twitter URL → extracts Twitter handle
  - Test: README with multiple contacts → extracts all contact methods
  - Test: README not found (404) → returns empty results without error
  - Test: Filter spam emails from README → excludes test@example.com
  - Expected: All tests FAIL (ReadmeParser not implemented)

- [ ] **T014** [P] Integration test for Layer 4 (social discovery) in tests/contact_enrichment/integration/test_social_discovery.py
  - Test: LinkedIn URL in bio → extracts LinkedIn username
  - Test: Blog URL is LinkedIn profile → identifies as LinkedIn contact
  - Test: Twitter in bio but not in twitter_username field → extracts from bio
  - Test: Deduplicate social profiles across sources → returns unique profiles
  - Test: Prioritize official fields over extracted → profile twitter_username takes precedence
  - Expected: All tests FAIL (SocialDiscoverer not implemented)

- [ ] **T015** [P] Integration test for full enrichment pipeline in tests/contact_enrichment/integration/test_contact_enricher.py
  - Mock: All GitHub API endpoints (profile, events, README)
  - Test: Enrich single candidate → returns ContactInfo with all layers
  - Test: Enrich 10 candidates concurrently → completes in <10 seconds
  - Test: Candidate with no contact info → returns empty ContactInfo without error
  - Test: GitHub API error (404, 403) → handles gracefully, continues processing
  - Test: EnrichmentResult metadata → includes success rates, timing, API call count
  - Test: GDPR fields → includes enriched_at, data_retention_expires_at, contact_sources
  - Expected: All tests FAIL (ContactEnricher not implemented)

---

## Phase 3.3: Core Implementation (ONLY after tests are failing)

### Models (3 tasks)

- [ ] **T016** [P] Create ContactInfo model in src/contact_enrichment/models/contact_info.py
  - Implement: ContactInfo Pydantic model per data-model.md
  - Fields: primary_email, additional_emails, linkedin_username, twitter_username, blog_url, company, hireable
  - Fields: contact_sources (dict[str, str]), enriched_at, gdpr_collection_basis, data_retention_expires_at
  - Add validators: email format validation, URL cleaning
  - Add: enriched_at defaults to datetime.utcnow()
  - Add: data_retention_expires_at = enriched_at + 30 days (configurable)
  - Add: gdpr_collection_basis = "legitimate_interest_recruiting"
  - Verify: tests/contact_enrichment/contract/test_output_schema.py ContactInfo tests pass

- [ ] **T017** [P] Create EnrichmentResult model in src/contact_enrichment/models/enrichment_result.py
  - Implement: EnrichmentResult Pydantic model per data-model.md
  - Fields: total_candidates, successfully_enriched, email_found_count, linkedin_found_count, twitter_found_count, website_found_count
  - Fields: average_contacts_per_candidate, enrichment_time_ms, api_calls_made, rate_limit_remaining, failed_enrichments
  - Add validators: counts >= 0, average_contacts calculated automatically
  - Verify: tests/contact_enrichment/contract/test_output_schema.py EnrichmentResult tests pass

- [ ] **T018** [P] Create EmailSource model in src/contact_enrichment/models/email_source.py
  - Implement: EmailSource Pydantic model (internal tracking)
  - Fields: email_address, source, found_at, commit_date, is_noreply
  - Add validator: source in ["profile", "commits", "readme"]
  - Purpose: Track email reliability for prioritization
  - Verify: Can be used internally by CommitEmailExtractor

### Libraries (4 tasks)

- [ ] **T019** [P] Create EmailValidator in src/contact_enrichment/lib/email_validator.py
  - Implement: validate_email(email: str) → bool
  - Use: email-validator library for RFC 5322 compliance
  - Logic: Check format (has @, has domain, valid TLD)
  - Verify: tests/contact_enrichment/unit/test_email_validator.py passes

- [ ] **T020** [P] Create NoreplyFilter in src/contact_enrichment/lib/noreply_filter.py
  - Implement: is_noreply(email: str) → bool
  - Load: Patterns from noreply_patterns.yaml config
  - Logic: Check if email contains any noreply pattern
  - Verify: tests/contact_enrichment/unit/test_noreply_filter.py passes

- [ ] **T021** [P] Create URLNormalizer in src/contact_enrichment/lib/url_normalizer.py
  - Implement: extract_linkedin_username(url: str) → Optional[str]
  - Implement: extract_twitter_handle(url: str) → Optional[str]
  - Regex: `linkedin\.com/in/([\w\-]+)` for LinkedIn
  - Regex: `(?:twitter|x)\.com/(\w+)` for Twitter/X
  - Logic: Remove @ symbols, trailing slashes, extract clean username
  - Verify: tests/contact_enrichment/unit/test_url_normalizer.py passes

- [ ] **T022** [P] Create SpamFilter in src/contact_enrichment/lib/spam_filter.py
  - Implement: is_spam_domain(email: str) → bool
  - Load: Spam domains from spam_domains.yaml config
  - Logic: Check if email domain matches spam domain list
  - Verify: tests/contact_enrichment/unit/test_spam_filter.py passes

### Services (5 tasks)

- [ ] **T023** Create ProfileExtractor (Layer 1) in src/contact_enrichment/services/profile_extractor.py
  - Implement: async extract_from_profile(username: str, github_client) → dict
  - Logic: Fetch GitHub profile via `/users/{username}`
  - Extract: email, blog, twitter_username, company, hireable, bio
  - Return: dict with extracted fields
  - Error handling: 404 → return empty dict
  - Verify: tests/contact_enrichment/integration/test_profile_extraction.py passes

- [ ] **T024** Create CommitEmailExtractor (Layer 2) in src/contact_enrichment/services/commit_email_extractor.py
  - Implement: async extract_from_commits(username: str, github_client) → list[EmailSource]
  - Logic: Fetch public events via `/users/{username}/events/public`
  - Logic: Parse PushEvent commits for email addresses
  - Logic: Filter noreply addresses using NoreplyFilter
  - Logic: Filter spam domains using SpamFilter
  - Logic: Validate email format using EmailValidator
  - Logic: Limit to 5 most recent unique emails
  - Return: list of EmailSource objects with commit_date
  - Verify: tests/contact_enrichment/integration/test_commit_extraction.py passes

- [ ] **T025** Create ReadmeParser (Layer 3) in src/contact_enrichment/services/readme_parser.py
  - Implement: async parse_readme(username: str, github_client) → dict
  - Logic: Fetch README from `/repos/{username}/{username}/contents/README.md`
  - Logic: Decode base64 content
  - Extract: emails using regex `\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b`
  - Extract: LinkedIn using regex `linkedin\.com/in/([\w\-]+)`
  - Extract: Twitter using regex `(?:twitter|x)\.com/(\w+)`
  - Logic: Filter spam emails using SpamFilter
  - Logic: Validate emails using EmailValidator
  - Error handling: 404 (no README) → return empty dict
  - Verify: tests/contact_enrichment/integration/test_readme_parsing.py passes

- [ ] **T026** Create SocialDiscoverer (Layer 4) in src/contact_enrichment/services/social_discoverer.py
  - Implement: discover_social_profiles(profile_data: dict, readme_data: dict) → dict
  - Logic: Check twitter_username field first (official)
  - Logic: Search for LinkedIn in bio, blog, README
  - Logic: Search for Twitter in bio (if not in official field)
  - Logic: Deduplicate social profiles across sources
  - Logic: Prioritize official profile fields over extracted
  - Use: URLNormalizer for cleaning URLs
  - Return: dict with linkedin_username, twitter_username
  - Verify: tests/contact_enrichment/integration/test_social_discovery.py passes

- [ ] **T027** Create ContactEnricher (Main Orchestrator) in src/contact_enrichment/services/contact_enricher.py
  - Implement: async enrich_candidate(candidate: Candidate, github_client) → ContactInfo
  - Logic: Call Layer 1 (ProfileExtractor)
  - Logic: Call Layer 2 (CommitEmailExtractor)
  - Logic: Call Layer 3 (ReadmeParser)
  - Logic: Call Layer 4 (SocialDiscoverer)
  - Logic: Prioritize emails: profile > recent commits > README
  - Logic: Deduplicate all contact information
  - Logic: Build contact_sources map (field → source)
  - Logic: Set GDPR fields (enriched_at, expires_at, collection_basis)
  - Error handling: Layer failures → continue with other layers
  - Return: ContactInfo with all discovered contact methods
  - Implement: async enrich_candidates(candidates: list[Candidate]) → tuple[list[ContactInfo], EnrichmentResult]
  - Logic: Process candidates concurrently (10-20 parallel)
  - Logic: Collect enrichment statistics
  - Logic: Track API calls and timing
  - Return: tuple of enriched contacts and metadata
  - Verify: tests/contact_enrichment/integration/test_contact_enricher.py passes

---

## Phase 3.4: Integration (2 tasks)

- [ ] **T028** Wire all components together in src/contact_enrichment/__init__.py
  - Export: ContactInfo, EnrichmentResult, ContactEnricher
  - Create: enrich_contacts(candidates: list[Candidate]) convenience function
  - Initialize: GitHub client (reuse from Module 002)
  - Document: Module API in docstrings
  - Verify: `from src.contact_enrichment import enrich_contacts` works

- [ ] **T029** Add logging and monitoring
  - Configure: logging to stdout with structured format
  - Log: Enrichment progress (candidate X of Y)
  - Log: Layer execution (Layer 1 found email, Layer 2 found 3 commits, etc.)
  - Log: Failures (GitHub API errors, validation failures)
  - Add: Execution time tracking for each layer
  - Verify: Logs appear when running enrichment

---

## Phase 3.5: Validation (NOT IMPLEMENTED YET - DEFERRED)

**Note**: These tasks are deferred until Phase 5 validation.

- [ ] **T030** [P] Run quickstart validation scenarios manually
- [ ] **T031** [P] Measure success rates with real candidates (target: 66.7% email, 91.7% contact)
- [ ] **T032** [P] Performance test: Enrich 100 candidates in <120 seconds
- [ ] **T033** GDPR audit: Verify auto-deletion, data export, retention policies
- [ ] **T034** Update CLAUDE.md with Module 010 completion status

---

## Dependencies

**Sequential (Blocking)**:
- T001 → T002 → T003 (setup must complete first)
- T004-T015 (all tests) → T016-T027 (implementation)
- T016-T018 (models) → T023-T027 (services depend on models)
- T019-T022 (libraries) → T023-T027 (services depend on libraries)
- T023-T026 (layers) → T027 (orchestrator depends on all layers)
- T027 (ContactEnricher) → T028 (integration)
- T028 → T029 (logging)

**Parallel (Can Run Together)**:
- T004, T005 (contract tests - different files)
- T006, T007, T008, T009, T010 (unit tests - different files)
- T011, T012, T013, T014, T015 (integration tests - different files)
- T016, T017, T018 (models - different files)
- T019, T020, T021, T022 (libraries - different files)
- After T022 completes: T023, T024, T025, T026 can run in parallel (different files, independent layers)

---

## Parallel Execution Examples

### Round 1: Contract Tests (After T003)
```bash
# Launch T004, T005 in parallel
pytest tests/contact_enrichment/contract/test_input_schema.py &
pytest tests/contact_enrichment/contract/test_output_schema.py &
wait
```

### Round 2: Unit Tests (After T005)
```bash
# Launch T006-T010 in parallel
pytest tests/contact_enrichment/unit/test_email_validator.py &
pytest tests/contact_enrichment/unit/test_noreply_filter.py &
pytest tests/contact_enrichment/unit/test_url_normalizer.py &
pytest tests/contact_enrichment/unit/test_spam_filter.py &
pytest tests/contact_enrichment/unit/test_email_deduplicator.py &
wait
```

### Round 3: Integration Tests (After T010)
```bash
# Launch T011-T015 in parallel
pytest tests/contact_enrichment/integration/test_profile_extraction.py &
pytest tests/contact_enrichment/integration/test_commit_extraction.py &
pytest tests/contact_enrichment/integration/test_readme_parsing.py &
pytest tests/contact_enrichment/integration/test_social_discovery.py &
pytest tests/contact_enrichment/integration/test_contact_enricher.py &
wait
```

### Round 4: Models (After T015)
```bash
# T016, T017, T018 can be implemented in parallel (different files)
```

### Round 5: Libraries (After T018)
```bash
# T019, T020, T021, T022 can be implemented in parallel (different files)
```

### Round 6: Services/Layers (After T022)
```bash
# T023, T024, T025, T026 can be implemented in parallel (independent layers)
```

---

## Validation Checklist

**GATE: Verify before marking Phase 3 complete**

- [x] All contracts have corresponding tests (T004, T005)
- [x] All entities have model tasks (T016: ContactInfo, T017: EnrichmentResult, T018: EmailSource)
- [x] All libraries have unit tests (T006-T010 before T019-T022)
- [x] All layers have integration tests (T011-T014 before T023-T026)
- [x] Tests written to FAIL before implementation (TDD enforced)
- [x] Each task specifies exact file path
- [x] No task modifies same file as another [P] task
- [x] Parallel tasks are truly independent

---

## Expected Test Results

**After T015 (All Tests Written)**:
- Total tests: ~35
- Passing: 0 (all should FAIL)
- Reason: Models, libraries, and services not implemented yet

**After T027 (All Implementation Complete)**:
- Total tests: ~35
- Passing: 35 (100%)
- Reason: All contract, unit, and integration tests pass

**After T029 (Integration Complete)**:
- Manual validation with quickstart.md scenarios
- All 10 scenarios should pass
- Success rates: 66.7% email, 91.7% contact (validated)

---

## Notes

- **TDD Discipline**: DO NOT implement before tests fail
- **Async First**: Use `async/await` for all GitHub API calls
- **Privacy First**: Filter noreply emails, respect privacy settings
- **GDPR Compliance**: Include retention metadata with all contact data
- **Error Resilience**: Layer failures should not stop enrichment
- **Concurrency**: Target 10-20 concurrent requests for performance
- **Commit Frequency**: After each task completion

**Validation Evidence**:
- Test file: `test_contact_enrichment.py`
- Results file: `contact_enrichment_test_results.txt`
- Sample size: 12 real candidates
- Email success: 66.7% (8/12) - EXCEEDS target 40-60%
- Contact success: 91.7% (11/12) - EXCEEDS target 75-85%

---

## Next Steps After Tasks Complete

1. Run full test suite: `pytest tests/contact_enrichment/ -v`
2. Validate with quickstart scenarios (manual testing)
3. Measure success rates with 100 real candidates
4. GDPR audit: Verify auto-deletion, data export
5. Update plan.md with "Phase 4: Complete" status
6. Commit Module 010 and merge to main
7. Integrate with Module 004 (Outreach Generator)
