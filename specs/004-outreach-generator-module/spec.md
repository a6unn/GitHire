# Feature Specification: Outreach Generator Module (Enhanced)

**Feature Branch**: `004-outreach-generator-module`
**Created**: 2025-10-06
**Updated**: 2025-10-10 (Research-backed enhancement)
**Status**: Ready for Implementation
**Input**: User description: "AI-powered module that generates personalized, research-backed outreach messages for shortlisted GitHub candidates using 3-stage LLM pipeline, multi-channel optimization, and contact enrichment data to achieve 30-50% response rates"

## User Scenarios & Testing

### Primary User Story
A recruiter has shortlisted top GitHub candidates for a senior backend engineer role. They need to send highly personalized outreach messages that:
- Reference specific GitHub projects and code contributions
- Include salary transparency upfront
- Are optimized for different channels (Email, LinkedIn, Twitter)
- Feel like they're from a technical peer, not a generic recruiter
- Get 30-50% response rates (vs industry average 5-12%)

The system uses a 3-stage LLM pipeline to deeply analyze candidate profiles, generate channel-specific messages, and refine for quality.

### Acceptance Scenarios

1. **Given** a shortlisted candidate with enriched contact data from Module 010, **When** the recruiter requests outreach generation, **Then** the system generates email, LinkedIn, and Twitter messages optimized for each channel with specific repo mentions and salary range

2. **Given** a candidate with "redis-clone" repository showing concurrent writes implementation, **When** outreach is generated for a distributed systems role, **Then** the message specifically mentions "the way you handled concurrent writes with locks is exactly how we approach distributed caching"

3. **Given** job requirements with salary range $150-200k, **When** generating email outreach, **Then** the subject line includes technical hook and body includes salary range upfront per research best practices

4. **Given** 10 shortlisted candidates, **When** generating batch outreach, **Then** each message is unique (no template feel), cliché-free, and includes personalization score

5. **Given** a generated outreach message in the UI, **When** the recruiter clicks edit, **Then** they can modify the message in-place, copy to clipboard, and regenerate if needed

6. **Given** a candidate responds positively to initial outreach, **When** recruiter requests follow-up sequence, **Then** system generates 2-3 contextual follow-up messages based on initial message and response

### Edge Cases
- What happens when a candidate has minimal enrichment data (no email, no social profiles)?
- How does the system handle candidates whose GitHub work doesn't align with job requirements?
- What happens when LLM generates a message with recruiter clichés ("passionate team", "exciting opportunity")?
- How does the system ensure salary range is always included even if job description lacks it?
- What happens when LinkedIn character limit (400 chars) cuts off important information?

## Requirements

### Functional Requirements

**Input Processing**
- **FR-001**: System MUST accept shortlisted candidate data including GitHub profile, enrichment data from Module 010 (email, LinkedIn, Twitter, blog), and ranking scores
- **FR-002**: System MUST accept job requirements including role, salary range, tech stack, company info, and key challenges
- **FR-003**: System MUST validate that minimum required data is present (GitHub username, at least one contact method, job role)
- **FR-004**: System MUST determine which channels are available (email if primary_email exists, LinkedIn if linkedin_username exists, Twitter if twitter_username exists)

**3-Stage LLM Pipeline**
- **FR-005**: **Stage 1 - Analysis**: System MUST use LLM to analyze candidate's GitHub profile and identify top 3 technical achievements, passion areas, career trajectory, and unique conversation starters
- **FR-006**: **Stage 2 - Generation**: System MUST use LLM to generate 3 message variations per available channel (email, LinkedIn, Twitter) using analysis insights
- **FR-007**: **Stage 3 - Refinement**: System MUST use LLM to validate and refine messages for quality (remove clichés, ensure specific mentions, verify CTA clarity)
- **FR-008**: System MUST track tokens and costs across all 3 stages per constitution transparency requirements

**Personalization Requirements**
- **FR-009**: System MUST include specific GitHub repository mention by name in every message (e.g., "Your redis-clone project")
- **FR-010**: System MUST include technical detail showing actual code review (e.g., "the way you handled concurrent writes with locks")
- **FR-011**: System MUST include salary range in message (email body, LinkedIn message, Twitter DM)
- **FR-012**: System MUST include tech stack clearly listed
- **FR-013**: System MUST include clear, actionable CTA (preferably Calendly link or simple yes/no question)
- **FR-014**: System MUST ensure message brevity: Email 50-125 words, LinkedIn <400 chars, Twitter <280 chars

**Multi-Channel Optimization**
- **FR-015**: **Email**: System MUST generate subject line 36-50 chars with technical hook, body with Hook → Context → Opportunity → CTA structure
- **FR-016**: **LinkedIn**: System MUST generate ultra-brief message (3-4 sentences max), lead with specific technical detail
- **FR-017**: **Twitter DM**: System MUST generate extremely brief message (2-3 sentences), focus on specific project + quick value prop
- **FR-018**: System MUST adapt tone per channel (Email: professional but conversational, LinkedIn: professional casual, Twitter: very casual)

**Quality Validation**
- **FR-019**: System MUST detect and remove recruiter clichés ("reaching out", "great opportunity", "passionate team", "exciting challenges")
- **FR-020**: System MUST detect and remove buzzwords without substance ("cutting-edge", "world-class", "innovative" without context)
- **FR-021**: System MUST validate that message references actual candidate GitHub data (not generic praise)
- **FR-022**: System MUST calculate personalization score (0-100) based on: specific repo mention (+30), technical detail (+30), unique insight (+20), enrichment data usage (+20)
- **FR-023**: System MUST flag messages below 70 personalization score for review

