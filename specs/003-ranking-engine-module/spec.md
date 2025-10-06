# Feature Specification: Ranking Engine Module

**Feature Branch**: `003-ranking-engine-module`
**Created**: 2025-10-05
**Status**: Draft
**Input**: User description: "Ranking Engine module that scores and ranks GitHub candidates based on fit to job requirements, calculating skill match percentage, activity level, experience proxy, and domain relevance, returning ranked list with score breakdowns explaining why each candidate matches"

## Execution Flow (main)
```
1. Parse user description from Input ✓
2. Extract key concepts ✓
   → Input: JobRequirement + Candidate list
   → Action: Score and rank candidates
   → Output: Ranked candidates with score breakdown
   → Constraint: Transparent scoring (explainable)
3. Mark unclear aspects ✓
   → See [NEEDS CLARIFICATION] markers below
4. Fill User Scenarios & Testing ✓
5. Generate Functional Requirements ✓
6. Identify Key Entities ✓
7. Run Review Checklist
   → WARN: Some clarifications needed
8. Return: SUCCESS (spec ready for planning)
```

---

## ⚡ Quick Guidelines
- ✅ Focus on WHAT users need and WHY
- ❌ Avoid HOW to implement (no tech stack, APIs, code structure)
- 👥 Written for business stakeholders, not developers

---

## User Scenarios & Testing *(mandatory)*

### Primary User Story

The Ranking Engine receives a list of GitHub candidates (from Module 002) and job requirements (from Module 001) and needs to score each candidate on how well they match the role. It should:
1. **Calculate** a skill match score (how many required skills the candidate has)
2. **Evaluate** activity level (recent contributions, active repos)
3. **Estimate** experience level (account age, repo maturity, stars)
4. **Assess** domain relevance (projects in same industry as job)
5. **Combine** scores into total ranking (0-100)
6. **Explain** each score with breakdown showing why the candidate ranked high/low
7. **Return** candidates sorted by total score (highest first)

The module operates as a pure algorithm with no external dependencies.

### Acceptance Scenarios

1. **Given** a candidate with all required skills present in their repos, **When** the ranking engine scores them, **Then** their skill match score is 100%

2. **Given** a candidate with 3 out of 5 required skills, **When** scoring, **Then** their skill match score is 60%

3. **Given** a candidate with 500+ contributions in the last year, **When** scoring activity, **Then** they receive a high activity score (90-100)

4. **Given** a candidate with a 7-year-old GitHub account and repos with 100+ stars, **When** estimating experience, **Then** they receive a high experience score (80-100)

5. **Given** a candidate with "fintech" projects and a JD in fintech domain, **When** scoring domain relevance, **Then** they receive a high domain score (80-100)

6. **Given** 50 candidates with varying scores, **When** ranking completes, **Then** they are sorted by total score descending (highest first)

7. **Given** a candidate with total score of 75, **When** viewing results, **Then** the score breakdown shows: skill match (80), activity (70), experience (75), domain (75)

8. **Given** two candidates with identical total scores, **When** ranking, **Then** they are [NEEDS CLARIFICATION: tie-breaking rule - alphabetical? most recent activity? random?]

### Edge Cases

- What happens when a candidate has zero required skills?
  - Assign skill match score of 0, but still calculate other scores

- What happens when a candidate has a brand new GitHub account (1 month old)?
  - Experience score will be low (0-20), but other scores can still be high

- What happens when domain is not specified in JobRequirement?
  - Skip domain scoring, distribute its weight to other factors

- What happens when all candidates score below [NEEDS CLARIFICATION: minimum threshold - 50? 60?]?
  - Return all candidates ranked, but flag that none meet minimum quality bar

- What happens when JobRequirement has conflicting data (Junior with 10 years)?
  - Process each criterion independently; don't try to resolve contradictions

---

## Requirements *(mandatory)*

### Functional Requirements

#### Input Processing
- **FR-001**: Module MUST accept JobRequirement JSON (from Module 001) as input
- **FR-002**: Module MUST accept list of Candidate objects (from Module 002) as input
- **FR-003**: Module MUST validate that JobRequirement contains required_skills before scoring

#### Scoring Algorithm
- **FR-004**: Module MUST calculate skill match score (0-100) based on percentage of required skills found in candidate's languages/repos
- **FR-005**: Module MUST calculate activity score (0-100) based on contribution count and recency
- **FR-006**: Module MUST calculate experience score (0-100) based on account age, repo maturity, and stars received
- **FR-007**: Module MUST calculate domain score (0-100) based on similarity between candidate's projects and job domain
- **FR-008**: Module MUST combine individual scores into total score using weighted formula: [NEEDS CLARIFICATION: weights - equal 25% each? or skill=40%, activity=20%, exp=20%, domain=20%?]

