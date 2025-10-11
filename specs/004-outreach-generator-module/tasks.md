# Implementation Tasks: Module 004 - Outreach Generator (Enhanced)

**Status**: Ready for Implementation
**Estimated Total Tasks**: 85+ tasks across 11 phases
**Approach**: Test-Driven Development (TDD)
**Target**: 120-140 tests passing, 30-50% response rate

---

## Phase 1: Setup & Data Models (12 tasks)

### Task 1.1: Create Module Structure
- [ ] Create directory `src/outreach_generator/`
- [ ] Create `src/outreach_generator/__init__.py` (empty for now)
- [ ] Create `src/outreach_generator/models.py`
- [ ] Create `src/outreach_generator/stages/` directory
- [ ] Create `src/outreach_generator/stages/__init__.py`
- [ ] Create `src/outreach_generator/prompts/` directory
- [ ] Create `tests/outreach_generator/` directory
- [ ] Create `tests/outreach_generator/contract/` directory
- [ ] Create `tests/outreach_generator/integration/` directory

**Acceptance**: Directory structure matches enhanced plan

### Task 1.2: Define Channel and Angle Enums
- [ ] In `models.py`, create `ChannelType` enum: "email", "linkedin", "twitter"
- [ ] Create `FollowUpAngle` enum: "reminder", "technical_challenge", "career_growth", "soft_close"
- [ ] Add docstrings explaining usage

**Acceptance**: Enums import correctly

### Task 1.3: Define PersonalizationMetadata Model
- [ ] Create `PersonalizationMetadata` Pydantic model in `models.py`
- [ ] Add fields: `referenced_repositories: list[str]`
- [ ] Add `technical_details_mentioned: list[str]`
- [ ] Add `enrichment_data_used: dict`
- [ ] Add `analysis_insights: dict`
- [ ] Add `cliches_removed: list[str]`
- [ ] Add `quality_flags: list[str]`

**Acceptance**: Model validates correctly

### Task 1.4: Define OutreachMessage Model
- [ ] Create `OutreachMessage` Pydantic model in `models.py`
- [ ] Add fields: `shortlist_id: str`, `channel: ChannelType`, `subject_line: Optional[str]`
- [ ] Add `message_text: str`, `personalization_score: float` (0-100)
- [ ] Add `personalization_metadata: PersonalizationMetadata`
- [ ] Add `tokens_used: int`, `stage_breakdown: dict`
- [ ] Add `is_edited: bool`, `generated_at: datetime`, `edited_at: Optional[datetime]`
- [ ] Add field validators: score 0-100, channel valid, subject_line 36-50 chars if email

**Acceptance**: Model validates all fields with proper constraints

### Task 1.5: Define FollowUpSequence Model
- [ ] Create `FollowUpSequence` Pydantic model in `models.py`
- [ ] Add fields: `outreach_message_id: str`, `sequence_number: int` (1-3)
- [ ] Add `scheduled_days_after: int` (3, 7, or 14)
- [ ] Add `message_text: str`, `angle: FollowUpAngle`
- [ ] Add `generated_at: datetime`
- [ ] Add validator for sequence_number (1-3) and scheduled_days_after (3, 7, 14)

**Acceptance**: Model validates correctly

### Task 1.6: Write Contract Tests for PersonalizationMetadata
- [ ] Create `tests/outreach_generator/contract/test_models.py`
- [ ] Test valid PersonalizationMetadata creation
- [ ] Test with empty lists (should validate)
- [ ] Test with populated data

**Acceptance**: 3-4 tests passing

### Task 1.7: Write Contract Tests for OutreachMessage
- [ ] Test valid OutreachMessage creation for email (with subject_line)
- [ ] Test valid OutreachMessage for LinkedIn (no subject_line)
- [ ] Test personalization_score validation (reject < 0, > 100)
- [ ] Test email subject_line length validation (36-50 chars)
- [ ] Test channel validation (only email/linkedin/twitter)
- [ ] Test tokens_used (non-negative)
- [ ] Test stage_breakdown structure

**Acceptance**: 7-8 tests passing

### Task 1.8: Write Contract Tests for FollowUpSequence
- [ ] Test valid FollowUpSequence creation
- [ ] Test sequence_number validation (1-3)
- [ ] Test scheduled_days_after validation (3, 7, 14)
- [ ] Test angle validation

**Acceptance**: 4-5 tests passing

### Task 1.9: Run Phase 1 Tests
- [ ] Execute `pytest tests/outreach_generator/contract/`
- [ ] Verify 14-17 tests passing

**Acceptance**: All contract tests green

### Task 1.10: Export Models from __init__.py
- [ ] Update `src/outreach_generator/__init__.py`
- [ ] Export `OutreachMessage`, `PersonalizationMetadata`, `FollowUpSequence`
- [ ] Export `ChannelType`, `FollowUpAngle`

**Acceptance**: `from src.outreach_generator import OutreachMessage` works

### Task 1.11: Phase 1 Documentation
- [ ] Add docstrings to all models
- [ ] Document field constraints and examples

**Acceptance**: Models well-documented

### Task 1.12: Phase 1 Complete
- [ ] Review code quality
- [ ] Ensure all tests passing
- [ ] Commit Phase 1 work with message: "feat: Module 004 Phase 1 - Data models and contract tests"

**Acceptance**: Phase 1 checkpoint reached (~15-20 tests passing)

---

## Phase 2: Stage 1 - Analysis (LLM Profile Analysis) (10 tasks)

### Task 2.1: Create AnalysisStage Class
- [ ] Create `src/outreach_generator/stages/analysis_stage.py`
- [ ] Define `AnalysisStage` class with `__init__(llm_client: LLMClient)`
- [ ] Add docstring explaining Stage 1 purpose

**Acceptance**: Class importable

