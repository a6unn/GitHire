"""
Generation Prompt Templates for Stage 2 (Multi-Channel Message Generation)

This module provides LLM prompts for generating outreach messages across different channels.
Uses insights from Stage 1 analysis to create personalized, channel-specific messages.
"""

from typing import Any


def build_email_prompt(insights: dict, job_req: dict, enrichment: dict, candidate: dict = None) -> str:
    """
    Build the email generation prompt for Stage 2.

    This prompt instructs GPT-4 to generate a personalized recruiting email
    using insights from Stage 1 analysis.

    Args:
        insights: Analysis insights from Stage 1 (achievements, passion_areas, conversation_starters, etc.)
        job_req: Job requirements (role, skills, company, salary_range, tech_stack)
        enrichment: Enriched contact data (email, linkedin, company, etc.)
        candidate: Candidate data including name and username (optional)

    Returns:
        Formatted prompt string for GPT-4

    Example:
        >>> prompt = build_email_prompt(insights, job_req, enrichment, candidate)
        >>> response = llm_client.complete(prompt)  # Returns JSON with subject_line and body
    """
    # Extract insights
    achievements = insights.get("achievements", [])
    passion_areas = insights.get("passion_areas", [])
    career_trajectory = insights.get("career_trajectory", "")
    conversation_starters = insights.get("conversation_starters", [])
    minimal_data = insights.get("minimal_data_fallback", False)

    # Extract candidate info
    candidate_name = None
    if candidate:
        # Try to get name from candidate data (could be full name or first name)
        candidate_name = candidate.get("name") or candidate.get("first_name")
        if not candidate_name:
            # Fall back to username as a friendly greeting
            github_username = candidate.get("github_username") or candidate.get("username")
            if github_username:
                candidate_name = github_username

    # Extract job requirements
    role = job_req.get("role_type", "Software Engineer")
    company_name = job_req.get("company_name", "Our Company")
    salary_range = job_req.get("salary_range", "Competitive salary")
    required_skills = job_req.get("required_skills", [])
    experience_level = job_req.get("experience_level", "Mid-level")

    # Extract enrichment data
    current_company = enrichment.get("company", "current company")

    # Format achievements and starters
    achievements_str = "\n".join(f"  - {a}" for a in achievements[:3])
    starters_str = "\n".join(f"  - {s}" for s in conversation_starters[:3])
    passion_str = ", ".join(passion_areas[:3])

    # Add candidate name instruction if available
    name_instruction = ""
    name_example = ""
    if candidate_name:
        name_instruction = f"\n- Candidate's Name: {candidate_name} (MUST use this name in greeting)"
        name_example = f"Hi {candidate_name}, "
    else:
        name_example = "Hi, "

    prompt = f"""You are an empathetic technical recruiter who writes like a developer, not a salesperson. Your goal is to craft a personalized recruiting email that respects the candidate's time and demonstrates genuine research.

**Candidate Insights (from deep profile analysis):**{name_instruction}
- Top Achievements:
{achievements_str}
- Passion Areas: {passion_str}
- Career Stage: {career_trajectory}
- Conversation Starters:
{starters_str}
- Minimal Data Scenario: {minimal_data}

**Job Opportunity:**
- Role: {role}
- Company: {company_name}
- Experience Level: {experience_level}
- Required Skills: {", ".join(required_skills[:5]) if required_skills else "Not specified"}
- Salary Range: {salary_range}
- Current Company: {current_company}

**Email Constraints:**
- Subject line: 36-50 characters (CRITICAL: must be within this range)
- Body: 50-125 words (CRITICAL: must be within this range)
- Structure: Hook (conversation starter) to Context (why this role) to Opportunity (salary, role, tech) to CTA (Calendly link or meeting request)

**Required Elements:**
1. Specific repository or project mention by name (from achievements or starters)
2. Technical detail showing you reviewed their code (implementation detail, architecture choice, etc.)
3. Salary range explicitly stated (no hiding compensation)
4. Clear CTA with action (e.g., "chat", "discuss", "schedule a call")

**Forbidden Phrases (DO NOT USE):**
- "reaching out"
- "great opportunity"
- "passionate team"
- "exciting challenges"
- "cutting-edge" (without specific context)
- "touching base"
- "circle back"
- "thought leader"

**Tone Guidelines:**
- Write like a developer who respects other developers' time
- Be specific, not generic
- Be brief, not wordy
- Be honest, not salesy
- Use technical language naturally (not buzzwords)

**Example Good Email:**

Subject: Redis expertise needed for distributed systems role
Body: {name_example}I noticed your redis-clone project's concurrent write handling with locks - that's exactly the approach we're taking for our caching layer at DataCorp. We're building a real-time analytics platform processing 10M events/sec and need someone with your distributed systems expertise. Senior Backend Engineer role, $150k-$200k, fully remote. Interested in a quick chat this week? Here's my Calendly: https://calendly.com/recruiter

(This example: 75 words, mentions specific repo, shows code review, includes salary, has clear CTA)

**Your Task:**
Generate a recruiting email for the candidate using the insights above. Return ONLY a valid JSON object with this exact structure:

{{
    "subject_line": "36-50 character subject line here",
    "body": "50-125 word email body with Hook, Context, Opportunity, and CTA"
}}

**Important:**
- {"Start with greeting using candidate's name: " + candidate_name if candidate_name else "Start with a friendly greeting"}
- Ensure subject line is 36-50 characters (count carefully!)
- Ensure body is 50-125 words (count carefully!)
- Include specific repo/project name from achievements
- Include technical detail from their work
- Include salary range explicitly
- End with clear CTA
- DO NOT use forbidden phrases

Generate the email now:"""

    return prompt


