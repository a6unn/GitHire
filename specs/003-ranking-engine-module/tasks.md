# Task List: Ranking Engine Module (Module 003)

**Created**: 2025-10-06
**Based on**: `specs/003-ranking-engine-module/plan.md`

---

## Task Breakdown

### Phase 1: Data Models & Setup (Tasks 1-3)

#### Task 1: Create module structure
- [ ] Create `src/ranking_engine/` directory
- [ ] Create `src/ranking_engine/__init__.py`
- [ ] Create `src/ranking_engine/models.py`
- [ ] Create `src/ranking_engine/scorers/` directory
- [ ] Create `src/ranking_engine/scorers/__init__.py`
- [ ] Create `tests/ranking_engine/` directory
- [ ] Update `pyproject.toml` if needed

#### Task 2: Implement data models
- [ ] Define `ScoreBreakdown` Pydantic model
  - matched_skills: list[str]
  - missing_skills: list[str]
  - activity_reasoning: str
  - experience_reasoning: str
  - domain_reasoning: str
- [ ] Define `ScoreWeights` Pydantic model
  - skill_match_weight: float = 0.40
  - experience_weight: float = 0.20
  - activity_weight: float = 0.20
  - domain_weight: float = 0.20
  - Add validator: weights must sum to 1.0 (±0.01 tolerance)
- [ ] Define `RankedCandidate` Pydantic model
  - candidate: Candidate (from Module 002)
  - rank: int (1-indexed)
  - total_score: float (0-100)
  - skill_match_score: float (0-100)
  - activity_score: float (0-100)
  - experience_score: float (0-100)
  - domain_score: float (0-100)
  - score_breakdown: ScoreBreakdown

#### Task 3: Write contract tests for models
- [ ] Create `tests/contract/test_ranking_models.py`
- [ ] Test ScoreWeights validation (sum to 1.0)
- [ ] Test ScoreWeights invalid (sum < 0.99 or > 1.01)
- [ ] Test RankedCandidate with valid data
- [ ] Test RankedCandidate with score ranges (0-100)
- [ ] Test ScoreBreakdown structure

---

### Phase 2: Skill Scoring (Tasks 4-7)

#### Task 4: Implement skill matcher with LLM
- [ ] Create `src/ranking_engine/skill_matcher.py`
- [ ] Import LLMClient from Module 001
- [ ] Implement `SkillMatcher` class:
  - `__init__(self, llm_client: Optional[LLMClient] = None)`
  - `match_skills(required_skills: list[str], candidate_languages: list[str]) -> tuple[list[str], list[str]]`
- [ ] Logic:
  - First pass: exact matches (case-insensitive)
  - Second pass: LLM semantic matching for remaining skills
  - Return (matched_skills, missing_skills)
- [ ] Create prompt template for skill matching

#### Task 5: Write tests for skill matcher
- [ ] Create `tests/integration/test_skill_matcher.py`
- [ ] Test exact matches (case-insensitive)
- [ ] Test semantic matching with mocked LLM (React → Frontend)
- [ ] Test no matches
- [ ] Test all matches
- [ ] Test empty required skills
- [ ] Test empty candidate languages

#### Task 6: Implement skill scorer
- [ ] Create `src/ranking_engine/scorers/skill_scorer.py`
- [ ] Implement `SkillScorer` class:
  - `score(matched_skills: list[str], required_skills: list[str]) -> float`
- [ ] Logic: `(len(matched) / len(required)) * 100`
- [ ] Handle edge case: empty required_skills → return 100.0

#### Task 7: Write tests for skill scorer
- [ ] Create `tests/integration/test_skill_scorer.py`
- [ ] Test 0% match (0 of 5)
- [ ] Test 60% match (3 of 5)
- [ ] Test 100% match (5 of 5)
- [ ] Test empty required skills → 100%
- [ ] Test edge cases

---

### Phase 3: Experience Scoring (Tasks 8-10)

