# Implementation Plan: Ranking Engine Module (Module 003)

**Status**: Planning
**Created**: 2025-10-06
**Based on**: `specs/003-ranking-engine-module/spec.md`

---

## Overview

Module 003 takes candidates from Module 002 and job requirements from Module 001, then scores and ranks them based on:
- **Skill Match** (40%): How many required skills the candidate has
- **Experience** (20%): Account age, repo maturity, stars
- **Activity** (20%): Recent contributions and activity level
- **Domain Relevance** (20%): Projects matching job domain

Returns ranked candidates with transparent score breakdowns.

---

## Architecture

### Core Components

```
src/ranking_engine/
├── __init__.py              # Public API (rank_candidates function)
├── models.py                # RankedCandidate, ScoreWeights, ScoreBreakdown
├── ranker.py                # Main Ranker class
├── scorers/
│   ├── __init__.py
│   ├── skill_scorer.py      # Skill match scoring
│   ├── experience_scorer.py # Experience scoring
│   ├── activity_scorer.py   # Activity scoring
│   └── domain_scorer.py     # Domain relevance scoring
└── skill_matcher.py         # LLM-based semantic skill matching
```

### Data Models

**RankedCandidate** (extends Candidate from Module 002):
```python
class ScoreBreakdown(BaseModel):
    matched_skills: list[str]
    missing_skills: list[str]
    activity_reasoning: str
    experience_reasoning: str
    domain_reasoning: str

class RankedCandidate(BaseModel):
    # All Candidate fields
    candidate: Candidate

    # Ranking fields
    rank: int
    total_score: float  # 0-100
    skill_match_score: float  # 0-100
    activity_score: float  # 0-100
    experience_score: float  # 0-100
    domain_score: float  # 0-100
    score_breakdown: ScoreBreakdown
```

**ScoreWeights** (configuration):
```python
class ScoreWeights(BaseModel):
    skill_match_weight: float = 0.40
    experience_weight: float = 0.20
    activity_weight: float = 0.20
    domain_weight: float = 0.20

    @model_validator(mode='after')
    def weights_sum_to_one(self):
        total = (self.skill_match_weight + self.experience_weight +
                 self.activity_weight + self.domain_weight)
        if not 0.99 <= total <= 1.01:
            raise ValueError("Weights must sum to 1.0")
        return self
```

---

## Implementation Phases

### Phase 1: Data Models (Task 1-3)
- Create `models.py` with RankedCandidate, ScoreWeights, ScoreBreakdown
- Add Pydantic validation
- Write contract tests

### Phase 2: Skill Scoring (Task 4-7)
- Implement `skill_matcher.py` with LLM-based semantic matching
- Implement `skill_scorer.py`
- Calculate percentage match (matched / required)
- Write tests with mocked LLM

### Phase 3: Experience Scoring (Task 8-10)
- Implement `experience_scorer.py`
- Calculate composite score:
  - Account age (days since creation)
  - Total repos and stars
  - Repo maturity (oldest repo age)
- Write tests

### Phase 4: Activity Scoring (Task 11-13)
- Implement `activity_scorer.py`
- Calculate based on:
  - Total contributions
  - Followers count
  - Public repos count
- Write tests

### Phase 5: Domain Scoring (Task 14-16)
- Implement `domain_scorer.py` with LLM-based matching
- Match candidate repos against job domain
- Handle missing domain (skip scoring)
- Write tests

### Phase 6: Main Ranker (Task 17-20)
- Implement `ranker.py` - orchestrates all scorers
- Combine weighted scores
- Sort by total score
- Handle ties by total contributions
- Generate score breakdowns

### Phase 7: Integration & Testing (Task 21-24)
- Create public API in `__init__.py`
- Write integration tests
- Test with real Module 001 + 002 outputs
- Update demo_pipeline.py

---

## Detailed Component Design

### 1. SkillMatcher (LLM-based)

```python
class SkillMatcher:
    """Semantic skill matching using LLM."""

    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm_client = llm_client or create_llm_client("openai")

    def match_skills(
        self,
        required_skills: list[str],
        candidate_languages: list[str]
    ) -> tuple[list[str], list[str]]:
        """
        Returns (matched_skills, missing_skills).
        Uses LLM to do semantic matching.
        """
        # First: exact matches (case-insensitive)
        # Then: LLM for semantic matches
        # e.g., "React" matches "Frontend Development"
```

### 2. SkillScorer

```python
class SkillScorer:
    """Calculates skill match score."""

    def score(
        self,
        matched_skills: list[str],
        required_skills: list[str]
    ) -> float:
        """Returns 0-100 based on percentage match."""
        if not required_skills:
            return 100.0
        return (len(matched_skills) / len(required_skills)) * 100
```

