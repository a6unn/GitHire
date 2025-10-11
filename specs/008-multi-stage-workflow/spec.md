# Feature Specification: Multi-Stage Project Workflow

**Feature Branch**: `008-multi-stage-workflow`
**Created**: 2025-10-07
**Status**: Draft
**Input**: User requirement: "Redesign workflow to use project-based approach with manual shortlisting instead of automatic pipeline. User creates project → sources candidates → ranks → manually shortlists → enriches selected → generates outreach on-demand"

## Execution Flow (main)
```
1. Parse user description from Input ✓
2. Extract key concepts from description ✓
   → Identified: project-based workflow, manual control, staged progression, shortlisting, on-demand actions
3. For each unclear aspect ✓
   → Clarifications needed (see below)
4. Fill User Scenarios & Testing section ✓
5. Generate Functional Requirements ✓
6. Identify Key Entities ✓
7. Run Review Checklist
8. Return: SUCCESS (spec ready for planning)
```

---

## ⚡ Quick Guidelines
- ✅ Focus on WHAT users need and WHY
- ❌ Avoid HOW to implement (no tech stack, APIs, code structure)
- 👥 Written for business stakeholders, not developers

---

## Clarifications

### Session 2025-10-07
- Q: Should users be able to re-run sourcing or ranking if not satisfied? → A: Yes, allow re-running each stage
- Q: Can users skip enrichment and go straight to outreach? → A: Yes, enrichment is optional
- Q: Should shortlist be persistent across sessions? → A: Yes, saved in database
- Q: What happens if user closes browser during sourcing/ranking? → A: Process continues, status saved
- Q: Can users edit project name/JD after creation? → A: Not in MVP, add later

---

## User Scenarios & Testing *(mandatory)*

### Primary User Story
A recruiter wants to hire a Senior Python Developer. They create a project with the job description, let the system find GitHub candidates, review the ranked results, manually select the most promising 5-10 candidates, optionally enrich their profiles with more data, and generate personalized outreach messages only for the selected candidates.

**Example Journey**:
1. User clicks "Create Project"
2. Enters: "Senior Python Developer Search" (name), "Senior Python Developer" (title), [job description]
3. Submits → redirected to project page with status: "Draft"
4. Clicks "Find Candidates" → system sources ~25 candidates
5. Project status changes to "Sourced", candidates displayed
6. Clicks "Rank Candidates" → system scores all candidates
7. Project status changes to "Ranked", candidates sorted by score
8. User reviews scores, checks boxes next to top 8 candidates
9. Clicks "Shortlist Selected" → 8 candidates saved to shortlist
10. In shortlist view, clicks "Enrich Profile" on 2 candidates to get more details
11. Clicks "Generate Outreach" on 5 shortlisted candidates
12. Reviews, copies, and edits messages as needed
13. Marks messages as "Sent" after sending via email/LinkedIn

### Edge Cases to Test
- **Empty search results**: No candidates found during sourcing
- **All low scores**: All candidates score below 50%
- **Shortlist nothing**: User ranks but doesn't shortlist anyone
- **Re-run ranking**: User shortlists, then re-ranks (shortlist persists)
- **Delete project**: All associated data (shortlist, outreach) deleted
- **Concurrent projects**: User has multiple projects in different stages

---

## Functional Requirements *(mandatory)*

### FR-001: Project Creation
**Description**: Users must be able to create a named project with job requirements before starting the candidate search process.

**User Value**: Organizes recruitment efforts into separate projects, allows tracking multiple hiring initiatives simultaneously.

**Behavior**:
- User clicks "Create New Project" from Dashboard or Projects page
- Modal/form appears with fields:
  - Project Name (required, 1-255 characters)
  - Job Title (required, 1-255 characters)
  - Job Description (required, min 10 characters)
- System validates inputs and creates project with status "draft"
- User redirected to Project Detail page
- Project appears in Projects list

**Acceptance Criteria**:
- ✅ Project created with unique ID
- ✅ Status set to "draft" on creation
- ✅ All three fields required (validation errors shown)
- ✅ Created timestamp recorded
- ✅ Project visible in Projects list immediately

---

### FR-002: Candidate Sourcing (Stage 1)
**Description**: Within a draft project, users can trigger candidate sourcing to find ~25 GitHub developers matching the job description.

