# Feature Specification: JD Parser Module

**Feature Branch**: `001-jd-parser-module`
**Created**: 2025-10-05
**Status**: Draft
**Input**: User description: "JD Parser Module with free-text input interface similar to Juicebox PeopleGPT for extracting structured requirements from natural language job descriptions"

## Execution Flow (main)
```
1. Parse user description from Input ✓
2. Extract key concepts from description ✓
   → Identified: recruiters (actors), free-text input (action), structured extraction (data), NLP parsing (constraint)
3. For each unclear aspect ✓
   → Marked with [NEEDS CLARIFICATION] where applicable
4. Fill User Scenarios & Testing section ✓
5. Generate Functional Requirements ✓
6. Identify Key Entities ✓
7. Run Review Checklist
   → WARN: Some clarifications needed (see FR-009, FR-010, FR-011)
8. Return: SUCCESS (spec ready for planning after clarifications)
```

---

## ⚡ Quick Guidelines
- ✅ Focus on WHAT users need and WHY
- ❌ Avoid HOW to implement (no tech stack, APIs, code structure)
- 👥 Written for business stakeholders, not developers

---

## Clarifications

### Session 2025-10-05
- Q: Multi-language support scope - start with English only, or support other languages? → A: English only (simplifies POC, faster delivery)
- Q: Input length limits - max characters for free-text input? → A: 20,000+ characters (unlimited - handle any length)
- Q: Should system extract company info, benefits, or only candidate requirements? → A: Candidate requirements only (skills, experience, role)
- Q: Output format specification - JSON schema, typed object, or other? → A: JSON with defined schema (standard web API format)
- Q: What's the minimum viable input to proceed? → A: Both skill AND role required (stricter validation)

---

## User Scenarios & Testing *(mandatory)*

### Primary User Story
A recruiter needs to find software developers for an open position. Instead of manually filtering GitHub profiles or crafting complex search queries, they want to describe the role in natural, conversational language (similar to how they would describe it to a colleague) and have the system automatically extract the key hiring criteria.

**Example Input (from Juicebox pattern)**:
> "senior fullstack .net engineers with strong technical knowledge with 8-15 years experience from tamilnadu with c#, dotnet core and angular skills"

**Expected Behavior**:
The system parses this free-text input and extracts:
- **Role/Title**: Senior Fullstack .NET Engineer
- **Required Skills**: C#, .NET Core, Angular
- **Experience Level**: 8-15 years
- **Location Preference**: Tamil Nadu
- **Seniority**: Senior
- **Additional Context**: Strong technical knowledge

### Acceptance Scenarios

1. **Given** a recruiter is on the project creation screen, **When** they type "senior python developer with 5+ years in fintech using fastapi and postgresql", **Then** the system extracts: role="Senior Python Developer", skills=["Python", "FastAPI", "PostgreSQL"], experience="5+ years", domain="fintech"

2. **Given** a recruiter enters minimal text "react developer", **When** the parser processes it, **Then** the system extracts: role="React Developer" (inferred from "developer"), skills=["React"], and marks experience, location, and other fields as unspecified

3. **Given** a recruiter provides input with missing required fields "backend experience needed", **When** the parser processes it, **Then** the system returns error indicating both role and specific technical skills are required

4. **Given** a recruiter provides ambiguous input "developer with some backend experience", **When** the parser processes it, **Then** the system flags ambiguous terms ("some backend experience" lacks specificity) but can proceed if role and at least one skill are identifiable

5. **Given** a recruiter submits a formal job description with multiple paragraphs, **When** the parser processes it, **Then** the system extracts all structured fields from the prose (responsibilities, requirements, nice-to-haves)

6. **Given** a recruiter wants to refine their search, **When** they edit the free-text input, **Then** the system re-parses and updates the extracted requirements in real-time

### Edge Cases
- What happens when the input contains contradictory information (e.g., "junior developer with 10 years experience")?
  - System should flag the contradiction and ask for clarification

- What happens when the input contains typos or abbreviations (e.g., "sr dev", "JS/TS", "5 yoe")?
  - System should normalize abbreviations (yoe → years of experience) and handle common typos

- What happens when the input is in a language other than English?
  - System rejects non-English input with error message: "Currently only English job descriptions are supported"

- What happens when the input contains no technical skills, only soft skills (e.g., "team player with good communication")?
  - System should extract soft skills separately but warn that GitHub sourcing requires technical skills

- What happens when the input is extremely long (e.g., 20,000+ characters from a comprehensive JD)?
  - System processes the full input without truncation, extracting all relevant information regardless of length

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST accept free-text natural language input for job descriptions in English without character limits, structured forms, or templates

- **FR-002**: System MUST extract the following structured fields from free-text input:
  - Job role/title (e.g., "Senior Backend Engineer", "Frontend Developer")
  - Required technical skills (programming languages, frameworks, tools)
  - Years of experience (ranges like "5-8 years" or minimums like "3+ years")
  - Seniority level (Junior, Mid-level, Senior, Staff, Principal)
  - Location preferences (cities, states, countries, or "remote")
  - Domain/Industry context (e.g., fintech, healthcare, e-commerce)