**Follow-up Sequences**
- **FR-024**: System MUST support generating 2-3 follow-up messages based on initial outreach and assumed no-response scenario
- **FR-025**: Follow-up 1 (Day 3): Brief reminder with additional technical insight or different repo mention
- **FR-026**: Follow-up 2 (Day 7): Different angle (career growth, technical challenge preview, team intro)
- **FR-027**: Follow-up 3 (Optional, Day 14): Final soft close with clear opt-out

**User Interface Requirements**
- **FR-028**: System MUST display generated messages in UI with edit capability (inline editing)
- **FR-029**: System MUST provide "Copy to Clipboard" button for each message
- **FR-030**: System MUST provide "Regenerate" button to generate new variation
- **FR-031**: System MUST display personalization score, referenced repos, and tokens used as metadata
- **FR-032**: System MUST save edited messages to database for tracking

**Output Format**
- **FR-033**: System MUST return structured outreach data including message text, subject line (email), personalization score, referenced elements, tokens used, channel type
- **FR-034**: System MUST include confidence score for message quality
- **FR-035**: System MUST flag messages that used fallback strategies (minimal data, generic approach)
- **FR-036**: System MUST provide explanation of personalization approach used

### Key Entities

- **OutreachMessage**: Represents a generated personalized message for a specific candidate and channel
  - Attributes:
    - `shortlist_id` (FK to shortlisted candidate)
    - `channel` (email, linkedin, twitter)
    - `subject_line` (email only, 36-50 chars)
    - `message_text` (main body, channel-specific length)
    - `personalization_score` (0-100)
    - `personalization_metadata` (PersonalizationMetadata object)
    - `tokens_used` (total across 3 stages)
    - `stage_breakdown` (tokens per stage)
    - `is_edited` (boolean, user modified)
    - `generated_at`, `edited_at`
  - Relationships: One OutreachMessage per (shortlisted_candidate, channel), references JobRequirement

- **PersonalizationMetadata**: Tracks how personalization was applied
  - Attributes:
    - `referenced_repositories` (list of repo names mentioned)
    - `technical_details_mentioned` (list of specific code/feature references)
    - `enrichment_data_used` (which fields from Module 010 were used)
    - `analysis_insights` (Stage 1 LLM output summary)
    - `cliches_removed` (list of clichés detected and removed in Stage 3)
    - `quality_flags` (list of quality issues if any)

- **FollowUpSequence**: Represents a follow-up message sequence
  - Attributes:
    - `outreach_message_id` (FK to original message)
    - `sequence_number` (1, 2, 3)
    - `scheduled_days_after` (3, 7, 14)
    - `message_text`
    - `angle` (reminder, technical_challenge, career_growth, soft_close)
    - `generated_at`

---

## Constitutional Rules

### Prompt Versioning & Auditability
- All LLM prompts MUST be versioned and logged per constitution
- Stage 1 (Analysis), Stage 2 (Generation), Stage 3 (Refinement) prompts stored separately
- Token usage tracked per stage and per message

### Quality Standards
- Personalization score >= 70 required for auto-send recommendation
- Cliché detection mandatory in Stage 3 refinement
- Salary transparency enforced (error if missing from job req)

### Response Rate Targets
- Target: 30-50% response rate (vs industry 5-12%)
- Track open rate, response rate, meeting rate per message
- A/B test subject lines, tone variations, CTA types

---

## Review & Acceptance Checklist

### Content Quality
- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

### Requirement Completeness
- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

---

## Execution Status

- [x] User description parsed
- [x] Key concepts extracted
- [x] Research completed (OUTREACH_GENERATION_RESEARCH.md)
- [x] User scenarios defined
- [x] Requirements generated
- [x] Entities identified
- [x] Review checklist passed

---

## Dependencies

### Internal Dependencies
- **Module 002 (GitHub Sourcer)**: Candidate GitHub profile data, repositories, contributions
- **Module 010 (Contact Enrichment)**: Enriched contact data (email, LinkedIn, Twitter, blog, company, hireable status)
- **Module 001 (JD Parser)**: Job requirements (role, skills, salary range, company info)
- **Shared LLM Client**: GPT-4 API integration (user has API key)

### External Dependencies
- **GPT-4 API** (OpenAI): For 3-stage LLM pipeline
- **Database**: Store outreach messages, follow-up sequences, personalization metadata

---

## Research Findings Summary

### Response Rate Impact
- Generic approach: 5-12% response rate
- High personalization: 30-50% response rate (5x improvement)
- Specific repo mentions: +500% response rate increase

### What Developers Want
- ✅ Salary transparency upfront (80-90% of recruiters hide this)
- ✅ Specific project mentions (shows actual research)
- ✅ Brief & direct (50-125 words optimal for email)
- ✅ Clear ask (no vague "let's chat")
- ✅ Technical credibility (speak like a developer, not HR)

### Multi-Channel Best Practices
- **Email**: 100 words optimal, subject 36-50 chars, send Tue-Thu 10am-12pm
- **LinkedIn**: <400 chars, lead with technical detail, include Calendly link
- **Twitter DM**: <280 chars, ultra-brief, single link CTA

---

## Next Steps

1. ✅ Spec created with research-backed requirements
2. **Create comprehensive implementation plan** → 3-stage pipeline architecture
3. **Generate detailed task list** → TDD approach with integration tests
4. **Implement Module 004** → GPT-4 powered outreach generation