### Task 2.2: Create Analysis Prompt Template
- [ ] Create `src/outreach_generator/prompts/analysis_prompt.py`
- [ ] Define function `build_analysis_prompt(candidate: dict, enrichment: dict, job_req: dict) -> str`
- [ ] Prompt structure:
   - Role: "You are a technical recruiting researcher with 10 years of experience"
   - Context: Candidate GitHub data, enrichment data, job requirements
   - Task: Analyze and identify top 3 achievements, passion areas, trajectory, conversation starters
   - Output format: JSON with structured fields
- [ ] Include examples in prompt for better GPT-4 output

**Acceptance**: Function returns formatted prompt string

### Task 2.3: Implement AnalysisStage.analyze() Method
- [ ] Add method `analyze(candidate: dict, enrichment: dict, job_req: dict) -> dict`
- [ ] Build prompt using `build_analysis_prompt()`
- [ ] Call LLM with prompt requesting JSON output
- [ ] Parse JSON response to extract:
   - `achievements: list[str]` (top 3)
   - `passion_areas: list[str]`
   - `career_trajectory: str`
   - `conversation_starters: list[str]`
- [ ] Track tokens used
- [ ] Return structured dict (AnalysisInsights)

**Acceptance**: Method executes and returns structured data

### Task 2.4: Add Fallback Strategy for Minimal Data
- [ ] Check if candidate has minimal repos (<3 repos)
- [ ] If minimal data, use fallback prompt focusing on potential rather than past work
- [ ] Set flag `minimal_data_fallback: true` in insights

**Acceptance**: Handles candidates with 0-2 repos

### Task 2.5: Write Test for Analysis with Rich Data
- [ ] Create `tests/outreach_generator/integration/test_analysis_stage.py`
- [ ] Mock LLMClient to return deterministic analysis JSON
- [ ] Test: Candidate with 10+ repos, GPT-4 returns achievements, passion areas, trajectory, starters
- [ ] Verify: All fields populated, tokens tracked

**Acceptance**: 2-3 tests passing

### Task 2.6: Write Test for Analysis with Minimal Data
- [ ] Test: Candidate with 1 repo
- [ ] Verify: Fallback strategy used, insights focus on potential
- [ ] Verify: `minimal_data_fallback: true` in result

**Acceptance**: 2 tests passing

### Task 2.7: Write Test for Enrichment Data Usage
- [ ] Test: Candidate with LinkedIn, Twitter, blog from enrichment
- [ ] Verify: Enrichment data included in prompt
- [ ] Verify: Analysis references company, bio, social profiles

**Acceptance**: 2-3 tests passing

### Task 2.8: Write Test for Error Handling
- [ ] Test: LLM returns non-JSON response
- [ ] Verify: Graceful error handling, return fallback insights

**Acceptance**: 1-2 tests passing

### Task 2.9: Run Phase 2 Tests
- [ ] Execute `pytest tests/outreach_generator/integration/test_analysis_stage.py`
- [ ] Verify 9-13 tests passing

**Acceptance**: All analysis tests green

### Task 2.10: Phase 2 Complete
- [ ] Run all tests: `pytest tests/outreach_generator/`
- [ ] Verify ~25-35 cumulative tests passing
- [ ] Commit Phase 2 work: "feat: Module 004 Phase 2 - Stage 1 Analysis implementation"

**Acceptance**: Phase 2 checkpoint reached

---

## Phase 3: Channel Optimizer (10 tasks)

### Task 3.1: Create ChannelOptimizer Class
- [ ] Create `src/outreach_generator/channel_optimizer.py`
- [ ] Define `ChannelOptimizer` class
- [ ] Add docstring explaining purpose

**Acceptance**: Class importable

### Task 3.2: Implement Email Validation
- [ ] Add method `validate_email(subject: str, body: str) -> tuple[bool, list[str]]`
- [ ] Check subject line length: 36-50 chars
- [ ] Check body word count: 50-125 words
- [ ] Return (is_valid, error_messages)

**Acceptance**: Validation logic works

### Task 3.3: Implement Email Formatting
- [ ] Add method `format_for_email(subject: str, body: str) -> dict`
- [ ] Validate using `validate_email()`
- [ ] Structure body: Hook → Context → Opportunity → CTA
- [ ] Return `{subject_line: str, message_text: str, channel: "email"}`

**Acceptance**: Email formatting works

### Task 3.4: Implement LinkedIn Validation
- [ ] Add method `validate_linkedin(message: str) -> tuple[bool, list[str]]`
- [ ] Check total length: <400 chars
- [ ] Check sentence count: 3-4 sentences (heuristic)
- [ ] Return (is_valid, error_messages)

**Acceptance**: LinkedIn validation works

### Task 3.5: Implement LinkedIn Formatting
- [ ] Add method `format_for_linkedin(message: str) -> dict`
- [ ] Validate using `validate_linkedin()`
- [ ] Ensure professional casual tone markers
- [ ] Return `{message_text: str, channel: "linkedin"}`

**Acceptance**: LinkedIn formatting works

### Task 3.6: Implement Twitter Validation
- [ ] Add method `validate_twitter(message: str) -> tuple[bool, list[str]]`
- [ ] Check total length: <280 chars
- [ ] Check sentence count: 2-3 sentences
- [ ] Return (is_valid, error_messages)

**Acceptance**: Twitter validation works

### Task 3.7: Implement Twitter Formatting
- [ ] Add method `format_for_twitter(message: str) -> dict`
- [ ] Validate using `validate_twitter()`
- [ ] Ensure very casual tone
- [ ] Return `{message_text: str, channel: "twitter"}`

**Acceptance**: Twitter formatting works

### Task 3.8: Write Tests for Email Formatting
- [ ] Create `tests/outreach_generator/integration/test_channel_optimizer.py`
- [ ] Test: Valid email (subject 40 chars, body 100 words) → validates successfully
- [ ] Test: Invalid email (subject 60 chars) → validation fails
- [ ] Test: Invalid email (body 30 words) → validation fails

**Acceptance**: 3-4 tests passing

### Task 3.9: Write Tests for LinkedIn and Twitter Formatting
- [ ] Test: Valid LinkedIn (350 chars, 4 sentences) → validates
- [ ] Test: Invalid LinkedIn (450 chars) → validation fails
- [ ] Test: Valid Twitter (250 chars, 3 sentences) → validates
- [ ] Test: Invalid Twitter (300 chars) → validation fails