- **FR-003**: System MUST distinguish between:
  - **Required skills** (must-have): explicitly stated or strongly implied
  - **Nice-to-have skills** (preferred): indicated by keywords like "bonus", "preferred", "nice to have"

- **FR-004**: System MUST normalize skill variations to canonical forms:
  - "JS", "javascript", "Java Script" → "JavaScript"
  - "react.js", "reactjs", "React" → "React"
  - "dotnet", ".net core", "asp.net" → ".NET Core"

- **FR-005**: System MUST handle ambiguous or incomplete inputs by:
  - Flagging missing critical information (e.g., no technical skills mentioned)
  - Suggesting clarifications for vague terms (e.g., "some experience" → "How many years?")
  - Assigning confidence scores to extracted fields (high/medium/low confidence)

- **FR-006**: System MUST support iterative refinement:
  - Allow users to edit their free-text input
  - Re-parse on every change and update extracted fields
  - Preserve user intent across edits (incremental updates, not full re-parse from scratch)

- **FR-007**: System MUST provide visual feedback showing what was extracted from the input:
  - Highlight portions of the input text that correspond to extracted fields
  - Show structured output alongside free-text input
  - Display confidence levels for each extracted field

- **FR-008**: System MUST handle common JD patterns:
  - Bullet-point lists ("• 5+ years experience", "• Python, Django")
  - Sentence-based descriptions ("We're looking for a senior engineer with...")
  - Abbreviated formats ("Sr. SWE, 5yoe, Python/Go/K8s")

- **FR-009**: System MUST process formal job descriptions (multi-paragraph documents) by:
  - Extracting requirements from "Requirements" or "Qualifications" sections
  - Distinguishing responsibilities from requirements
  - Identifying "nice to have" vs "must have" from context
  - Ignoring company information, benefits, and non-candidate-requirement sections

- **FR-010**: System MUST return structured output as JSON with a defined schema containing:
  - All extracted fields (role, skills, experience, etc.)
  - Confidence score for each field (0-100%)
  - Original input text for reference
  - Schema versioning for backward compatibility

- **FR-011**: System MUST handle parsing failures gracefully:
  - If input contains zero technical skills, return error: "At least one technical skill required"
  - If input contains no identifiable role/title, return error: "Job role or title required"
  - Minimum viable input MUST contain both at least one skill AND one role/title
  - If input is gibberish or non-job-related, reject with clear message

### Key Entities *(include if feature involves data)*

- **JobRequirement**: Represents the structured output of the parser
  - Attributes: role/title, required_skills (list), preferred_skills (list), years_of_experience (range or minimum), seniority_level, location_preferences (list), domain/industry, confidence_score (per field)
  - Relationships: Created from one FreeTextInput, used by GitHubSourcer for candidate search

- **FreeTextInput**: Represents the raw user input
  - Attributes: text (string), character_count, language_detected, submitted_at (timestamp)
  - Relationships: Generates one JobRequirement via parsing

- **SkillNormalization**: Represents canonical skill mappings
  - Attributes: canonical_name (e.g., "JavaScript"), aliases (list, e.g., ["JS", "javascript", "ECMAScript"])
  - Relationships: Used by parser to normalize skills in JobRequirement

- **ExtractionConfidence**: Represents confidence metadata for parsed fields
  - Attributes: field_name, confidence_score (0-100), reasoning (why this score), highlighted_text_spans (which parts of input contributed)
  - Relationships: Attached to JobRequirement for each extracted field

---

## Review & Acceptance Checklist
*GATE: Automated checks run during main() execution*

### Content Quality
- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

### Requirement Completeness
- [x] No [NEEDS CLARIFICATION] markers remain (all 5 clarifications completed)
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable (via confidence scores, extraction accuracy)
- [x] Scope is clearly bounded (free-text input → structured output, no UI/UX implementation)
- [x] Dependencies and assumptions identified (English input, GitHub as target platform)

---

## Execution Status
*Updated by main() during processing*

- [x] User description parsed
- [x] Key concepts extracted
- [x] Ambiguities marked (3 NEEDS CLARIFICATION items)
- [x] User scenarios defined
- [x] Requirements generated
- [x] Entities identified
- [x] Review checklist passed (with warnings)

---

## Notes for Planning Phase

**Key Decisions Needed Before Planning**:
1. Multi-language support scope (start English-only or broader?)
2. Max input length (character limit for free-text)
3. Output format specification (JSON schema definition)
4. Minimum viable input criteria (what's the threshold for "parseable"?)
5. Should we extract company info/benefits or only candidate requirements?

**Assumptions for POC**:
- Input language: English only
- Input length: Up to 5000 characters (typical JD length)
- Output format: Structured object/JSON with defined schema
- Minimum input: At least 1 technical skill OR 1 role title
- Scope: Extract candidate requirements only (not company info)

**Dependencies**:
- None (this is the first module in the pipeline)

**Downstream Consumers**:
- GitHub Sourcer module (will use JobRequirement output to query GitHub API)
- Ranking Engine (may use requirement confidence scores for ranking logic)