#### Task 8: Implement experience scorer
- [ ] Create `src/ranking_engine/scorers/experience_scorer.py`
- [ ] Implement `ExperienceScorer` class:
  - `score(candidate: Candidate) -> tuple[float, str]`
- [ ] Scoring algorithm:
  - Account age score (0-100): scale days since creation
    - 0-365 days → 0-30 points
    - 1-3 years → 30-60 points
    - 3-5 years → 60-80 points
    - 5+ years → 80-100 points
  - Stars score (0-100): scale total stars across repos
    - 0-10 stars → 0-30 points
    - 10-100 stars → 30-70 points
    - 100-1000 stars → 70-90 points
    - 1000+ stars → 90-100 points
  - Repo count score (0-100): scale public repos
    - 0-5 repos → 0-40 points
    - 5-20 repos → 40-70 points
    - 20-50 repos → 70-90 points
    - 50+ repos → 90-100 points
  - Weighted average: 40% account age + 30% stars + 30% repo count
- [ ] Generate reasoning string explaining score

#### Task 9: Write tests for experience scorer
- [ ] Create `tests/integration/test_experience_scorer.py`
- [ ] Test new account (1 month old) → low score
- [ ] Test veteran account (7 years old) → high score
- [ ] Test high stars (1000+) → high score
- [ ] Test low stars (5) → low score
- [ ] Test many repos (100+) → high score
- [ ] Test few repos (2) → low score
- [ ] Test composite scoring (varied inputs)

#### Task 10: Handle missing created_at field
- [ ] Add fallback for candidates without created_at (assume average: 3 years)
- [ ] Test fallback behavior

---

### Phase 4: Activity Scoring (Tasks 11-13)

#### Task 11: Implement activity scorer
- [ ] Create `src/ranking_engine/scorers/activity_scorer.py`
- [ ] Implement `ActivityScorer` class:
  - `score(candidate: Candidate) -> tuple[float, str]`
- [ ] Scoring algorithm:
  - Followers score (0-100): scale followers count
    - 0-10 followers → 0-30 points
    - 10-100 followers → 30-60 points
    - 100-1000 followers → 60-85 points
    - 1000+ followers → 85-100 points
  - Public repos score (0-100): scale repos count
    - 0-5 repos → 0-40 points
    - 5-20 repos → 40-70 points
    - 20+ repos → 70-100 points
  - Weighted average: 50% followers + 50% repos
- [ ] Generate reasoning string

#### Task 12: Write tests for activity scorer
- [ ] Create `tests/integration/test_activity_scorer.py`
- [ ] Test high followers (5000+) → high score
- [ ] Test low followers (5) → low score
- [ ] Test many repos (50+) → high score
- [ ] Test few repos (2) → low score
- [ ] Test zero followers and repos → 0 score

#### Task 13: Handle missing activity fields
- [ ] Add fallback for missing followers (default: 0)
- [ ] Test fallback behavior

---

### Phase 5: Domain Scoring (Tasks 14-16)

#### Task 14: Implement domain scorer with LLM
- [ ] Create `src/ranking_engine/scorers/domain_scorer.py`
- [ ] Implement `DomainScorer` class:
  - `__init__(self, llm_client: Optional[LLMClient] = None)`
  - `score(candidate: Candidate, job_domain: Optional[str]) -> tuple[float, str]`
- [ ] Logic:
  - If job_domain is None → return (0.0, "No domain specified")
  - Extract repo names and descriptions from candidate
  - Use LLM to match repos against job domain
  - Score based on number of relevant repos found
- [ ] Create prompt template for domain matching

#### Task 15: Write tests for domain scorer
- [ ] Create `tests/integration/test_domain_scorer.py`
- [ ] Test matching domain (fintech repos + fintech job) → high score
- [ ] Test non-matching domain (healthcare repos + fintech job) → low score
- [ ] Test no domain specified → 0 score
- [ ] Test no repos → 0 score
- [ ] Mock LLM responses

