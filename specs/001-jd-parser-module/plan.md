# Implementation Plan: JD Parser Module

**Branch**: `001-jd-parser-module` | **Date**: 2025-10-05 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-jd-parser-module/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path ✓
2. Fill Technical Context ✓
   → Project Type: single (backend module)
   → Structure Decision: src/ for parser module
3. Fill Constitution Check section ✓
4. Evaluate Constitution Check section ✓
   → Initial check: PASS (all principles aligned)
5. Execute Phase 0 → research.md ✓
6. Execute Phase 1 → contracts, data-model.md, quickstart.md, CLAUDE.md ✓
7. Re-evaluate Constitution Check ✓
   → Post-Design check: PASS (no violations)
8. Plan Phase 2 → Task generation approach documented ✓
9. STOP - Ready for /tasks command ✓
```

## Summary

**Primary Requirement**: Create an AI-powered JD Parser that accepts free-text natural language job descriptions and extracts structured candidate requirements for GitHub sourcing.

**Technical Approach**:
- Use LLM API (OpenAI/Anthropic) for intelligent extraction with structured prompts
- JSON schema-based output with confidence scoring per field
- Modular design: Parser class with clear input/output contracts
- Skill normalization via configurable dictionary mapping
- Comprehensive validation (minimum: role + skill required)

**Key Clarifications Resolved**:
- Language: English only
- Input length: Unlimited
- Extraction scope: Candidate requirements only (no company/benefits)
- Output format: JSON with defined schema
- Minimum viable input: Both skill AND role required

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: LLM SDK (openai or anthropic), Pydantic (data validation), pytest
**Storage**: In-memory for POC (no database persistence)
**Testing**: pytest (unit + integration), mock LLM responses for deterministic tests
**Target Platform**: Python module (CLI + programmatic API)
**Project Type**: single (standalone parser module)
**Performance Goals**: <2s parsing time for typical JD (500-2000 chars), <5s for large JDs (10000+ chars)
**Constraints**: LLM API rate limits (varies by provider), token limits (handle up to 20k+ char inputs)
**Scale/Scope**: POC module, 11 functional requirements, 4 key entities

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. AI-First Development
- [x] LLM used for JD parsing (no regex/keyword matching)
- [x] LLM components are modular and provider-agnostic (abstraction layer)
- [x] AI interactions logged for debugging (prompt + response logging)
- [ ] N/A: Outreach generation not in this module

### II. Privacy-First Architecture
- [x] No data scraping (parser operates on user-provided text)
- [x] No personal data collection (JD text only, no PII)
- [ ] N/A: Opt-out mechanism (handled by downstream modules)
- [ ] N/A: GDPR compliance (no data storage in parser module)

### III. Single Source of Truth
- [x] No external integrations in parser (self-contained)
- [ ] N/A: GitHub API (used by downstream Sourcer module)
- [ ] N/A: Rate limits (handled by Sourcer module)
- [ ] N/A: Caching (no external calls in parser)

### IV. Transparency & Explainability
- [x] Extraction logic is explainable (confidence scores per field)
- [x] AI-generated content shows reasoning (confidence + highlighted spans)
- [x] No black-box decisions (JSON output shows all extracted fields with scores)

### V. Modular Architecture
- [x] JD Parser is standalone with clear interface (accepts text → returns JSON)
- [x] Parser is independently testable (mock LLM responses)
- [ ] N/A: GitHub Sourcer (separate module)
- [ ] N/A: Ranking Engine (separate module)
- [ ] N/A: Outreach Generator (separate module)

**Initial Constitution Check**: ✅ PASS

## Project Structure

### Documentation (this feature)
```
specs/001-jd-parser-module/
├── plan.md              # This file (/plan command output)
├── spec.md              # Feature specification
├── research.md          # Phase 0 output (technology decisions)
├── data-model.md        # Phase 1 output (entity definitions)
├── quickstart.md        # Phase 1 output (manual test scenarios)
└── contracts/           # Phase 1 output (JSON schemas)
    ├── input-schema.json
    └── output-schema.json
```

### Source Code (repository root)
```
src/
├── jd_parser/
│   ├── __init__.py
│   ├── parser.py           # Main JDParser class
│   ├── llm_client.py       # LLM API abstraction layer
│   ├── models.py           # Pydantic models (JobRequirement, etc.)
│   ├── validators.py       # Input/output validation
│   ├── skill_normalizer.py # Skill canonicalization
│   └── prompts/
│       └── extraction_prompt.txt
├── cli.py                  # CLI entry point (optional)
└── config/
    └── skill_mappings.json # Canonical skill dictionary

tests/
├── contract/
│   ├── test_input_contract.py
│   └── test_output_contract.py
├── integration/
│   ├── test_end_to_end_parsing.py
│   ├── test_edge_cases.py
│   └── test_llm_integration.py
└── unit/
    ├── test_skill_normalizer.py
    ├── test_validators.py
    └── test_models.py
