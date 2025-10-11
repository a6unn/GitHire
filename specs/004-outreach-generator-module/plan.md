# Implementation Plan: Module 004 - Outreach Generator (Enhanced)

**Feature Branch**: `004-outreach-generator-module`
**Created**: 2025-10-06
**Updated**: 2025-10-10 (Research-backed enhancement)
**Status**: Ready for Implementation

## Overview

Module 004 generates highly personalized, research-backed outreach messages for shortlisted GitHub candidates using a **3-stage LLM pipeline** (Analysis → Generation → Refinement) and **multi-channel optimization** (Email, LinkedIn, Twitter). The module integrates with Module 010 (Contact Enrichment) to leverage enriched contact data and targets **30-50% response rates** (vs industry average 5-12%).

## Architecture Design

### Core Components

```
src/outreach_generator/
├── __init__.py                    # Public API (generate_outreach, generate_follow_ups)
├── models.py                      # Pydantic models (OutreachMessage, PersonalizationMetadata, FollowUpSequence)
├── orchestrator.py                # OutreachOrchestrator (3-stage pipeline coordinator)
├── stages/
│   ├── __init__.py
│   ├── analysis_stage.py          # Stage 1: Deep GitHub analysis
│   ├── generation_stage.py        # Stage 2: Multi-channel message generation
│   └── refinement_stage.py        # Stage 3: Quality validation & refinement
├── channel_optimizer.py           # Channel-specific formatting (Email, LinkedIn, Twitter)
├── personalization_scorer.py      # Calculate personalization score (0-100)
├── cliche_detector.py             # Detect & remove recruiter clichés
└── prompts/
    ├── analysis_prompt.py         # Stage 1 prompt template
    ├── generation_prompt.py       # Stage 2 prompt templates (per channel)
    └── refinement_prompt.py       # Stage 3 prompt template
```

### Data Models

**OutreachMessage** (Pydantic model):
- `shortlist_id: str` - FK to shortlisted candidate
- `channel: str` - "email", "linkedin", "twitter"
- `subject_line: Optional[str]` - Email only, 36-50 chars
- `message_text: str` - Main body, channel-specific length
- `personalization_score: float` - Quality score 0-100
- `personalization_metadata: PersonalizationMetadata`
- `tokens_used: int` - Total across 3 stages
- `stage_breakdown: dict` - Tokens per stage {analysis: X, generation: Y, refinement: Z}
- `is_edited: bool` - User modified flag
- `generated_at: datetime`
- `edited_at: Optional[datetime]`

**PersonalizationMetadata** (Pydantic model):
- `referenced_repositories: list[str]` - Repo names mentioned
- `technical_details_mentioned: list[str]` - Specific code/feature references
- `enrichment_data_used: dict` - Which Module 010 fields were used
- `analysis_insights: dict` - Stage 1 LLM output summary (achievements, interests, trajectory)
- `cliches_removed: list[str]` - Clichés detected and removed
- `quality_flags: list[str]` - Quality issues if any

**FollowUpSequence** (Pydantic model):
- `outreach_message_id: str` - FK to original message
- `sequence_number: int` - 1, 2, 3
- `scheduled_days_after: int` - 3, 7, 14
- `message_text: str`
- `angle: str` - "reminder", "technical_challenge", "career_growth", "soft_close"
- `generated_at: datetime`

### 3-Stage Pipeline Flow

```
Input: ShortlistedCandidate + EnrichedData + JobRequirement
    ↓
┌────────────────────────────────────────┐
│  STAGE 1: ANALYSIS                     │
│  ─────────────────────                 │
│  AnalysisStage.analyze()               │
│  - Deep GitHub profile analysis        │
│  - Top 3 technical achievements        │
│  - Passion areas & career trajectory   │
│  - Unique conversation starters        │
│  Output: AnalysisInsights              │
└─────────────┬──────────────────────────┘
              │
              ▼
┌────────────────────────────────────────┐
│  STAGE 2: GENERATION                   │
│  ────────────────────                  │
│  GenerationStage.generate()            │
│  - Determine available channels        │
│  - Generate 3 variations per channel   │
│  - Email (50-125 words)                │
│  - LinkedIn (<400 chars)               │
│  - Twitter (<280 chars)                │
│  Output: RawMessages (per channel)     │
└─────────────┬──────────────────────────┘
              │
              ▼
┌────────────────────────────────────────┐
│  STAGE 3: REFINEMENT                   │
│  ─────────────────────                 │
│  RefinementStage.refine()              │
│  - Detect & remove clichés             │
│  - Validate specific mentions          │
│  - Verify CTA clarity                  │
│  - Calculate personalization score     │
│  Output: RefinedOutreachMessage        │
└─────────────┬──────────────────────────┘
              │
              ▼
OutreachMessage (ready for UI display)
```