**User Value**: Automated discovery of potential candidates without manual GitHub searches.

**Behavior**:
- Project Detail page shows "Find Candidates" button (only in "draft" status)
- User clicks button → system:
  - Parses job description (Module 001)
  - Searches GitHub (Module 002)
  - Finds ~25-30 candidates
- Project status changes from "draft" → "sourced"
- Candidates displayed in table/list view with basic info:
  - GitHub username
  - Profile URL
  - Location
  - Bio
  - Repository count
  - Programming languages
- Loading indicator shown during sourcing (typically 10-30 seconds)

**Acceptance Criteria**:
- ✅ Button only visible when status = "draft"
- ✅ Sourcing can be triggered once per project (or allow re-run with confirmation)
- ✅ At least 1 candidate returned (error if 0 results)
- ✅ Status persists if browser closed during sourcing
- ✅ Candidates stored in database (not lost on refresh)

---

### FR-003: Candidate Ranking (Stage 2)
**Description**: After sourcing completes, users can trigger ranking to score all candidates from 0-100 based on job requirements.

**User Value**: Automated scoring helps prioritize candidates, saving time in manual review.

**Behavior**:
- Project Detail page shows "Rank Candidates" button (only in "sourced" status)
- User clicks button → system:
  - Runs ranking algorithm (Module 003)
  - Assigns scores to all candidates (0-100 scale)
  - Calculates score breakdown (skill match, experience, activity, domain)
