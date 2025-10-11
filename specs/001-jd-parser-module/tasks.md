# Tasks: JD Parser Module

**Input**: Design documents from `/specs/001-jd-parser-module/`
**Prerequisites**: plan.md, research.md, data-model.md, contracts/, quickstart.md

## Execution Flow (main)
```
1. Load plan.md from feature directory ✓
2. Load design documents ✓
   → data-model.md: 4 entities extracted
   → contracts/: 2 schema files found
   → quickstart.md: 6 test scenarios identified
   → research.md: Technology decisions captured
3. Generate tasks by category ✓
   → Setup: 3 tasks
   → Tests: 9 tasks (contract + integration)
   → Core: 8 tasks (models, validators, LLM client, parser)
   → Polish: 4 tasks
4. Apply task rules ✓
   → Different files = [P] parallel execution
   → Same file = sequential
   → Tests before implementation (TDD)
5. Number tasks sequentially (T001-T024)
6. Generate dependency graph ✓
7. Create parallel execution examples ✓
8. Validate task completeness ✓
9. Return: SUCCESS (24 tasks ready for execution)
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
- **Source**: `src/jd_parser/` for all Python modules
- **Tests**: `tests/contract/`, `tests/integration/`, `tests/unit/`
- **Config**: `src/config/` for skill mappings

---

## Phase 3.1: Setup

- [ ] **T001** Create Python project structure with src/jd_parser/, tests/, and src/config/ directories
- [ ] **T002** Initialize Python project with pyproject.toml including dependencies: openai>=1.0.0, anthropic>=0.18.0, pydantic>=2.0.0, pytest>=7.4.0, pytest-mock>=3.11.0
- [ ] **T003** [P] Create src/config/skill_mappings.json with initial skill normalization mappings (JavaScript, React, Python, .NET Core, etc. per data-model.md)

---

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

- [ ] **T004** [P] Contract test for input schema in tests/contract/test_input_contract.py - validate against specs/001-jd-parser-module/contracts/input-schema.json
- [ ] **T005** [P] Contract test for output schema in tests/contract/test_output_contract.py - validate against specs/001-jd-parser-module/contracts/output-schema.json
- [ ] **T006** [P] Integration test for Scenario 1 (full JD parsing) in tests/integration/test_full_jd_parsing.py - "senior python developer with 5+ years in fintech"
- [ ] **T007** [P] Integration test for Scenario 2 (minimal input) in tests/integration/test_minimal_input.py - "react developer"
- [ ] **T008** [P] Integration test for Scenario 3 (validation error) in tests/integration/test_validation_errors.py - missing role/skills
- [ ] **T009** [P] Integration test for Scenario 4 (ambiguous input) in tests/integration/test_ambiguous_input.py - low confidence scores
- [ ] **T010** [P] Integration test for Scenario 5 (formal JD) in tests/integration/test_formal_jd.py - multi-paragraph with sections
- [ ] **T011** [P] Integration test for Scenario 6 (iterative refinement) in tests/integration/test_iterative_refinement.py - re-parse on edit
- [ ] **T012** [P] Integration test for edge cases in tests/integration/test_edge_cases.py - contradictions, typos, non-English, long input

---

## Phase 3.3: Core Implementation (ONLY after tests are failing)

- [ ] **T013** [P] Create Pydantic models in src/jd_parser/models.py: FreeTextInput, YearsOfExperience, TextSpan, ConfidenceScore, JobRequirement (per data-model.md)
- [ ] **T014** [P] Create input/output validators in src/jd_parser/validators.py: validate_input(), validate_output(), validate_minimum_fields()
- [ ] **T015** [P] Create skill normalizer in src/jd_parser/skill_normalizer.py: SkillNormalizer class with static lookup + LLM fallback
- [ ] **T016** Create LLM client abstraction in src/jd_parser/llm_client.py: LLMClient abstract class, OpenAIClient, AnthropicClient implementations
- [ ] **T017** Create extraction prompt template in src/jd_parser/prompts/extraction_prompt.txt with few-shot examples and JSON schema instructions
- [ ] **T018** Implement main JDParser class in src/jd_parser/parser.py: parse() method using LLM client, skill normalizer, and validators
- [ ] **T019** Add confidence scoring logic to src/jd_parser/parser.py: calculate scores per field, generate reasoning, identify highlighted spans
- [ ] **T020** Add error handling to src/jd_parser/parser.py: handle LLM failures, validation errors, minimum field requirements (FR-011)

---

## Phase 3.4: Integration & CLI

- [ ] **T021** Create CLI entry point in src/jd_parser/cli.py: accept JD text as argument, output JSON to stdout
- [ ] **T022** Add logging configuration in src/jd_parser/parser.py: log LLM prompts, responses, and confidence scores for debugging

---

## Phase 3.5: Polish

- [ ] **T023** [P] Create unit tests in tests/unit/: test_skill_normalizer.py, test_validators.py, test_models.py
- [ ] **T024** [P] Performance validation: Verify <2s for typical JD (500-2000 chars), <5s for large JD (10,000+ chars) - add timing tests in tests/integration/test_performance.py

---

## Dependencies

**Setup → Tests**:
- T001, T002, T003 must complete before T004-T012

**Tests → Implementation**:
- T004-T012 (all contract/integration tests) must complete before T013-T020
- Tests must FAIL initially (no implementation)

**Core Implementation Dependencies**:
- T013 (models) blocks T014 (validators), T018 (parser)
- T014 (validators) blocks T018 (parser)
- T015 (skill normalizer) blocks T018 (parser)
- T016 (LLM client) blocks T018 (parser)
- T017 (prompt template) blocks T018 (parser)
- T018 (parser) blocks T019 (confidence scoring), T020 (error handling), T021 (CLI)

**Polish Dependencies**:
- T023, T024 can start after T020 completes

---

## Parallel Execution Examples

### Phase 3.1 Setup (After T001, T002)
```bash
# T003 can run independently
Task: "Create src/config/skill_mappings.json with skill normalization mappings"
```

### Phase 3.2 Tests (After T003)
```bash
# Launch T004-T012 together - all independent test files
Task: "Contract test for input schema in tests/contract/test_input_contract.py"
Task: "Contract test for output schema in tests/contract/test_output_contract.py"
Task: "Integration test Scenario 1 in tests/integration/test_full_jd_parsing.py"
Task: "Integration test Scenario 2 in tests/integration/test_minimal_input.py"
Task: "Integration test Scenario 3 in tests/integration/test_validation_errors.py"
Task: "Integration test Scenario 4 in tests/integration/test_ambiguous_input.py"
Task: "Integration test Scenario 5 in tests/integration/test_formal_jd.py"
Task: "Integration test Scenario 6 in tests/integration/test_iterative_refinement.py"
Task: "Integration test edge cases in tests/integration/test_edge_cases.py"
```

### Phase 3.3 Core (After T012, before dependencies)
```bash
# Launch T013, T014, T015 together - independent files
Task: "Create Pydantic models in src/jd_parser/models.py"
Task: "Create validators in src/jd_parser/validators.py"
Task: "Create skill normalizer in src/jd_parser/skill_normalizer.py"