### Channel-Specific Optimization

**Email Format:**
```
Subject: [36-50 chars, technical hook]
Example: "Your redis-clone project + Backend @ TechCorp"

Body (50-125 words):
- Hook (1 sentence): Specific repo/technical mention
- Context (2 sentences): Who you are, why now
- Opportunity (2 sentences): Role, salary, tech stack
- CTA (1 sentence): Clear next step (Calendly link)
```

**LinkedIn Format:**
```
<400 characters total
3-4 sentences max
- Lead with specific technical detail
- Include role, salary, tech stack
- End with Calendly link
```

**Twitter DM Format:**
```
<280 characters total
2-3 sentences
- Focus on specific project + quick value prop
- Include role, salary
- Single link CTA
```

## Implementation Phases

### Phase 1: Setup & Data Models (Foundation)
**Objective**: Establish project structure and Pydantic models

**Tasks**:
1. Create `src/outreach_generator/` directory structure (stages/, prompts/)
2. Define `OutreachMessage` Pydantic model with all fields and validation
3. Define `PersonalizationMetadata` Pydantic model
4. Define `FollowUpSequence` Pydantic model
5. Add channel enum ("email", "linkedin", "twitter")
6. Add angle enum for follow-ups ("reminder", "technical_challenge", "career_growth", "soft_close")
7. Write contract tests for models (validation, required fields, score ranges)

**Acceptance Criteria**:
- Models validate all fields correctly
- Personalization score enforced 0-100 range
- Channel restricted to valid options
- 15-20 contract tests passing

### Phase 2: Stage 1 - Analysis (Deep GitHub Analysis)
**Objective**: Implement LLM-powered GitHub profile analysis

**Tasks**:
1. Create `AnalysisStage` class
2. Implement `analyze()` method:
   - Build analysis prompt from candidate GitHub data + enrichment data
   - Call GPT-4 with structured output request (JSON)
   - Extract: top 3 achievements, passion areas, trajectory, conversation starters
3. Create `prompts/analysis_prompt.py`:
   - Role: Technical recruiting researcher with 10 years experience
   - Context: GitHub profile, repos, contributions, enrichment data
   - Task: Analyze and identify key personalization points
   - Output: Structured JSON (achievements, interests, trajectory, starters)
4. Write integration tests with mocked GPT-4 responses

**Acceptance Criteria**:
- Analysis prompt includes all candidate data
- GPT-4 returns structured insights
- Handles candidates with minimal data (fallback strategy)
- 10-15 integration tests passing

### Phase 3: Channel Optimizer
**Objective**: Channel-specific message formatting

**Tasks**:
1. Create `ChannelOptimizer` class
2. Implement `format_for_email()`:
   - Validate subject line 36-50 chars
   - Validate body 50-125 words
   - Structure: Hook → Context → Opportunity → CTA
3. Implement `format_for_linkedin()`:
   - Validate <400 chars total
   - 3-4 sentences max
   - Professional casual tone
4. Implement `format_for_twitter()`:
   - Validate <280 chars total
   - 2-3 sentences
   - Very casual tone
5. Write unit tests for formatting

**Acceptance Criteria**:
- Each channel enforces correct character/word limits
- Format validation catches violations
- 12-15 unit tests passing

### Phase 4: Stage 2 - Generation (Multi-Channel Messages)
**Objective**: Generate channel-specific messages using analysis insights

