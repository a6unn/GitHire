"""
Follow-Up Prompt Templates

This module provides LLM prompts for generating follow-up messages
with different angles: reminder, technical_challenge, career_growth, soft_close.

Research shows that 2-3 follow-ups increase response rates by 50-80%.
Each follow-up uses a different angle to maintain engagement without being pushy.
"""

from typing import Any


def build_followup_prompt(
    original_message: str,
    job_req: dict,
    candidate: dict,
    sequence_num: int,
    angle: str
) -> str:
    """
    Build follow-up prompt for LLM.

    Generates a prompt based on the follow-up angle:
    - "reminder": Brief reminder + different repo mention
    - "technical_challenge": Preview actual technical problem from role
    - "career_growth": Emphasize career progression opportunity
    - "soft_close": Final gentle close with opt-out

    Args:
        original_message: Original outreach message text
        job_req: Job requirements (role, company, tech_stack, etc.)
        candidate: Candidate data (username, top_repos, etc.)
        sequence_num: Sequence number (1-3)
        angle: Follow-up angle ("reminder", "technical_challenge", "career_growth", "soft_close")

    Returns:
        Formatted prompt string for LLM

    Example:
        >>> prompt = build_followup_prompt(original_msg, job_req, candidate, 1, "reminder")
        >>> response = llm_client.complete(prompt)  # Returns follow-up message
    """
    # Extract data
    username = candidate.get("github_username", "")
    name = candidate.get("name", username)
    top_repos = candidate.get("top_repos", [])
    role_type = job_req.get("role_type", "Engineer")
    company_name = job_req.get("company_name", "our company")
    salary_range = job_req.get("salary_range", "")
    tech_stack = job_req.get("tech_stack", [])

    # Format repo names
    repo_names = [repo.get("name", "") for repo in top_repos[:5]]
    repo_names_str = ", ".join(repo_names) if repo_names else "No repos available"

    # Build angle-specific prompt
    if angle == "reminder":
        return _build_reminder_prompt(
            name, original_message, repo_names_str, role_type, company_name, salary_range
        )
    elif angle == "technical_challenge":
        return _build_technical_challenge_prompt(
            name, original_message, role_type, company_name, tech_stack, salary_range
        )
    elif angle == "career_growth":
        return _build_career_growth_prompt(
            name, original_message, role_type, company_name, salary_range
        )
    elif angle == "soft_close":
        return _build_soft_close_prompt(
            name, original_message, role_type, company_name
        )
    else:
        # Default to reminder
        return _build_reminder_prompt(
            name, original_message, repo_names_str, role_type, company_name, salary_range
        )


def _build_reminder_prompt(
    name: str,
    original_message: str,
    repo_names: str,
    role_type: str,
    company_name: str,
    salary_range: str
) -> str:
    """Build prompt for Day 3 reminder follow-up."""
    return f"""You are a technical recruiter writing a brief follow-up to an initial outreach message.

**Original Message Sent 3 Days Ago:**
{original_message}

**Candidate Context:**
- Name: {name}
- Top Repositories: {repo_names}

**Job Context:**
- Role: {role_type}
- Company: {company_name}
- Salary: {salary_range}

**Your Task:**
Write a BRIEF follow-up message (Day 3 reminder). This is a gentle nudge, NOT a sales pitch.

**Requirements:**
1. **Very Brief**: 2-3 sentences maximum (30-50 words)
2. **Different Repo**: Mention a DIFFERENT repository than the original message
   - Original message repos: {repo_names}
   - Pick a different one or mention a different aspect
3. **No Pressure**: Acknowledge they're busy, no pushy language
4. **Simple CTA**: Just a yes/no question ("Interested?" or "Worth a chat?")

**Forbidden Phrases:**
- "Just following up"
- "Circling back"
- "Touching base"
- "Any thoughts?"
- "Did you get my previous email?"

**Good Examples:**

Example 1:
"Hi {name}, saw your async-patterns library too - clean abstraction design. Still exploring the {role_type} role ({salary_range})? Quick chat this week?"

Example 2:
"Quick follow-up: your WebSocket server project caught my eye as well. {role_type} at {company_name} still interesting? Happy to share details."

**Now write the Day 3 reminder follow-up:**
"""