### 3. ExperienceScorer

```python
class ExperienceScorer:
    """Calculates experience score based on GitHub history."""

    def score(self, candidate: Candidate) -> tuple[float, str]:
        """Returns (score 0-100, reasoning)."""
        # Account age weight: 40%
        # Total stars weight: 30%
        # Repo count weight: 30%
```

### 4. ActivityScorer

```python
class ActivityScorer:
    """Calculates activity score based on recent contributions."""

    def score(self, candidate: Candidate) -> tuple[float, str]:
        """Returns (score 0-100, reasoning)."""
        # Followers weight: 30%
        # Public repos weight: 30%
        # (Could add contribution count if available: 40%)
```

### 5. DomainScorer

```python
class DomainScorer:
    """Calculates domain relevance using LLM."""

    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm_client = llm_client or create_llm_client("openai")

    def score(
        self,
        candidate: Candidate,
        job_domain: Optional[str]
    ) -> tuple[float, str]:
        """Returns (score 0-100, reasoning)."""
        if not job_domain:
            return (0.0, "No domain specified")

        # Use LLM to match repo descriptions/names against job domain
```

### 6. Ranker (Main Orchestrator)

```python
class Ranker:
    """Main ranking engine."""

    def __init__(
        self,
        weights: Optional[ScoreWeights] = None,
        llm_client: Optional[LLMClient] = None
    ):
        self.weights = weights or ScoreWeights()
        self.skill_matcher = SkillMatcher(llm_client)
        self.skill_scorer = SkillScorer()
        self.experience_scorer = ExperienceScorer()
        self.activity_scorer = ActivityScorer()
        self.domain_scorer = DomainScorer(llm_client)

    def rank(
        self,
        candidates: list[Candidate],
        job_requirement: JobRequirement
    ) -> list[RankedCandidate]:
        """
        Score and rank all candidates.

        1. For each candidate:
           - Score skills (with semantic matching)
           - Score experience
           - Score activity
           - Score domain
           - Calculate weighted total
        2. Sort by total score descending
        3. Handle ties by total contributions
        4. Assign ranks
        5. Return list of RankedCandidate
        """
```

---

## Testing Strategy

### Contract Tests (Test Phase 1)
- `test_ranked_candidate_model.py`: Validate RankedCandidate Pydantic model
- `test_score_weights_model.py`: Validate weights sum to 1.0
- `test_score_breakdown_model.py`: Validate ScoreBreakdown structure

### Unit Tests (Test Phase 2-5)
- `test_skill_matcher.py`: Test semantic skill matching with mocked LLM
- `test_skill_scorer.py`: Test skill match percentage calculation
- `test_experience_scorer.py`: Test experience scoring algorithm
- `test_activity_scorer.py`: Test activity scoring algorithm
- `test_domain_scorer.py`: Test domain matching with mocked LLM

### Integration Tests (Test Phase 6)
- `test_ranker.py`: Test full ranking pipeline
- `test_ranking_with_ties.py`: Test tie-breaking logic
- `test_missing_domain.py`: Test when domain not specified
- `test_empty_candidates.py`: Test edge case with no candidates

### End-to-End Test (Test Phase 7)
- `test_full_pipeline_with_ranking.py`: Module 001 → 002 → 003

---

## Dependencies

### From Module 001
- `JobRequirement` model (required_skills, domain, seniority_level)

### From Module 002
- `Candidate` model (languages, followers, repos, etc.)

### New Dependencies
- OpenAI API (already available from Module 001)
- No new external dependencies needed

---

## Performance Targets

- **Ranking 25 candidates**: < 5 seconds (including LLM calls)
- **LLM calls**: Minimize by batching (one call for all skill matches, one for domain)
- **Algorithm complexity**: O(n log n) for sorting

---

## Success Criteria

1. ✅ All 26 functional requirements from spec implemented
2. ✅ Transparent score breakdowns (FR-013 to FR-016)
3. ✅ LLM-based semantic skill matching (FR-017)
4. ✅ Deterministic scoring (FR-022)
5. ✅ Handle all edge cases (FR-024 to FR-026)
6. ✅ All tests passing (target: 30+ tests for Module 003)
7. ✅ Integration with existing pipeline working

---

## Next Steps

1. Create detailed task list from this plan
2. Implement TDD: Write tests first for each component
3. Implement components in order (Phase 1 → 7)
4. Update demo_pipeline.py to include ranking
5. Update README.md with Module 003 status