**Acceptance**: 4-5 tests passing

### Task 3.10: Phase 3 Complete
- [ ] Run `pytest tests/outreach_generator/integration/test_channel_optimizer.py`
- [ ] Verify 7-9 tests passing
- [ ] Run all tests: `pytest tests/outreach_generator/`
- [ ] Verify ~32-44 cumulative tests passing
- [ ] Commit Phase 3 work: "feat: Module 004 Phase 3 - Channel-specific formatting and validation"

**Acceptance**: Phase 3 checkpoint reached

---

## Phase 4: Stage 2 - Generation (Multi-Channel Messages) (12 tasks)

### Task 4.1: Create GenerationStage Class
- [ ] Create `src/outreach_generator/stages/generation_stage.py`
- [ ] Define `GenerationStage` class with `__init__(llm_client: LLMClient, channel_optimizer: ChannelOptimizer)`
- [ ] Add docstring

**Acceptance**: Class importable

### Task 4.2: Create Email Generation Prompt
- [ ] Create `src/outreach_generator/prompts/generation_prompt.py`
- [ ] Define `build_email_prompt(insights: dict, job_req: dict, enrichment: dict) -> str`
- [ ] Prompt structure:
   - Role: "Empathetic technical recruiter writing like a developer, not a salesperson"
   - Context: Analysis insights, job details, enrichment data
   - Constraints: 50-125 words, subject 36-50 chars, Hook → Context → Opportunity → CTA
   - Requirements: Specific repo mention, technical detail, salary range, clear CTA
   - Forbidden phrases: "reaching out", "great opportunity", "passionate team"
- [ ] Output format: JSON with `{subject_line: str, body: str}`

**Acceptance**: Function returns email generation prompt

### Task 4.3: Create LinkedIn Generation Prompt
- [ ] Define `build_linkedin_prompt(insights: dict, job_req: dict, enrichment: dict) -> str`
- [ ] Constraints: <400 chars, 3-4 sentences, professional casual tone
- [ ] Requirements: Lead with technical detail, include salary, Calendly link
- [ ] Output format: JSON with `{message: str}`

**Acceptance**: Function returns LinkedIn generation prompt

### Task 4.4: Create Twitter Generation Prompt
- [ ] Define `build_twitter_prompt(insights: dict, job_req: dict, enrichment: dict) -> str`
- [ ] Constraints: <280 chars, 2-3 sentences, very casual tone
- [ ] Requirements: Specific project mention, quick value prop, role, salary, link
- [ ] Output format: JSON with `{message: str}`

**Acceptance**: Function returns Twitter generation prompt

### Task 4.5: Implement Determine Available Channels
- [ ] Add method `_determine_channels(enrichment: dict) -> list[str]`
- [ ] Check `primary_email` → add "email"
- [ ] Check `linkedin_username` → add "linkedin"
- [ ] Check `twitter_username` → add "twitter"
- [ ] Return list of available channels

**Acceptance**: Method correctly identifies available channels

### Task 4.6: Implement GenerationStage.generate() for Email
- [ ] Add method `generate(insights: dict, job_req: dict, enrichment: dict, channel: str) -> dict`
- [ ] If channel == "email":
   - Build prompt using `build_email_prompt()`
   - Call LLM requesting JSON output
   - Parse response to extract subject_line and body
   - Use ChannelOptimizer.format_for_email() to validate
   - Track tokens used
   - Return formatted message dict

**Acceptance**: Email generation works

### Task 4.7: Implement GenerationStage.generate() for LinkedIn
- [ ] If channel == "linkedin":
   - Build prompt using `build_linkedin_prompt()`
   - Call LLM requesting JSON output
   - Parse response to extract message
   - Use ChannelOptimizer.format_for_linkedin() to validate
   - Track tokens used
   - Return formatted message dict

**Acceptance**: LinkedIn generation works

### Task 4.8: Implement GenerationStage.generate() for Twitter
- [ ] If channel == "twitter":
   - Build prompt using `build_twitter_prompt()`
   - Call LLM requesting JSON output
   - Parse response to extract message
   - Use ChannelOptimizer.format_for_twitter() to validate
   - Track tokens used
   - Return formatted message dict

**Acceptance**: Twitter generation works

### Task 4.9: Write Tests for Email Generation
- [ ] Create `tests/outreach_generator/integration/test_generation_stage.py`
- [ ] Mock LLMClient to return email JSON (subject + body)
- [ ] Test: Generate email for candidate with Python repos + Python job
- [ ] Verify: Subject 36-50 chars, body 50-125 words, repo mentioned, salary included

**Acceptance**: 3-4 tests passing

### Task 4.10: Write Tests for LinkedIn and Twitter Generation
- [ ] Test: Generate LinkedIn message (<400 chars, repo mentioned, salary included)
- [ ] Test: Generate Twitter message (<280 chars, repo mentioned, salary included)
- [ ] Test: Enrichment data with only email → generates only email

**Acceptance**: 4-5 tests passing

### Task 4.11: Write Test for Validation Failure
- [ ] Test: LLM returns message exceeding constraints (e.g., 600 char LinkedIn)
- [ ] Verify: Validation fails, error returned

**Acceptance**: 2 tests passing

### Task 4.12: Phase 4 Complete
- [ ] Run `pytest tests/outreach_generator/integration/test_generation_stage.py`
- [ ] Verify 9-11 tests passing
- [ ] Run all tests: `pytest tests/outreach_generator/`
- [ ] Verify ~41-55 cumulative tests passing
- [ ] Commit Phase 4 work: "feat: Module 004 Phase 4 - Stage 2 Multi-channel generation"

**Acceptance**: Phase 4 checkpoint reached

---

## Phase 5: Cliché Detector & Personalization Scorer (10 tasks)