def _build_technical_challenge_prompt(
    name: str,
    original_message: str,
    role_type: str,
    company_name: str,
    tech_stack: list[str],
    salary_range: str
) -> str:
    """Build prompt for Day 7 technical challenge follow-up."""
    tech_stack_str = ", ".join(tech_stack[:3]) if tech_stack else "our tech stack"

    return f"""You are a technical recruiter writing a Day 7 follow-up with a technical challenge preview.

**Original Message Sent 7 Days Ago:**
{original_message}

**Candidate Context:**
- Name: {name}

**Job Context:**
- Role: {role_type}
- Company: {company_name}
- Tech Stack: {tech_stack_str}
- Salary: {salary_range}

**Your Task:**
Write a follow-up that previews an ACTUAL technical challenge the candidate would work on.
This gives them a taste of the work and shows respect for their technical expertise.

**Requirements:**
1. **Brief**: 3-4 sentences (50-75 words)
2. **Specific Technical Problem**: Describe a real technical challenge using {tech_stack_str}
   - Example: "We're optimizing query latency for 100M+ events/day - need distributed caching expertise"
   - Example: "Building real-time conflict resolution for collaborative editing - complex CRDT work"
3. **Honest About Difficulty**: Acknowledge it's a hard problem
4. **CTA**: Offer to discuss the problem, not just "the role"

**Good Example:**

"Hi {name}, thought you'd find this interesting: we're wrestling with distributed lock management across 20+ Redis instances (handling 10M writes/sec). Classic thundering herd problem. Your redis-clone experience seems directly applicable. Want to discuss our approach? {salary_range} + equity."

**Now write the Day 7 technical challenge follow-up:**
"""


def _build_career_growth_prompt(
    name: str,
    original_message: str,
    role_type: str,
    company_name: str,
    salary_range: str
) -> str:
    """Build prompt for career growth follow-up (alternative to technical challenge)."""
    return f"""You are a technical recruiter writing a follow-up emphasizing career progression.

**Original Message Sent:**
{original_message}

**Candidate Context:**
- Name: {name}

**Job Context:**
- Role: {role_type}
- Company: {company_name}
- Salary: {salary_range}

**Your Task:**
Write a follow-up emphasizing career growth and impact potential.

**Requirements:**
1. **Brief**: 3-4 sentences (50-70 words)
2. **Growth Path**: Mention concrete progression (Senior → Staff → Principal)
3. **Impact**: Quantify scope of impact (team size, users, revenue, scale)
4. **Autonomy**: Mention ownership and decision-making authority

**Good Example:**

"Hi {name}, quick note on growth: this {role_type} role has clear path to Staff in 12-18 months (we just promoted two engineers). You'd own architecture decisions for our API serving 50M requests/day. {salary_range} + equity. Still interested in learning more?"

**Now write the career growth follow-up:**
"""


def _build_soft_close_prompt(
    name: str,
    original_message: str,
    role_type: str,
    company_name: str
) -> str:
    """Build prompt for Day 14 soft close follow-up."""
    return f"""You are a technical recruiter writing a final follow-up (Day 14 soft close).

**Original Message Sent 14 Days Ago:**
{original_message}

**Candidate Context:**
- Name: {name}

**Job Context:**
- Role: {role_type}
- Company: {company_name}

**Your Task:**
Write a final, gentle close that gives the candidate a clear opt-out.
This shows respect for their time and maintains goodwill.

**Requirements:**
1. **Very Brief**: 2-3 sentences (30-45 words)
2. **Acknowledge Silence**: Assume they're not interested, that's okay
3. **Explicit Opt-Out**: Make it easy to say no
4. **Leave Door Open**: For future opportunities
5. **No Guilt**: No "last chance" or "opportunity won't last" pressure

**Forbidden Phrases:**
- "Last chance"
- "Opportunity is closing"
- "Really want to connect"
- "Final follow-up"

**Good Examples:**

Example 1:
"Hi {name}, assuming the {role_type} role isn't a fit right now - no worries! If you'd like me to stop reaching out, just let me know. Otherwise, I'll keep you in mind for future roles. Cheers."

Example 2:
"Hey {name}, I'll assume you're not interested in the {company_name} role (totally fine!). Reply 'no thanks' if you'd prefer I don't reach out again. Otherwise, happy to stay in touch for future opportunities."

Example 3:
"Quick note: if the {role_type} role isn't interesting, no problem at all. Just reply 'pass' and I'll remove you from my list. Otherwise, door's open if you ever want to chat. Best of luck!"

**Now write the Day 14 soft close follow-up:**
"""