- Project status changes from "sourced" → "ranked"
- Candidates re-displayed sorted by score (highest first) with:
  - Rank number (#1, #2, #3...)
  - Total score (e.g., 87.5)
  - Score breakdown bars/charts
  - Matched skills list
  - Missing skills list
  - Checkbox for shortlisting
- Loading indicator shown during ranking (typically 30-60 seconds)

**Acceptance Criteria**:
- ✅ Button only visible when status = "sourced"
- ✅ All sourced candidates receive scores
- ✅ Candidates sorted highest to lowest score
- ✅ Score breakdown displayed for each candidate
- ✅ Ranking persists across sessions

---

### FR-004: Manual Shortlisting (Stage 3)
**Description**: Users can individually shortlist/unshortlist candidates from the ranked table for further action.

**User Value**: Gives user control over which candidates to pursue, allowing quick individual selection without batch operations.

**Behavior**:
- Ranked candidates displayed in table with:
  - Name & Rank
  - Match % (sortable)
  - Skills Match %
  - Experience %
  - Activity %
  - Shortlist button ("Shortlist" / "Unshortlist")
- User clicks "Shortlist" button on individual candidate → immediately saved to shortlist
- Button changes to "Unshortlist" with different styling
- User clicks "Unshortlist" → removed from shortlist immediately
- Project status changes to "shortlisted" when first candidate shortlisted
- Shortlisted count shown in project header
- "View Shortlist" button navigates to shortlist-only page

**Acceptance Criteria**:
- ✅ Each candidate has individual shortlist button
- ✅ Shortlist/unshortlist actions immediate (no confirmation needed)
- ✅ Shortlist status persists across page refreshes
- ✅ Button visual state reflects current shortlist status
- ✅ Can shortlist/unshortlist from both "All Candidates" and "Shortlist" views
- ✅ Project status updates to "shortlisted" on first shortlist action

---

### FR-004B: Shortlist View Page
**Description**: Dedicated page showing only shortlisted candidates with actions for enrichment and outreach.

**User Value**: Focused workspace for working with selected candidates without distraction from full candidate list.

**Behavior**:
- Accessible via "View Shortlist" button on project detail page
- Shows table of only shortlisted candidates with:
  - Name & Rank
  - Match % and score breakdowns
  - Unshortlist button
  - Enrich Profile button
  - Generate Outreach button
  - Outreach status badge (if generated)
- Empty state if no candidates shortlisted yet
- "Back to All Candidates" navigation

**Acceptance Criteria**:
- ✅ Only shortlisted candidates displayed
- ✅ All enrichment and outreach actions available
- ✅ Can unshortlist from this view
- ✅ Empty state with helpful message
- ✅ Navigation between all candidates and shortlist views

---

### FR-005: Profile Enrichment (Optional, Per-Candidate)
**Description**: For shortlisted candidates, users can request additional profile data to make better decisions before outreach.

**User Value**: Provides deeper insights (recent contributions, project types, code quality) to personalize outreach or validate fit.

**Behavior**:
- In "Shortlisted" tab, each candidate card shows "Enrich Profile" button
- User clicks button → system:
  - Fetches additional GitHub data (repos, contributions, languages)
  - Analyzes code patterns and recent activity
  - Stores enriched data in database
- Button shows loading state during enrichment (5-15 seconds)
- After completion, enriched info displayed:
  - Recent projects (top 3-5 repos)
  - Contribution frequency chart
  - Skills inferred from code
  - Activity summary
- Button changes to "Re-enrich" or shows checkmark with timestamp

**Acceptance Criteria**:
- ✅ Enrichment optional (can skip and go to outreach)
- ✅ Each candidate enriched independently (not batch)
- ✅ Enriched data persists (not re-fetched on refresh)
- ✅ Shows timestamp of when enriched
- ✅ Can re-enrich to get fresh data

---

### FR-006: Outreach Generation (Per-Candidate)
**Description**: For shortlisted candidates, users can generate personalized outreach messages on-demand, one candidate at a time.

**User Value**: Saves time writing personalized messages, ensures consistent quality, allows customization before sending.

**Behavior**:
- In "Shortlisted" tab, each candidate card shows "Generate Outreach" button
- User clicks button → system:
  - Runs Module 004 (Outreach Generator) for that candidate
  - Generates personalized message based on candidate profile + job requirements
  - Stores message in database
- Message displayed in expandable section or modal:
  - Subject line
  - Message body (formatted, preserves line breaks)
  - Personalization notes (why this message was generated)
- User can:
  - Copy message to clipboard
  - Edit message inline
  - Save edited version
  - Regenerate (get new version)
  - Mark as "Sent"
- Button changes based on state:
  - "Generate Outreach" (not generated yet)
  - "View Outreach" (already generated)
  - "Sent ✓" (marked as sent)

**Acceptance Criteria**:
- ✅ Outreach generated independently for each candidate
- ✅ User can edit generated message (changes saved)
- ✅ Can regenerate if not satisfied (overwrites)
- ✅ "Mark as Sent" updates status and timestamp
- ✅ Message persists in database (visible on future visits)

---

### FR-007: Project Status Flow
**Description**: Projects progress through defined statuses that control which actions are available.

**User Value**: Clear progression prevents confusion about what step comes next.

**Status Flow**:
```
draft → sourcing → sourced → ranking → ranked → shortlisted
```

**Status Definitions**:
- **draft**: Project created, ready for candidate sourcing
- **sourcing**: Actively searching GitHub (in progress)
- **sourced**: Candidates found, ready for ranking
- **ranking**: Scoring candidates (in progress)
- **ranked**: Candidates scored, ready for shortlisting
- **shortlisted**: Candidates shortlisted, can enrich/generate outreach

**Acceptance Criteria**:
- ✅ Status transitions only allowed in correct order
- ✅ Cannot skip stages (must source before ranking)
- ✅ Status visible in project header with badge/indicator
- ✅ Projects list shows status for each project
- ✅ Can filter projects by status

---

### FR-008: Projects List Management
**Description**: Users can view all their projects, filter by status, and navigate to project details.

**User Value**: Central hub for managing multiple recruitment initiatives.

**Behavior**:
- Projects page shows table/grid of all projects with:
  - Project name
  - Job title
  - Status badge
  - Created date
  - Candidate count (if sourced)
  - Shortlist count (if shortlisted)
- Click project → navigates to Project Detail page
- Filter dropdown to show: All / Draft / Sourced / Ranked / Shortlisted
- Sort options: Newest first, Oldest first, Name A-Z
- "Create New Project" button prominently displayed
- Delete project action (with confirmation)

**Acceptance Criteria**:
- ✅ All projects visible to user (not global)
- ✅ Filters work correctly
- ✅ Pagination if >20 projects
- ✅ Delete removes project and all associated data
- ✅ Empty state shown if no projects

---

### FR-009: Remove Old Pipeline Workflow
**Description**: Current "Find Candidates" button on Dashboard that runs entire pipeline in one go must be removed.

**User Value**: Simplifies UI, enforces new project-based workflow.

**Changes**:
- Remove "Find Candidates" section from Dashboard
- Remove pipeline progress tracking from Dashboard
- Remove results display on Dashboard
- Dashboard shows: Stats overview + "Create Project" button + Recent projects list
- Projects page becomes primary entry point

**Acceptance Criteria**:
- ✅ No "Find Candidates" form on Dashboard
- ✅ Dashboard redirects to project creation flow
- ✅ Old API endpoint (`POST /pipeline/run`) deprecated (not removed yet, for backward compatibility)
- ✅ No breaking changes to existing data

---

## Key Entities *(mandatory)*

### Entity: Project
**Description**: Container for a recruitment initiative with specific job requirements.

**Key Attributes**:
- `id` - Unique identifier
- `name` - User-provided project name (e.g., "Q1 Python Hiring")
- `job_title` - Role being hired for (e.g., "Senior Python Developer")
- `job_description_text` - Full job description
- `status` - Current stage (draft, sourcing, sourced, ranking, ranked, shortlisted)
- `created_at` - When project was created
- `updated_at` - Last modification time
- `candidate_count` - Number of candidates sourced
- `shortlist_count` - Number of candidates shortlisted

**Relationships**:
- Has many: Sourced Candidates
- Has many: Shortlisted Candidates
- Has many: Outreach Messages

---

### Entity: Sourced Candidate
**Description**: GitHub developer found during sourcing stage.

**Key Attributes**:
- `project_id` - Foreign key to project
- `github_username` - Unique GitHub handle
- `profile_url` - Link to GitHub profile
- `location` - Geographic location
- `bio` - Profile bio text
- `repository_count` - Number of public repos
- `languages` - List of programming languages used
- `rank` - Position after ranking (null if not ranked yet)
- `total_score` - Overall match score 0-100 (null if not ranked yet)
- `score_breakdown` - JSON with skill match, experience, activity, domain scores

**Relationships**:
- Belongs to: Project
- May have: Shortlist entry
- May have: Outreach message

---

### Entity: Shortlisted Candidate
**Description**: Candidate manually selected by user for further action.

**Key Attributes**:
- `project_id` - Foreign key to project
- `github_username` - Foreign key to sourced candidate
- `shortlisted_at` - When added to shortlist
- `enriched_data` - JSON with additional GitHub data (nullable)
- `enrichment_status` - pending / completed / failed
- `enriched_at` - When enrichment completed

**Relationships**:
- Belongs to: Project
- References: Sourced Candidate
- May have: Outreach Message

---

### Entity: Outreach Message
**Description**: Personalized message generated for a shortlisted candidate.

**Key Attributes**:
- `project_id` - Foreign key to project
- `github_username` - Foreign key to candidate
- `subject` - Email subject line
- `message` - Generated message body
- `personalization_notes` - Explanation of personalization
- `edited_message` - User-edited version (nullable)
- `status` - draft / sent
- `sent_at` - When marked as sent
- `created_at` - When generated
- `updated_at` - Last edit time

**Relationships**:
- Belongs to: Project
- Belongs to: Shortlisted Candidate

---

## Success Criteria *(mandatory)*

### Must Have
1. ✅ User can create a project with name + job description
2. ✅ User can source candidates within a project (separate from ranking)
3. ✅ User can rank sourced candidates (separate from sourcing)
4. ✅ User can manually select candidates to shortlist
5. ✅ User can generate outreach for individual shortlisted candidates
6. ✅ All data persists across browser sessions
7. ✅ Project status flow prevents skipping stages
8. ✅ Old Dashboard pipeline workflow removed

### Should Have
1. User can re-run sourcing if not satisfied with results
2. User can remove candidates from shortlist
3. User can edit generated outreach messages
4. Projects list filterable by status

### Nice to Have
1. Enrichment data visualization (charts, timelines)
2. Export shortlist to CSV
3. Email integration (send outreach directly)
4. Collaborative projects (multiple users)

---

## Review Checklist

- [x] All FRs describe WHAT, not HOW
- [x] User value clearly stated for each FR
- [x] Edge cases identified in testing scenarios
- [x] Key entities and relationships defined
- [x] No technical implementation details
- [x] Success criteria measurable
- [x] Clarifications documented

**Status**: ✅ Ready for Planning (`/plan`)