### Task 5.1: Create ClicheDetector Class
- [ ] Create `src/outreach_generator/cliche_detector.py`
- [ ] Define `ClicheDetector` class
- [ ] Add class-level CLICHES list:
   - "reaching out", "great opportunity", "passionate team", "exciting challenges"
   - "cutting-edge", "world-class", "innovative" (without context)
   - "touching base", "circle back", "synergy", "thought leader"

**Acceptance**: Class importable with cliché list

### Task 5.2: Implement Cliché Detection
- [ ] Add method `detect(message: str) -> list[str]`
- [ ] Case-insensitive search for clichés
- [ ] Return list of detected clichés

**Acceptance**: Detection works

### Task 5.3: Implement Cliché Removal
- [ ] Add method `remove(message: str) -> tuple[str, list[str]]`
- [ ] Find and remove clichés, replace with neutral text or remove sentence
- [ ] Return (cleaned_message, removed_cliches)

**Acceptance**: Removal works

### Task 5.4: Write Tests for Cliché Detection
- [ ] Create `tests/outreach_generator/integration/test_cliche_detector.py`
- [ ] Test: Message with "reaching out" → detected
- [ ] Test: Message with "great opportunity" → detected
- [ ] Test: Message with multiple clichés → all detected
- [ ] Test: Clean message → no clichés detected

**Acceptance**: 4-5 tests passing

### Task 5.5: Write Tests for Cliché Removal
- [ ] Test: Remove "reaching out" from message
- [ ] Test: Remove multiple clichés from message
- [ ] Verify: Cleaned message makes sense, removed list accurate

**Acceptance**: 3-4 tests passing

### Task 5.6: Create PersonalizationScorer Class
- [ ] Create `src/outreach_generator/personalization_scorer.py`
- [ ] Define `PersonalizationScorer` class
- [ ] Add docstring explaining scoring formula

**Acceptance**: Class importable

### Task 5.7: Implement Scoring Logic
- [ ] Add method `score(message: str, candidate: dict, enrichment: dict) -> tuple[float, dict]`
- [ ] Scoring:
   - Check specific repo mention (name in message): +30 points
   - Check technical detail (code/feature keyword): +30 points
   - Check unique insight (enrichment data referenced): +20 points
   - Check enrichment usage (email/LinkedIn/Twitter/blog): +20 points
- [ ] Return (score: 0-100, breakdown: dict)

**Acceptance**: Scoring calculation works

### Task 5.8: Write Tests for Personalization Scoring
- [ ] Create `tests/outreach_generator/integration/test_personalization_scorer.py`
- [ ] Test: Message with repo mention → +30 points
- [ ] Test: Message with technical detail ("concurrent writes", "redis implementation") → +30 points
- [ ] Test: Message with enrichment usage (LinkedIn company) → +20 points
- [ ] Test: Full personalization → 100 points

**Acceptance**: 5-6 tests passing

### Task 5.9: Write Test for Low Personalization Score
- [ ] Test: Generic message with no repo, no technical detail → low score (<40)

**Acceptance**: 1 test passing

### Task 5.10: Phase 5 Complete
- [ ] Run `pytest tests/outreach_generator/integration/test_cliche_detector.py`
- [ ] Run `pytest tests/outreach_generator/integration/test_personalization_scorer.py`
- [ ] Verify 13-16 tests passing for Phase 5
- [ ] Run all tests: `pytest tests/outreach_generator/`
- [ ] Verify ~54-71 cumulative tests passing
- [ ] Commit Phase 5 work: "feat: Module 004 Phase 5 - Cliché detection and personalization scoring"

**Acceptance**: Phase 5 checkpoint reached

---

## Phase 6: Stage 3 - Refinement (Quality Validation) (10 tasks)

### Task 6.1: Create RefinementStage Class
- [ ] Create `src/outreach_generator/stages/refinement_stage.py`
- [ ] Define `RefinementStage` class with `__init__(llm_client: LLMClient, cliche_detector: ClicheDetector, personalization_scorer: PersonalizationScorer)`
- [ ] Add docstring

**Acceptance**: Class importable

### Task 6.2: Create Refinement Prompt Template
- [ ] Create `src/outreach_generator/prompts/refinement_prompt.py`
- [ ] Define `build_refinement_prompt(message: str, candidate: dict, detected_cliches: list[str]) -> str`
- [ ] Prompt structure:
   - Role: "Quality assurance specialist for recruiting messages"
   - Task: Review message, remove clichés, verify specifics, ensure CTA clarity
   - Context: Original message, candidate data, detected clichés
   - Output: Refined message (no clichés, specific mentions verified, polished)

**Acceptance**: Function returns refinement prompt

### Task 6.3: Implement RefinementStage.refine() Method
- [ ] Add method `refine(message: dict, candidate: dict, enrichment: dict, insights: dict) -> dict`
- [ ] Step 1: Use ClicheDetector.detect() to find clichés
- [ ] Step 2: If clichés found, use ClicheDetector.remove() or LLM refinement prompt to clean
- [ ] Step 3: Verify specific mentions (cross-check repo names with candidate data)
- [ ] Step 4: Verify CTA clarity (contains action word or link)
- [ ] Step 5: Use PersonalizationScorer.score() to calculate score
- [ ] Step 6: If score < 70, set `quality_flags: ["low_personalization"]`
- [ ] Track tokens used
- [ ] Return refined message dict with metadata

**Acceptance**: Method executes refinement steps

### Task 6.4: Implement Specific Mention Verification
- [ ] Add helper `_verify_specific_mentions(message: str, candidate: dict) -> bool`
- [ ] Check if at least one repo name from candidate.top_repos is in message
- [ ] Return True if verified, False otherwise

**Acceptance**: Verification logic works