#### Ranking
- **FR-009**: Module MUST rank candidates by total score in descending order (highest first)
- **FR-010**: Module MUST handle ties using [NEEDS CLARIFICATION: tie-breaking rule]
- **FR-011**: Module MUST return top N candidates where N is [NEEDS CLARIFICATION: configurable? fixed at 20?]

#### Transparency (Constitutional Principle IV)
- **FR-012**: Module MUST provide score breakdown for each candidate showing individual scores (skill, activity, experience, domain)
- **FR-013**: Module MUST provide reasoning for each score explaining what factors contributed
- **FR-014**: Module MUST highlight which skills were matched and which were missing
- **FR-015**: Module MUST show how activity score was calculated (e.g., "500 contributions in last year")

#### Output Format
- **FR-016**: Module MUST return list of RankedCandidate objects with original candidate data plus scoring metadata
- **FR-017**: Each RankedCandidate MUST include: total_score, skill_match_score, activity_score, experience_score, domain_score, score_breakdown (explanation)
- **FR-018**: Module MUST preserve all original Candidate fields (github_username, repos, etc.)

#### Performance
- **FR-019**: Module MUST complete ranking within [NEEDS CLARIFICATION: time limit - part of 2min total? specific?]
- **FR-020**: Module MUST be deterministic (same inputs always produce same scores)

#### Edge Cases
- **FR-021**: Module MUST handle empty candidate list (return empty ranked list)
- **FR-022**: Module MUST handle candidates with missing fields (score based on available data)
- **FR-023**: Module MUST handle JobRequirement with no domain specified (skip domain scoring)

### Key Entities

#### RankedCandidate (Output)
- Represents a scored and ranked GitHub candidate
- Attributes:
  - All fields from Candidate (github_username, name, bio, repos, languages, etc.)
  - total_score (0-100, weighted combination of all scores)
  - skill_match_score (0-100, percentage of required skills matched)
  - activity_score (0-100, based on contributions and recency)
  - experience_score (0-100, based on account age and repo maturity)
  - domain_score (0-100, based on project similarity to job domain)
  - rank (1, 2, 3... position in sorted list)
  - score_breakdown (object with explanations for each score)
    - matched_skills (list of skills found)
    - missing_skills (list of skills not found)
    - activity_reasoning (e.g., "500 contributions in last year")
    - experience_reasoning (e.g., "7-year-old account, 5 repos with 100+ stars")
    - domain_reasoning (e.g., "3 fintech projects found")
- Relationships: Extends Candidate from Module 002, consumed by Module 004 (Outreach Generator)

#### ScoreWeights (Configuration)
- Represents weighting formula for score combination
- Attributes:
  - skill_match_weight (default: 40%)
  - activity_weight (default: 20%)
  - experience_weight (default: 20%)
  - domain_weight (default: 20%)
- Note: Weights must sum to 100%
- Relationships: Used by scoring algorithm to calculate total_score

---

## Dependencies

### Input Dependencies
- **Module 001 (JD Parser)**: Provides JobRequirement with required_skills, domain, seniority_level
- **Module 002 (GitHub Sourcer)**: Provides list of Candidate objects with repos, languages, activity data

### External Dependencies
- **None**: This is a pure algorithm module (no API calls, no database, no external services)

### Output Consumers
- **Module 004 (Outreach Generator)**: Uses RankedCandidate data to personalize messages
- **Module 005 (Backend API)**: Returns ranked candidates to frontend

---

## Performance Requirements

- **PR-001**: Ranking must complete within allocated time (part of 2-minute total pipeline)
- **PR-002**: Algorithm should be efficient (O(n log n) for sorting, O(n) for scoring)
- **PR-003**: Module must handle up to [NEEDS CLARIFICATION: max candidates - 100? 500? 1000?] candidates without performance degradation

---

## Review & Acceptance Checklist
*GATE: Automated checks run during main() execution*

### Content Quality
- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

### Requirement Completeness
- [ ] No [NEEDS CLARIFICATION] markers remain (6 items need clarification)
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

---

## Execution Status
*Updated by main() during processing*

- [x] User description parsed
- [x] Key concepts extracted (inputs, scoring, ranking, transparency)
- [x] Ambiguities marked (6 NEEDS CLARIFICATION items)
- [x] User scenarios defined
- [x] Requirements generated (23 functional requirements)
- [x] Entities identified (2 entities)
- [ ] Review checklist passed (warnings: clarifications needed)

---

## Next Steps

1. **Clarify this spec** → Resolve 6 [NEEDS CLARIFICATION] items
2. **Plan implementation** → Design scoring algorithm
3. **Generate tasks** → TDD task list
4. **Build module** → Pure function, no external dependencies