**Tasks**:
1. Create `GenerationStage` class
2. Implement `generate()` method:
   - Determine available channels from enrichment data
   - For each channel, build generation prompt with:
     - Analysis insights from Stage 1
     - Job requirements (role, salary, tech stack)
     - Channel-specific constraints (length, tone)
   - Call GPT-4 to generate 3 variations per channel
   - Use ChannelOptimizer to format
3. Create `prompts/generation_prompt.py`:
   - Separate templates for email, LinkedIn, Twitter
   - Include research-backed best practices
   - Enforce: specific repo mention, technical detail, salary range, clear CTA
4. Write integration tests with mocked GPT-4

**Acceptance Criteria**:
- Generates messages for all available channels
- Messages meet channel-specific constraints
- Salary range always included
- Specific repo mentioned by name
- 15-20 integration tests passing

### Phase 5: Cliché Detector & Personalization Scorer
**Objective**: Quality validation components

**Tasks**:
1. Create `ClicheDetector` class:
   - Maintain list of recruiter clichés ("reaching out", "great opportunity", "passionate team", "exciting challenges", "cutting-edge", "world-class")
   - Implement `detect()` method: Find clichés in message
   - Implement `remove()` method: Remove clichés and replace with neutral text
2. Create `PersonalizationScorer` class:
   - Implement `score()` method:
     - Specific repo mention: +30 points
     - Technical detail (code/feature reference): +30 points
     - Unique insight (not on resume): +20 points
     - Enrichment data usage: +20 points
   - Return score 0-100 + breakdown
3. Write unit tests

**Acceptance Criteria**:
- Detects all common clichés
- Scoring formula validated
- 12-15 unit tests passing

### Phase 6: Stage 3 - Refinement (Quality Validation)
**Objective**: Refine messages for quality and remove clichés

**Tasks**:
1. Create `RefinementStage` class
2. Implement `refine()` method:
   - Call ClicheDetector to find and remove clichés
   - Validate specific mentions (cross-check with candidate data)
   - Verify CTA clarity (contains action word or link)
   - Call PersonalizationScorer to calculate score
   - If score < 70, flag for review
3. Create `prompts/refinement_prompt.py`:
   - Role: Quality assurance for recruiting messages
   - Task: Review message, ensure no clichés, verify specifics, polish
   - Output: Refined message text
4. Write integration tests

**Acceptance Criteria**:
- Clichés successfully removed
- Personalization score calculated accurately
- Messages below 70 score flagged
- 15-20 integration tests passing

### Phase 7: Orchestrator (3-Stage Integration)
**Objective**: Coordinate full 3-stage pipeline

**Tasks**:
1. Create `OutreachOrchestrator` class with GPT-4 client dependency
2. Implement `generate_outreach()` method:
   - Stage 1: Call AnalysisStage.analyze()
   - Stage 2: Call GenerationStage.generate() for each channel
   - Stage 3: Call RefinementStage.refine() on each message
   - Build PersonalizationMetadata
   - Track tokens per stage
   - Return list of OutreachMessage (one per channel)
3. Implement batch generation `generate_batch()`:
   - Generate for multiple candidates
   - Ensure diversity across batch
4. Write integration tests with mocked GPT-4

**Acceptance Criteria**:
- Full 3-stage pipeline executes successfully
- Tokens tracked per stage
- Multi-channel messages generated
- 20-25 integration tests passing

### Phase 8: Follow-Up Sequence Generation
**Objective**: Generate follow-up message sequences

**Tasks**:
1. Create `FollowUpGenerator` class
2. Implement `generate_sequence()` method:
   - Input: Original outreach message + job req
   - Generate 3 follow-ups with different angles:
     - Day 3 (Reminder): Brief reminder + different repo mention
     - Day 7 (Technical Challenge): Preview of actual technical problem
     - Day 14 (Soft Close): Final soft close with opt-out
   - Use GPT-4 with follow-up prompt
3. Write integration tests

**Acceptance Criteria**:
- Generates 2-3 follow-up messages
- Each has different angle
- Follow-ups reference original message context
- 10-12 integration tests passing

### Phase 9: Public API & Backend Integration
**Objective**: Expose clean API and integrate with backend

**Tasks**:
1. Create `__init__.py` with public functions:
   - `generate_outreach(shortlist_id, job_req) -> list[OutreachMessage]`
   - `generate_follow_ups(outreach_message_id) -> list[FollowUpSequence]`