def build_linkedin_prompt(insights: dict, job_req: dict, enrichment: dict, candidate: dict = None) -> str:
    """
    Build the LinkedIn generation prompt for Stage 2.

    This prompt instructs GPT-4 to generate a brief, professional-casual
    LinkedIn message using insights from Stage 1 analysis.

    Args:
        insights: Analysis insights from Stage 1
        job_req: Job requirements
        enrichment: Enriched contact data
        candidate: Candidate data including name and username (optional)

    Returns:
        Formatted prompt string for GPT-4
    """
    # Extract insights
    conversation_starters = insights.get("conversation_starters", [])
    achievements = insights.get("achievements", [])

    # Extract candidate info
    candidate_name = None
    if candidate:
        # Try to get name from candidate data (could be full name or first name)
        candidate_name = candidate.get("name") or candidate.get("first_name")
        if not candidate_name:
            # Fall back to username as a friendly greeting
            github_username = candidate.get("github_username") or candidate.get("username")
            if github_username:
                candidate_name = github_username

    # Extract job requirements
    role = job_req.get("role_type", "Software Engineer")
    company_name = job_req.get("company_name", "Our Company")
    salary_range = job_req.get("salary_range", "Competitive salary")

    # Format first starter and achievement
    starter = conversation_starters[0] if conversation_starters else "your GitHub work"
    achievement = achievements[0] if achievements else "your technical background"

    # Add candidate name instruction if available
    name_instruction = ""
    name_example = ""
    if candidate_name:
        name_instruction = f"\n- Candidate's Name: {candidate_name} (MUST use this name in greeting)"
        name_example = f"Hi {candidate_name}! "
    else:
        name_example = ""

    prompt = f"""You are a technical recruiter crafting a brief LinkedIn message to a developer.

**Candidate Context:**{name_instruction}
- Top Achievement: {achievement}
- Best Conversation Starter: {starter}

**Job Opportunity:**
- Role: {role}
- Company: {company_name}
- Salary: {salary_range}

**LinkedIn Message Constraints:**
- Total length: <400 characters (CRITICAL: must be under 400 chars)
- Sentences: 3-4 sentences (use periods, exclamation marks, or question marks)
- Tone: Professional casual (like a developer reaching out to another developer)

**Required Elements:**
1. Lead with specific technical detail (repo name or feature from achievement)
2. Connect to job role
3. Include salary range explicitly
4. End with Calendly link or clear CTA

**Forbidden Phrases:**
- "reaching out", "great opportunity", "passionate team", "exciting challenges"

**Example Good LinkedIn Message:**

"{name_example}Loved your redis-clone's concurrent write implementation! We're building a similar distributed system at DataCorp and need that expertise. Senior Backend Engineer, $150k-$200k, remote. Quick chat? https://calendly.com/recruiter"

(This example: 210 chars, 4 sentences, specific mention, salary included, clear CTA)

**Your Task:**
Generate a LinkedIn message using the context above. Return ONLY a valid JSON object:

{{
    "message": "<400 character LinkedIn message with 3-4 sentences"
}}

**Important:**
- {f"Start with greeting using candidate's name: {candidate_name}" if candidate_name else "Start with a friendly greeting"}
- Total length MUST be <400 characters (count carefully!)
- Use 3-4 sentences (end with . ! or ?)
- Include specific repo or technical detail
- Include salary range
- End with CTA

Generate the LinkedIn message now:"""

    return prompt