```

**Structure Decision**: Single project structure chosen. This is a standalone Python module (JD Parser) that will be imported by other modules later. No frontend/backend split needed. Clear separation between parser logic, LLM client, and data models.

## Phase 0: Outline & Research

**Research Questions**:
1. Which LLM provider to use? (OpenAI GPT-4, Anthropic Claude, or both?)
2. What prompting technique for structured extraction? (Few-shot, function calling, JSON mode?)
3. How to handle skill normalization? (Static dictionary vs dynamic LLM-based?)
4. How to ensure deterministic testing with LLM APIs? (Mocking strategy?)
5. What Pydantic version for data validation? (v1 vs v2?)

**Research Findings** (documented in `research.md`):

### 1. LLM Provider Choice
**Decision**: Support both OpenAI and Anthropic with abstraction layer
**Rationale**:
- Constitution requires "modular and replaceable" AI components
- Different providers have different strengths (GPT-4: function calling, Claude: long context)
- Abstraction layer enables A/B testing and fallback logic
**Alternatives**: Single provider (simpler but less flexible), Open-source models (cost-effective but lower quality)

### 2. Prompting Technique
**Decision**: Use structured output/JSON mode with few-shot examples
**Rationale**:
- OpenAI JSON mode ensures valid JSON output
- Anthropic supports structured outputs via prompt engineering
- Few-shot examples improve extraction accuracy (especially for edge cases)
- Confidence scoring requires explicit instruction in prompt
**Alternatives**: Function calling (OpenAI-specific, less portable), Pure prompt engineering (less reliable formatting)

### 3. Skill Normalization
**Decision**: Static dictionary with LLM fallback for unknowns
**Rationale**:
- Static mappings are fast and deterministic (e.g., "JS" → "JavaScript")
- LLM fallback handles new/obscure skills (e.g., "htmx", "bun")
- Constitution requires explainability (static rules easier to audit)
**Alternatives**: Pure LLM (slower, less predictable), Manual-only (incomplete coverage)

### 4. Testing with LLM APIs
**Decision**: Mock LLM responses using pytest fixtures + contract tests
**Rationale**:
- Unit tests use mock responses (deterministic, fast, no API costs)
- Integration tests use real API with cached responses (verify actual behavior)
- Contract tests ensure schema compliance (catch breaking changes)
**Alternatives**: VCR.py (records real responses, but still costs money initially), No mocking (expensive, slow)

### 5. Pydantic Version
**Decision**: Pydantic v2 (latest stable)
**Rationale**:
- Better performance (5-50x faster than v1)
- Native JSON schema generation (matches FR-010 requirement)
- Improved validation error messages (better UX for debugging)
**Alternatives**: Pydantic v1 (more established, but slower)

**Output**: research.md created ✓

## Phase 1: Design & Contracts

### Data Model (`data-model.md`)

#### 1. JobRequirement (Output Entity)
```
Represents the structured output of the JD Parser.

Fields:
- role: str | null (Job title, e.g., "Senior Backend Engineer")
- required_skills: list[str] (Must-have technical skills, normalized)
- preferred_skills: list[str] (Nice-to-have skills, normalized)
- years_of_experience: dict (min: int | null, max: int | null, range_text: str | null)
- seniority_level: str | null (enum: "Junior", "Mid-level", "Senior", "Staff", "Principal", null)
- location_preferences: list[str] (Cities, countries, or "remote")
- domain: str | null (Industry/domain context, e.g., "fintech", "healthcare")
- confidence_scores: dict[str, ConfidenceScore] (Per-field confidence metadata)
- original_input: str (Raw JD text for reference)
- schema_version: str (e.g., "1.0.0" for backward compatibility)

Validation Rules:
- At least one required_skill must be present (FR-011)
- role must be non-empty string or null (FR-011)
- If role is null AND required_skills is empty → validation error
- seniority_level must be from allowed enum or null
- years_of_experience.min <= years_of_experience.max (if both present)
- confidence_scores keys must match extracted field names
```

#### 2. ConfidenceScore (Nested Entity)
```
Represents confidence metadata for each extracted field.

Fields:
- field_name: str (e.g., "role", "required_skills")
- score: int (0-100, higher = more confident)
- reasoning: str (Why this score? e.g., "Explicitly stated in JD")
- highlighted_spans: list[dict] (Text spans that contributed to extraction)
  - Each span: {"start": int, "end": int, "text": str}

Validation Rules:
- score must be between 0-100 inclusive
- reasoning must be non-empty
- highlighted_spans can be empty (if no specific text matched)
```

#### 3. FreeTextInput (Input Entity)
```
Represents the raw user input.

Fields:
- text: str (The JD text, unlimited length)
- language: str (Default: "en" for English)
- submitted_at: datetime (Timestamp, auto-generated)

Validation Rules:
- text must be non-empty (min 1 character)
- language must be "en" (enforced for POC)
- text length unlimited (FR-001 clarification)
```

#### 4. SkillNormalizationMapping (Configuration Entity)
```
Represents canonical skill mappings for normalization.

Fields:
- canonical_name: str (e.g., "JavaScript")
- aliases: list[str] (e.g., ["JS", "javascript", "ECMAScript", "js"])
- category: str | null (e.g., "language", "framework", "tool")