2. Create backend endpoint in `projects_router.py`:
   - `POST /projects/{project_id}/shortlist/{username}/outreach` - Generate outreach
   - `GET /projects/{project_id}/shortlist/{username}/outreach` - Get existing outreach
   - `PUT /projects/{project_id}/shortlist/{username}/outreach/{message_id}` - Update (edit) message
   - `POST /projects/{project_id}/shortlist/{username}/outreach/{message_id}/regenerate` - Regenerate
   - `POST /projects/{project_id}/shortlist/{username}/outreach/{message_id}/follow-ups` - Generate follow-ups
3. Create database models (OutreachMessage, FollowUpSequence tables)
4. Write API-level tests

**Acceptance Criteria**:
- API endpoints work correctly
- Database persistence implemented
- 8-10 API tests passing

### Phase 10: Frontend Integration
**Objective**: Build UI for outreach generation

**Tasks**:
1. Create `OutreachPanel.tsx` component in ShortlistedCandidatesPage:
   - "Generate Outreach" button
   - Display generated messages (tabs for Email/LinkedIn/Twitter)
   - Show personalization score, referenced repos, tokens used
   - Inline editing capability
   - "Copy to Clipboard" button per message
   - "Regenerate" button
2. Create `FollowUpPanel.tsx` component:
   - Display follow-up sequence
   - Show scheduled days (Day 3, Day 7, Day 14)
   - Show angle for each
3. Add API client functions in `frontend/src/api/projects.ts`:
   - `generateOutreach(projectId, username)`
   - `getOutreach(projectId, username)`
   - `updateOutreach(projectId, username, messageId, text)`
   - `regenerateOutreach(projectId, username, messageId)`
   - `generateFollowUps(projectId, username, messageId)`
4. Test in browser

**Acceptance Criteria**:
- UI displays generated outreach
- Editing works
- Copy to clipboard works
- Regenerate works
- Follow-ups display correctly

### Phase 11: End-to-End Testing & Documentation
**Objective**: Full integration testing and documentation

**Tasks**:
1. Test full workflow:
   - Create project → Source candidates → Rank → Shortlist → Enrich → Generate Outreach
   - Verify email, LinkedIn, Twitter messages generated
   - Verify personalization score >= 70
   - Test editing and regeneration
   - Test follow-up generation
2. Manual quality review:
   - Check for clichés (should be removed)
   - Verify specific repo mentions (should be present)
   - Verify salary included (should be present)
   - Verify message uniqueness (no template feel)
3. Update README with Module 004 documentation
4. Update WORKFLOW_SPEC.md to include outreach generation step

**Acceptance Criteria**:
- Full workflow works end-to-end
- Message quality meets research standards
- Documentation complete
- All tests passing (~120-140 tests for Module 004)

## Testing Strategy

### Test Categories

1. **Contract Tests** (Phase 1): 15-20 tests
   - Pydantic model validation
   - Field constraints (score ranges, channel options)

2. **Integration Tests** (Phases 2-8): 95-110 tests
   - AnalysisStage with various candidate profiles
   - GenerationStage with multi-channel outputs
   - RefinementStage with cliché detection
   - OutreachOrchestrator with full pipeline
   - FollowUpGenerator with sequence generation

3. **Mock Strategy**:
   - Mock GPT-4 calls with deterministic responses
   - Test different GPT-4 response scenarios (success, failure, inappropriate content)
   - Ensure fast, repeatable tests

4. **API Tests** (Phase 9): 8-10 tests
   - Backend endpoint functionality
   - Database persistence

5. **End-to-End Tests** (Phase 11):
   - Full workflow with real modules
   - Manual quality review

### Performance Targets

- Stage 1 (Analysis): < 3 seconds
- Stage 2 (Generation): < 5 seconds (3 channels)
- Stage 3 (Refinement): < 2 seconds
- **Total per candidate**: < 10 seconds
- Batch 10 candidates: < 60 seconds (parallel if needed)

## Key Design Decisions

### 1. 3-Stage Pipeline Architecture
**Decision**: Separate analysis, generation, and refinement stages
**Rationale**: Modular design, easier testing, better quality control, token tracking per stage