def build_twitter_prompt(insights: dict, job_req: dict, enrichment: dict, candidate: dict = None) -> str:
    """
    Build the Twitter generation prompt for Stage 2.

    This prompt instructs GPT-4 to generate a very brief, casual
    Twitter message using insights from Stage 1 analysis.

    Args:
        insights: Analysis insights from Stage 1
        job_req: Job requirements
        enrichment: Enriched contact data
        candidate: Candidate data including name and username (optional)

    Returns:
        Formatted prompt string for GPT-4
    """
    # Extract insights
    conversation_starters = insights.get("conversation_starters", [])
    achievements = insights.get("achievements", [])

    # Extract candidate info
    candidate_name = None
    if candidate:
        # Try to get name from candidate data (could be full name or first name)
        candidate_name = candidate.get("name") or candidate.get("first_name")
        if not candidate_name:
            # Fall back to username as a friendly greeting
            github_username = candidate.get("github_username") or candidate.get("username")
            if github_username:
                candidate_name = github_username

    # Extract job requirements
    role = job_req.get("role_type", "Software Engineer")
    company_name = job_req.get("company_name", "Our Company")
    salary_range = job_req.get("salary_range", "Competitive")

    # Format first starter and achievement
    starter = conversation_starters[0] if conversation_starters else "your work"
    achievement = achievements[0] if achievements else "your code"

    # Add candidate name instruction if available
    name_instruction = ""
    name_example = ""
    if candidate_name:
        name_instruction = f"\n- Candidate's Name: {candidate_name} (can use in greeting if space allows)"
        name_example = f"Hey {candidate_name}! "
    else:
        name_example = ""

    prompt = f"""You are a technical recruiter crafting a very brief Twitter DM to a developer.

**Candidate Context:**{name_instruction}
- Achievement: {achievement}
- Starter: {starter}

**Job:**
- Role: {role}
- Company: {company_name}
- Salary: {salary_range}

**Twitter Constraints:**
- Total length: <280 characters (CRITICAL)
- Sentences: 2-3 sentences (very brief!)
- Tone: Very casual (like a friendly developer)

**Required:**
1. Specific project mention
2. Role + salary
3. Link or CTA

**Forbidden:**
- "reaching out", "great opportunity", no recruiter buzzwords

**Example:**

"{name_example}Loved your redis-clone! We're hiring for distributed systems at DataCorp. Senior Backend, $150k. Interested? https://calendly.com/me"

(150 chars, 3 sentences, specific, salary, CTA)

**Task:**
Generate Twitter message. Return JSON:

{{
    "message": "<280 char Twitter DM with 2-3 sentences"
}}

**Important:**
- {f"Can include candidate's name ({candidate_name}) if space allows" if candidate_name else "Start with a friendly greeting"}
- Keep it very brief and casual
- Must be <280 characters

Generate now:"""

    return prompt