#### Task 16: Handle missing domain in JobRequirement
- [ ] Ensure domain_scorer returns (0.0, "No domain specified")
- [ ] Test that ranker redistributes weight when domain missing

---

### Phase 6: Main Ranker (Tasks 17-20)

#### Task 17: Implement Ranker class
- [ ] Create `src/ranking_engine/ranker.py`
- [ ] Implement `Ranker` class:
  - `__init__(weights: Optional[ScoreWeights] = None, llm_client: Optional[LLMClient] = None)`
  - Initialize all scorers (skill, experience, activity, domain)
  - Store weights (default: ScoreWeights())

#### Task 18: Implement rank method
- [ ] Implement `rank(candidates: list[Candidate], job_requirement: JobRequirement) -> list[RankedCandidate]`
- [ ] For each candidate:
  - Use SkillMatcher to get matched/missing skills
  - Calculate skill_match_score using SkillScorer
  - Calculate experience_score using ExperienceScorer
  - Calculate activity_score using ActivityScorer
  - Calculate domain_score using DomainScorer
  - Calculate total_score: weighted sum of all scores
  - Build ScoreBreakdown with reasoning
  - Create RankedCandidate object
- [ ] Sort candidates by total_score descending
- [ ] Handle ties: sort by candidate.followers (more followers ranked higher)
- [ ] Assign rank (1-indexed)
- [ ] Return sorted list

#### Task 19: Handle domain weight redistribution
- [ ] When job_requirement.domain is None:
  - Redistribute domain_weight to other scores
  - New weights: skill 50%, experience 25%, activity 25%
- [ ] Test redistribution logic

#### Task 20: Write tests for Ranker
- [ ] Create `tests/integration/test_ranker.py`
- [ ] Test ranking with 5 candidates (varied scores)
- [ ] Test candidates sorted correctly (highest score first)
- [ ] Test tie-breaking by followers
- [ ] Test with missing domain (weight redistribution)
- [ ] Test with empty candidate list → return []
- [ ] Test with single candidate
- [ ] Mock all LLM calls

---

### Phase 7: Integration & Public API (Tasks 21-24)

#### Task 21: Create public API
- [ ] Update `src/ranking_engine/__init__.py`:
  - Import Ranker, RankedCandidate, ScoreWeights
  - Create convenience function:
    ```python
    def rank_candidates(
        candidates: list[Candidate],
        job_requirement: JobRequirement,
        weights: Optional[ScoreWeights] = None
    ) -> list[RankedCandidate]:
        ranker = Ranker(weights=weights)
        return ranker.rank(candidates, job_requirement)
    ```
  - Export: rank_candidates, Ranker, RankedCandidate, ScoreWeights

#### Task 22: Write end-to-end integration test
- [ ] Create `tests/integration/test_full_ranking_pipeline.py`
- [ ] Test: JobRequirement + Candidates → RankedCandidates
- [ ] Verify score breakdowns are populated
- [ ] Verify ranks are assigned correctly
- [ ] Mock LLM calls

#### Task 23: Update demo_pipeline.py
- [ ] Add Module 003 to demo pipeline:
  - Parse JD → Search GitHub → **Rank Candidates**
- [ ] Show top 3 ranked candidates with scores
- [ ] Display score breakdown for each candidate

#### Task 24: Update documentation
- [ ] Update `README.md`:
  - Add Module 003 status (✅ Complete with X tests)
  - Add ranking example code
  - Update architecture diagram
- [ ] Add to `.gitignore` if needed
- [ ] Update pyproject.toml scripts if needed

---

## Summary

**Total Tasks**: 24
- Phase 1 (Setup): 3 tasks
- Phase 2 (Skill): 4 tasks
- Phase 3 (Experience): 3 tasks
- Phase 4 (Activity): 3 tasks
- Phase 5 (Domain): 3 tasks
- Phase 6 (Ranker): 4 tasks
- Phase 7 (Integration): 4 tasks

**Expected Test Count**: ~35+ tests for Module 003

**Timeline Estimate**: Following TDD approach, implement one phase at a time.