### 2. Multi-Channel Optimization
**Decision**: Generate separate messages for Email, LinkedIn, Twitter with channel-specific constraints
**Rationale**: Research shows different channels have different best practices; one-size-fits-all doesn't work

### 3. Personalization Scoring Formula
**Decision**: Specific repo (+30) + Technical detail (+30) + Unique insight (+20) + Enrichment usage (+20) = 100
**Rationale**: Quantifiable quality metric based on research findings; helps prioritize which messages need review

### 4. Cliché Detection as Separate Component
**Decision**: Standalone ClicheDetector class with removable cliché list
**Rationale**: Testability, maintainability, ability to update cliché list without touching core logic

### 5. Follow-Up Sequence Generation
**Decision**: Generate 3 follow-ups with different angles at specific intervals (Day 3, 7, 14)
**Rationale**: Research shows multi-touch outreach increases response rates; different angles prevent repetition

### 6. GPT-4 for All Stages
**Decision**: Use GPT-4 (user has API key) for all 3 stages instead of Claude
**Rationale**: User already has GPT-4 subscription; Claude API requires separate payment; GPT-4 sufficient for task

### 7. UI Editing & Regeneration
**Decision**: Allow users to edit generated messages inline and regenerate if needed
**Rationale**: AI-generated content needs human oversight; recruiters know their voice best

## Dependencies

### Internal
- Module 002 (GitHub Sourcer): Candidate GitHub profile, repos, contributions
- Module 010 (Contact Enrichment): Email, LinkedIn, Twitter, blog, company, hireable status
- Module 001 (JD Parser): Job requirements (role, skills, salary, company info)
- Shared LLM Client (updated for GPT-4)

### External
- GPT-4 API (OpenAI): For 3-stage LLM pipeline
- Pydantic v2 for models
- Database (PostgreSQL/SQLite): Store outreach messages, follow-ups

## Success Metrics

- ✅ 120-140 tests passing for Module 004
- ✅ Messages reference actual candidate repos by name (validated in tests)
- ✅ Personalization score >= 70 for all messages
- ✅ No clichés detected in final messages
- ✅ Salary range included in 100% of messages
- ✅ Multi-channel support working (Email, LinkedIn, Twitter)
- ✅ Full pipeline: JD → Parse → Search → Rank → Shortlist → Enrich → Outreach works end-to-end
- ✅ Follow-up sequences generated with different angles
- ✅ UI editing and regeneration functional

## Risks & Mitigations

### Risk 1: GPT-4 Token Costs
**Mitigation**: Track tokens per stage; optimize prompts for brevity; use streaming if needed

### Risk 2: Message Quality (Generic Despite Personalization)
**Mitigation**: Strict validation in Stage 3; personalization score threshold; manual review for <70 score

### Risk 3: Performance (10 seconds per candidate may be slow for batch)
**Mitigation**: Parallel processing for batch generation; consider caching analysis results; optimize prompts

### Risk 4: Cliché Detection Misses New Clichés
**Mitigation**: Maintain updateable cliché list; log all messages for periodic review; user feedback loop

### Risk 5: Channel-Specific Constraints Too Restrictive
**Mitigation**: Graceful fallback if message can't fit constraints; offer to expand limits if needed

## Research-Backed Best Practices Implemented

✅ **Salary transparency** - Always included in message (FR-011)
✅ **Specific repo mentions** - Mandatory in every message (FR-009)
✅ **Technical detail** - Code/feature reference required (FR-010)
✅ **Message brevity** - Channel-specific limits enforced (FR-014)
✅ **Clear CTA** - Calendly link or simple yes/no (FR-013)
✅ **Cliché removal** - Automated detection and removal (FR-019, FR-020)
✅ **Multi-channel optimization** - Email/LinkedIn/Twitter specific (FR-015-018)
✅ **Follow-up sequences** - Multi-touch outreach (FR-024-027)

## Next Steps

1. ✅ Enhanced plan created → **Ready for /tasks**
2. Generate detailed task list (tasks.md) with TDD approach
3. Implement Phase 1 (Setup & Models)
4. Proceed through phases 2-11 with TDD approach
5. Achieve 30-50% response rate target 🎯