Loaded from: src/config/skill_mappings.json
```

### API Contracts (`contracts/`)

#### Input Contract (`contracts/input-schema.json`)
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "text": {
      "type": "string",
      "minLength": 1,
      "description": "Free-text job description in English"
    },
    "language": {
      "type": "string",
      "enum": ["en"],
      "default": "en",
      "description": "Input language (English only for POC)"
    }
  },
  "required": ["text"],
  "additionalProperties": false
}
```

#### Output Contract (`contracts/output-schema.json`)
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "role": {
      "type": ["string", "null"],
      "description": "Extracted job role/title"
    },
    "required_skills": {
      "type": "array",
      "items": {"type": "string"},
      "minItems": 0,
      "description": "Must-have technical skills (normalized)"
    },
    "preferred_skills": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Nice-to-have skills (normalized)"
    },
    "years_of_experience": {
      "type": "object",
      "properties": {
        "min": {"type": ["integer", "null"], "minimum": 0},
        "max": {"type": ["integer", "null"], "minimum": 0},
        "range_text": {"type": ["string", "null"]}
      }
    },
    "seniority_level": {
      "type": ["string", "null"],
      "enum": ["Junior", "Mid-level", "Senior", "Staff", "Principal", null]
    },
    "location_preferences": {
      "type": "array",
      "items": {"type": "string"}
    },
    "domain": {
      "type": ["string", "null"],
      "description": "Industry/domain context"
    },
    "confidence_scores": {
      "type": "object",
      "additionalProperties": {
        "type": "object",
        "properties": {
          "score": {"type": "integer", "minimum": 0, "maximum": 100},
          "reasoning": {"type": "string", "minLength": 1},
          "highlighted_spans": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "start": {"type": "integer", "minimum": 0},
                "end": {"type": "integer", "minimum": 0},
                "text": {"type": "string"}
              },
              "required": ["start", "end", "text"]
            }
          }
        },
        "required": ["score", "reasoning"]
      }
    },
    "original_input": {
      "type": "string",
      "description": "Raw JD text for reference"
    },
    "schema_version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+\\.\\d+$",
      "description": "Output schema version (semver)"
    }
  },
  "required": [
    "role",
    "required_skills",
    "preferred_skills",
    "years_of_experience",
    "seniority_level",
    "location_preferences",
    "domain",
    "confidence_scores",
    "original_input",
    "schema_version"
  ],
  "additionalProperties": false
}
```

### Contract Tests (failing, as expected)

**Test files created**:
- `tests/contract/test_input_contract.py` - Validates input schema compliance
- `tests/contract/test_output_contract.py` - Validates output schema compliance

Both tests currently FAIL (no implementation yet) ✓

### Quickstart Test Scenarios (`quickstart.md`)

Created with 6 manual test scenarios from spec acceptance criteria:
1. Full JD parsing (senior python developer example)
2. Minimal input (react developer)
3. Missing required fields (validation error)
4. Ambiguous input (low confidence scores)
5. Formal multi-paragraph JD
6. Iterative refinement (re-parse on edit)

### Agent Context Update

Running agent context update script:

```bash
.specify/scripts/bash/update-agent-context.sh claude
```

**Output**: CLAUDE.md updated with JD Parser context ✓

**Post-Design Constitution Check**: ✅ PASS (no violations introduced)

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- Load `.specify/templates/tasks-template.md` as base
- Generate tasks from Phase 1 design docs:
  - Each contract → contract test task [P]
  - Each entity in data-model.md → Pydantic model task [P]
  - Each integration scenario → integration test task
  - Implementation tasks to make tests pass

**Ordering Strategy**:
- Setup tasks first (project init, dependencies)
- TDD order: Contract tests → Integration tests → Implementation
- Dependency order: Models → Validators → LLM Client → Parser → CLI
- Mark [P] for parallel execution (independent files)

**Task Breakdown**:
1. Setup (2-3 tasks): Project structure, dependencies, config files
2. Contract tests (2 tasks [P]): Input schema test, Output schema test
3. Pydantic models (2-3 tasks [P]): JobRequirement, ConfidenceScore, FreeTextInput models
4. Unit tests & implementation (8-10 tasks): Skill normalizer, validators, LLM client, parser
5. Integration tests (3-4 tasks): End-to-end parsing, edge cases, LLM integration
6. Polish (2-3 tasks): CLI, documentation, performance validation

**Estimated Output**: 20-25 numbered, ordered tasks in tasks.md

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)
**Phase 4**: Implementation (execute tasks.md following TDD principles)
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

No violations - Constitution Check passed ✓

## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command)
- [x] Phase 1: Design complete (/plan command)
- [x] Phase 2: Task planning complete (/plan command - describe approach only)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS
- [x] Post-Design Constitution Check: PASS
- [x] All NEEDS CLARIFICATION resolved (5 clarifications completed)
- [x] Complexity deviations documented (none - no violations)

---
*Based on Constitution v1.0.0 - See `.specify/memory/constitution.md`*