# Then T016, T017 together
Task: "Create LLM client abstraction in src/jd_parser/llm_client.py"
Task: "Create extraction prompt in src/jd_parser/prompts/extraction_prompt.txt"

# Then T018 (waits for all above)
Task: "Implement JDParser class in src/jd_parser/parser.py"
```

### Phase 3.5 Polish (After T020)
```bash
# Launch T023, T024 together
Task: "Create unit tests in tests/unit/"
Task: "Performance validation tests in tests/integration/test_performance.py"
```

---

## Notes

- **[P] tasks** = different files, no dependencies
- **TDD Requirement**: Verify tests fail (red) before implementing (green)
- **Commit Strategy**: Commit after each task completion
- **LLM Mocking**: Use pytest-mock to mock LLM responses in tests for deterministic results
- **Schema Validation**: Use jsonschema library to validate against contracts/

---

## Task Generation Rules Applied

1. **From Contracts**:
   - input-schema.json → T004 (contract test) [P]
   - output-schema.json → T005 (contract test) [P]

2. **From Data Model**:
   - FreeTextInput, YearsOfExperience, TextSpan, ConfidenceScore, JobRequirement → T013 (models) [P]
   - SkillNormalizationMapping → T015 (skill normalizer) [P]

3. **From Quickstart Scenarios**:
   - Scenario 1 (full JD) → T006 [P]
   - Scenario 2 (minimal) → T007 [P]
   - Scenario 3 (validation error) → T008 [P]
   - Scenario 4 (ambiguous) → T009 [P]
   - Scenario 5 (formal JD) → T010 [P]
   - Scenario 6 (iterative) → T011 [P]
   - Edge cases → T012 [P]

4. **From Research Decisions**:
   - LLM abstraction → T016
   - Prompting technique → T017
   - Skill normalization strategy → T015
   - Testing with mocks → Applied to all tests

---

## Validation Checklist

- [x] All contracts have corresponding tests (T004, T005)
- [x] All entities have model tasks (T013 covers all from data-model.md)
- [x] All quickstart scenarios have integration tests (T006-T012)
- [x] All tests come before implementation (Phase 3.2 before 3.3)
- [x] Parallel tasks are truly independent (verified file paths)
- [x] Each task specifies exact file path
- [x] No task modifies same file as another [P] task
- [x] Dependencies clearly documented

**Total Tasks**: 24
**Estimated Effort**: 3-5 days for full implementation
**Ready for Execution**: ✅