### Task 6.5: Implement CTA Clarity Verification
- [ ] Add helper `_verify_cta_clarity(message: str) -> bool`
- [ ] Check for action words: "chat", "discuss", "connect", "schedule", "call", "meeting"
- [ ] Check for link pattern (http:// or calendly)
- [ ] Return True if CTA clear, False otherwise

**Acceptance**: CTA verification works

### Task 6.6: Write Tests for Refinement with Clichés
- [ ] Create `tests/outreach_generator/integration/test_refinement_stage.py`
- [ ] Mock LLMClient for refinement
- [ ] Test: Message with "reaching out" → clichés detected and removed
- [ ] Verify: Cleaned message, `cliches_removed` list populated

**Acceptance**: 2-3 tests passing

### Task 6.7: Write Tests for Specific Mention Verification
- [ ] Test: Message mentions "redis-clone" (repo in candidate data) → verified
- [ ] Test: Message with no repo mention → verification fails, quality flag set

**Acceptance**: 2-3 tests passing

### Task 6.8: Write Tests for Personalization Scoring in Refinement
- [ ] Test: High personalization message → score 80-100, no quality flags
- [ ] Test: Low personalization message → score <70, quality flag "low_personalization"

**Acceptance**: 2-3 tests passing

### Task 6.9: Write Test for Full Refinement Pipeline
- [ ] Test: Raw message (clichés, no specific mention, weak CTA) → refined message (clean, specific, clear CTA, score calculated)
- [ ] Verify: All refinement steps executed, metadata complete

**Acceptance**: 2-3 tests passing

### Task 6.10: Phase 6 Complete
- [ ] Run `pytest tests/outreach_generator/integration/test_refinement_stage.py`
- [ ] Verify 8-12 tests passing
- [ ] Run all tests: `pytest tests/outreach_generator/`
- [ ] Verify ~62-83 cumulative tests passing
- [ ] Commit Phase 6 work: "feat: Module 004 Phase 6 - Stage 3 Refinement and quality validation"

**Acceptance**: Phase 6 checkpoint reached

---

## Phase 7: Orchestrator (3-Stage Integration) (10 tasks)

### Task 7.1: Create OutreachOrchestrator Class
- [ ] Create `src/outreach_generator/orchestrator.py`
- [ ] Define `OutreachOrchestrator` class with `__init__(llm_client: LLMClient)`
- [ ] Initialize all stages: AnalysisStage, GenerationStage, RefinementStage
- [ ] Initialize helpers: ChannelOptimizer, ClicheDetector, PersonalizationScorer

**Acceptance**: Class importable

### Task 7.2: Implement generate_outreach() for Single Candidate
- [ ] Add method `generate_outreach(candidate: dict, enrichment: dict, job_req: dict) -> list[OutreachMessage]`
- [ ] **Stage 1**: Call AnalysisStage.analyze() to get insights
- [ ] **Determine channels**: Call GenerationStage._determine_channels()
- [ ] **Stage 2**: For each channel, call GenerationStage.generate()
- [ ] **Stage 3**: For each raw message, call RefinementStage.refine()
- [ ] Build PersonalizationMetadata for each message
- [ ] Track tokens per stage (`stage_breakdown: {analysis: X, generation: Y, refinement: Z}`)
- [ ] Create OutreachMessage objects
- [ ] Return list of OutreachMessage (one per channel)

**Acceptance**: Method executes 3-stage pipeline

### Task 7.3: Build PersonalizationMetadata
- [ ] Add helper `_build_metadata(insights: dict, refined_message: dict) -> PersonalizationMetadata`
- [ ] Extract `referenced_repositories` from refined_message
- [ ] Extract `technical_details_mentioned` from refined_message
- [ ] Extract `enrichment_data_used` from insights
- [ ] Set `analysis_insights` = insights
- [ ] Set `cliches_removed` from refinement
- [ ] Set `quality_flags` from refinement
- [ ] Return PersonalizationMetadata object

**Acceptance**: Metadata construction works

### Task 7.4: Implement Token Tracking
- [ ] Track tokens from Stage 1 (analysis)
- [ ] Track tokens from Stage 2 (generation per channel)
- [ ] Track tokens from Stage 3 (refinement per channel)
- [ ] Calculate total tokens
- [ ] Store breakdown in OutreachMessage.stage_breakdown

**Acceptance**: Token tracking accurate

### Task 7.5: Write Test for Full Pipeline - Email Only
- [ ] Create `tests/outreach_generator/integration/test_orchestrator.py`
- [ ] Mock LLMClient for all 3 stages
- [ ] Test: Candidate with email only → 1 OutreachMessage (email channel)
- [ ] Verify: 3 stages executed, message refined, personalization score calculated, tokens tracked

**Acceptance**: 3-4 tests passing

### Task 7.6: Write Test for Multi-Channel Pipeline
- [ ] Test: Candidate with email, LinkedIn, Twitter → 3 OutreachMessages
- [ ] Verify: Each channel has specific format (email has subject, LinkedIn <400 chars, Twitter <280 chars)
- [ ] Verify: All messages have unique content

**Acceptance**: 3-4 tests passing

### Task 7.7: Write Test for Low Personalization Flag
- [ ] Test: Candidate with minimal data → messages generated, personalization score <70, quality flag set

**Acceptance**: 2 tests passing

### Task 7.8: Implement Batch Generation
- [ ] Add method `generate_batch(candidates: list[dict], enrichments: list[dict], job_req: dict) -> list[list[OutreachMessage]]`
- [ ] Loop through candidates, call generate_outreach() for each
- [ ] Track diversity (check for repeated phrases across batch)
- [ ] Return list of lists (one inner list per candidate)

**Acceptance**: Batch generation works

### Task 7.9: Write Test for Batch Diversity
- [ ] Test: Generate for 3 similar candidates (all Python developers)
- [ ] Verify: Messages are unique, no copy-paste feel
- [ ] Verify: Different repos mentioned for each

**Acceptance**: 2-3 tests passing

### Task 7.10: Phase 7 Complete
- [ ] Run `pytest tests/outreach_generator/integration/test_orchestrator.py`
- [ ] Verify 10-13 tests passing
- [ ] Run all tests: `pytest tests/outreach_generator/`
- [ ] Verify ~72-96 cumulative tests passing
- [ ] Commit Phase 7 work: "feat: Module 004 Phase 7 - Orchestrator 3-stage pipeline integration"

**Acceptance**: Phase 7 checkpoint reached

---

## Phase 8: Follow-Up Sequence Generation (8 tasks)

### Task 8.1: Create FollowUpGenerator Class
- [ ] Create `src/outreach_generator/follow_up_generator.py`
- [ ] Define `FollowUpGenerator` class with `__init__(llm_client: LLMClient)`
- [ ] Add docstring

**Acceptance**: Class importable

### Task 8.2: Create Follow-Up Prompts
- [ ] Create `src/outreach_generator/prompts/followup_prompt.py`
- [ ] Define `build_followup_prompt(original_message: str, job_req: dict, candidate: dict, sequence_num: int, angle: str) -> str`
- [ ] Prompt variations by angle:
   - "reminder": Brief reminder + different repo mention
   - "technical_challenge": Preview actual technical problem from role
   - "career_growth": Emphasize career progression opportunity
   - "soft_close": Final gentle close with opt-out
- [ ] Constraints: Match original channel length limits

**Acceptance**: Function returns follow-up prompts

### Task 8.3: Implement generate_sequence() Method
- [ ] Add method `generate_sequence(outreach_message: OutreachMessage, job_req: dict, candidate: dict) -> list[FollowUpSequence]`
- [ ] Generate 3 follow-ups:
   - Sequence 1 (Day 3, Reminder): Brief reminder + different repo
   - Sequence 2 (Day 7, Technical Challenge): Technical problem preview
   - Sequence 3 (Day 14, Soft Close): Final gentle close
- [ ] Call LLM for each with appropriate angle prompt
- [ ] Track tokens used
- [ ] Create FollowUpSequence objects
- [ ] Return list

**Acceptance**: Method generates 3 follow-ups

### Task 8.4: Implement Context Preservation
- [ ] Ensure follow-ups reference original message context (same repo, same technical area)
- [ ] Ensure follow-ups don't repeat exact wording

**Acceptance**: Context preserved, no repetition

### Task 8.5: Write Test for Reminder Follow-Up
- [ ] Create `tests/outreach_generator/integration/test_followup_generator.py`
- [ ] Mock LLMClient
- [ ] Test: Generate Day 3 reminder follow-up
- [ ] Verify: Sequence number 1, scheduled_days_after 3, angle "reminder", different repo mentioned

**Acceptance**: 2-3 tests passing

### Task 8.6: Write Test for Technical Challenge Follow-Up
- [ ] Test: Generate Day 7 technical challenge follow-up
- [ ] Verify: Sequence number 2, scheduled_days_after 7, angle "technical_challenge", problem mentioned

**Acceptance**: 2 tests passing

### Task 8.7: Write Test for Full Follow-Up Sequence
- [ ] Test: Generate all 3 follow-ups for original email message
- [ ] Verify: 3 FollowUpSequence objects, different angles, no repetition

**Acceptance**: 2-3 tests passing

### Task 8.8: Phase 8 Complete
- [ ] Run `pytest tests/outreach_generator/integration/test_followup_generator.py`
- [ ] Verify 6-8 tests passing
- [ ] Run all tests: `pytest tests/outreach_generator/`
- [ ] Verify ~78-104 cumulative tests passing
- [ ] Commit Phase 8 work: "feat: Module 004 Phase 8 - Follow-up sequence generation"

**Acceptance**: Phase 8 checkpoint reached

---

## Phase 9: Public API & Backend Integration (10 tasks)

### Task 9.1: Create Public API Functions
- [ ] Update `src/outreach_generator/__init__.py`
- [ ] Define `generate_outreach(candidate: dict, enrichment: dict, job_req: dict) -> list[OutreachMessage]`
- [ ] Create OutreachOrchestrator and call generate_outreach()
- [ ] Define `generate_follow_ups(outreach_message: OutreachMessage, job_req: dict, candidate: dict) -> list[FollowUpSequence]`
- [ ] Create FollowUpGenerator and call generate_sequence()

**Acceptance**: Public API functions work

### Task 9.2: Create Database Models
- [ ] Create `src/backend_api/models/outreach_message.py`
- [ ] Define SQLAlchemy `OutreachMessageDB` model:
   - id (UUID), shortlist_id (FK), channel, subject_line, message_text
   - personalization_score, personalization_metadata (JSON)
   - tokens_used, stage_breakdown (JSON), is_edited
   - generated_at, edited_at
- [ ] Define SQLAlchemy `FollowUpSequenceDB` model:
   - id (UUID), outreach_message_id (FK), sequence_number, scheduled_days_after
   - message_text, angle, generated_at

**Acceptance**: Database models defined

### Task 9.3: Create Backend Endpoint - Generate Outreach
- [ ] In `src/backend_api/routers/projects_router.py`
- [ ] Add `POST /projects/{project_id}/shortlist/{username}/outreach`
- [ ] Fetch shortlisted candidate and enrichment data
- [ ] Fetch job requirement from project
- [ ] Call `generate_outreach()` from Module 004
- [ ] Save OutreachMessage objects to database
- [ ] Return list of OutreachMessage responses

**Acceptance**: Endpoint generates and saves outreach

### Task 9.4: Create Backend Endpoint - Get Outreach
- [ ] Add `GET /projects/{project_id}/shortlist/{username}/outreach`
- [ ] Fetch existing OutreachMessage records from database
- [ ] Return list of OutreachMessage responses

**Acceptance**: Endpoint retrieves outreach

### Task 9.5: Create Backend Endpoint - Update (Edit) Outreach
- [ ] Add `PUT /projects/{project_id}/shortlist/{username}/outreach/{message_id}`
- [ ] Accept updated message_text in request body
- [ ] Update database record, set is_edited=True, edited_at=now
- [ ] Return updated OutreachMessage

**Acceptance**: Endpoint updates outreach

### Task 9.6: Create Backend Endpoint - Regenerate Outreach
- [ ] Add `POST /projects/{project_id}/shortlist/{username}/outreach/{message_id}/regenerate`
- [ ] Delete existing message
- [ ] Call `generate_outreach()` to create new message
- [ ] Save to database
- [ ] Return new OutreachMessage

**Acceptance**: Endpoint regenerates outreach

### Task 9.7: Create Backend Endpoint - Generate Follow-Ups
- [ ] Add `POST /projects/{project_id}/shortlist/{username}/outreach/{message_id}/follow-ups`
- [ ] Fetch original OutreachMessage
- [ ] Fetch job requirement and candidate data
- [ ] Call `generate_follow_ups()` from Module 004
- [ ] Save FollowUpSequence objects to database
- [ ] Return list of FollowUpSequence responses

**Acceptance**: Endpoint generates and saves follow-ups

### Task 9.8: Write API Tests
- [ ] Create `tests/backend_api/test_outreach_endpoints.py`
- [ ] Test: POST generate outreach → 3 messages created (email, LinkedIn, Twitter)
- [ ] Test: GET outreach → retrieves existing messages
- [ ] Test: PUT update outreach → is_edited=True
- [ ] Test: POST regenerate → new message created
- [ ] Test: POST generate follow-ups → 3 follow-ups created

**Acceptance**: 5-7 API tests passing

### Task 9.9: Run Backend Tests
- [ ] Execute `pytest tests/backend_api/test_outreach_endpoints.py`
- [ ] Verify 5-7 tests passing

**Acceptance**: All backend API tests green

### Task 9.10: Phase 9 Complete
- [ ] Run all tests: `pytest tests/outreach_generator/` and `pytest tests/backend_api/`
- [ ] Verify ~83-111 cumulative tests passing
- [ ] Commit Phase 9 work: "feat: Module 004 Phase 9 - Public API and backend integration"

**Acceptance**: Phase 9 checkpoint reached

---

## Phase 10: Frontend Integration (10 tasks)

### Task 10.1: Add Frontend API Client Functions
- [ ] Update `frontend/src/api/projects.ts`
- [ ] Add `generateOutreach(projectId: string, username: string): Promise<OutreachMessage[]>`
- [ ] Add `getOutreach(projectId: string, username: string): Promise<OutreachMessage[]>`
- [ ] Add `updateOutreach(projectId: string, username: string, messageId: string, text: string): Promise<OutreachMessage>`
- [ ] Add `regenerateOutreach(projectId: string, username: string, messageId: string): Promise<OutreachMessage>`
- [ ] Add `generateFollowUps(projectId: string, username: string, messageId: string): Promise<FollowUpSequence[]>`

**Acceptance**: API client functions defined

### Task 10.2: Create OutreachPanel Component
- [ ] Create `frontend/src/components/OutreachPanel.tsx`
- [ ] Component receives: `projectId: string, username: string`
- [ ] State: `outreachMessages: OutreachMessage[], loading: boolean, error: string`
- [ ] "Generate Outreach" button (calls generateOutreach API)
- [ ] Display loading state while generating

**Acceptance**: Component renders

### Task 10.3: Implement Outreach Display
- [ ] Display generated messages in tabs: "Email", "LinkedIn", "Twitter"
- [ ] Each tab shows:
   - Subject line (email only)
   - Message text
   - Personalization score (0-100) with color coding (green >80, yellow 70-80, red <70)
   - Referenced repos (list)
   - Technical details mentioned (list)
   - Tokens used
   - Stage breakdown (analysis, generation, refinement tokens)

**Acceptance**: Outreach messages display correctly

### Task 10.4: Implement Inline Editing
- [ ] Add "Edit" button per message
- [ ] On click, make message_text editable (textarea)
- [ ] "Save" button calls updateOutreach API
- [ ] "Cancel" button reverts changes
- [ ] Show "Edited" badge if is_edited=true

**Acceptance**: Editing works

### Task 10.5: Implement Copy to Clipboard
- [ ] Add "Copy to Clipboard" button per message
- [ ] On click, copy message_text to clipboard
- [ ] Show toast: "Copied to clipboard!"

**Acceptance**: Copy works

### Task 10.6: Implement Regenerate
- [ ] Add "Regenerate" button per message
- [ ] On click, call regenerateOutreach API
- [ ] Replace old message with new one
- [ ] Show loading state during regeneration

**Acceptance**: Regenerate works

### Task 10.7: Create FollowUpPanel Component
- [ ] Create `frontend/src/components/FollowUpPanel.tsx`
- [ ] Component receives: `projectId: string, username: string, outreachMessageId: string`
- [ ] "Generate Follow-Ups" button
- [ ] Display 3 follow-ups:
   - Day 3 (Reminder)
   - Day 7 (Technical Challenge)
   - Day 14 (Soft Close)
- [ ] Each shows: message_text, angle, scheduled_days_after
- [ ] "Copy to Clipboard" button for each follow-up

**Acceptance**: Follow-up panel works

### Task 10.8: Integrate into ShortlistedCandidatesPage
- [ ] Update `frontend/src/pages/ShortlistedCandidatesPage.tsx`
- [ ] Add "Generate Outreach" button per candidate (in candidate card)
- [ ] On click, open modal or expand section showing OutreachPanel
- [ ] If outreach already exists, show "View Outreach" button instead

**Acceptance**: Integration complete

### Task 10.9: Add TypeScript Types
- [ ] Create `frontend/src/types/outreach.ts`
- [ ] Define `OutreachMessage` interface
- [ ] Define `PersonalizationMetadata` interface
- [ ] Define `FollowUpSequence` interface

**Acceptance**: Types defined

### Task 10.10: Phase 10 Complete
- [ ] Test in browser:
   - Generate outreach for shortlisted candidate
   - Verify 3 messages (email, LinkedIn, Twitter if enriched)
   - Edit a message, save, verify "Edited" badge
   - Copy message to clipboard
   - Regenerate a message
   - Generate follow-ups, verify 3 follow-ups displayed
- [ ] Commit Phase 10 work: "feat: Module 004 Phase 10 - Frontend UI for outreach generation"

**Acceptance**: Phase 10 checkpoint reached, UI fully functional

---

## Phase 11: End-to-End Testing & Documentation (5 tasks)

### Task 11.1: Full Workflow Test
- [ ] Test complete workflow in browser:
   1. Create project with job description (include salary range)
   2. Source candidates (Module 002)
   3. Shortlist candidates
   4. Enrich candidates (Module 010)
   5. Generate outreach (Module 004)
- [ ] Verify: Email, LinkedIn, Twitter messages generated
- [ ] Verify: Personalization score >= 70 for all messages
- [ ] Verify: Specific repo mentioned in each message
- [ ] Verify: Salary range included in each message
- [ ] Verify: No clichés in messages ("reaching out", "great opportunity", etc.)

**Acceptance**: Full workflow works end-to-end

### Task 11.2: Manual Quality Review
- [ ] Review generated messages for quality:
   - [ ] Check for recruiter clichés (should be removed)
   - [ ] Verify specific GitHub repo mentions (should be present)
   - [ ] Verify technical details (code/feature references)
   - [ ] Verify salary transparency (should be included)
   - [ ] Verify CTA clarity (should have Calendly link or clear ask)
   - [ ] Verify message uniqueness (no template feel)
   - [ ] Verify channel constraints (email 50-125 words, LinkedIn <400 chars, Twitter <280 chars)

**Acceptance**: Quality standards met

### Task 11.3: Performance Validation
- [ ] Measure time to generate outreach for 1 candidate:
   - [ ] Stage 1 (Analysis): < 3 seconds
   - [ ] Stage 2 (Generation): < 5 seconds
   - [ ] Stage 3 (Refinement): < 2 seconds
   - [ ] Total: < 10 seconds
- [ ] Measure batch generation for 10 candidates: < 60 seconds

**Acceptance**: Performance targets met

### Task 11.4: Update Documentation
- [ ] Update `README.md`:
   - [ ] Add Module 004 to Implementation Status section
   - [ ] Update total test count (~220-250 tests)
   - [ ] Add Module 004 usage example (code snippet)
   - [ ] Update project structure with outreach_generator/
   - [ ] Update data flow diagram: "... → Shortlist → Enrich → **Outreach** → Messages"
- [ ] Update `WORKFLOW_SPEC.md`:
   - [ ] Add outreach generation step after enrichment
   - [ ] Include 3-stage pipeline explanation
   - [ ] Include multi-channel optimization details
- [ ] Create `OUTREACH_QUICKSTART.md`:
   - [ ] Quick guide for using outreach generation feature
   - [ ] Example workflows
   - [ ] Best practices for reviewing/editing messages

**Acceptance**: Documentation complete and accurate

### Task 11.5: Final Phase Complete
- [ ] Run full test suite: `pytest`
- [ ] Verify ~120-140 tests passing for Module 004
- [ ] Verify total project tests: ~220-250
- [ ] All tests green
- [ ] Code quality reviewed
- [ ] Commit final work: "feat: Module 004 COMPLETE - Research-backed outreach generation with 30-50% response rate target"
- [ ] Create PR summary highlighting:
   - 3-stage LLM pipeline (Analysis → Generation → Refinement)
   - Multi-channel support (Email, LinkedIn, Twitter)
   - Personalization scoring (0-100)
   - Cliché detection and removal
   - Follow-up sequence generation
   - Full UI integration with editing and regeneration

**Acceptance**: Module 004 COMPLETE ✅

---

## Summary

| Phase | Tasks | Estimated Tests | Cumulative Tests |
|-------|-------|-----------------|------------------|
| Phase 1: Setup & Models | 12 | 15-20 | 15-20 |
| Phase 2: Stage 1 - Analysis | 10 | 9-13 | 24-33 |
| Phase 3: Channel Optimizer | 10 | 7-9 | 31-42 |
| Phase 4: Stage 2 - Generation | 12 | 9-11 | 40-53 |
| Phase 5: Cliché Detector & Scorer | 10 | 13-16 | 53-69 |
| Phase 6: Stage 3 - Refinement | 10 | 8-12 | 61-81 |
| Phase 7: Orchestrator | 10 | 10-13 | 71-94 |
| Phase 8: Follow-Up Generator | 8 | 6-8 | 77-102 |
| Phase 9: Backend Integration | 10 | 5-7 | 82-109 |
| Phase 10: Frontend Integration | 10 | 0 (manual) | 82-109 |
| Phase 11: E2E & Documentation | 5 | 0 (manual) | 82-109 |
| **Total** | **107** | **82-109** | **120-140** (with API tests) |

## Execution Approach

1. **TDD Throughout**: Write tests before implementation
2. **Sequential Phases**: Complete phases 1 → 11 in order
3. **Commit Per Phase**: Git commit at end of each phase with descriptive message
4. **Test After Each Phase**: Run pytest to verify cumulative tests passing
5. **Manual Testing**: Phases 10-11 require browser testing for UI validation
6. **Quality Gates**:
   - Phase 1: Models validate correctly
   - Phase 2-6: Individual stages work independently
   - Phase 7: Full 3-stage pipeline integrated
   - Phase 8: Follow-ups generate correctly
   - Phase 9: Backend API functional
   - Phase 10: UI fully functional
   - Phase 11: End-to-end quality validated

## Success Criteria

- ✅ All ~120-140 tests passing for Module 004
- ✅ Full pipeline works: Create Project → Source → Rank → Shortlist → Enrich → **Outreach**
- ✅ Messages reference actual candidate repos by name (validated)
- ✅ Personalization score >= 70 for all messages (validated)
- ✅ No clichés detected in final messages (validated)
- ✅ Salary range included in 100% of messages (validated)
- ✅ Multi-channel support working (Email, LinkedIn, Twitter)
- ✅ Follow-up sequences generated with different angles (validated)
- ✅ UI editing and regeneration functional (tested in browser)
- ✅ Performance targets met (< 10 sec per candidate)
- ✅ Total project tests: ~220-250 (141 existing + 80-109 new)
- ✅ **Target achieved: 30-50% response rate** (validated in production use)

---

**Ready to implement! 🚀**

Follow TDD approach, commit frequently, and aim for the 30-50% response rate target!
