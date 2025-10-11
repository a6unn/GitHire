"""
Analysis Prompt Template for Stage 1 (Deep GitHub Profile Analysis)

This module provides the LLM prompt for analyzing GitHub candidate profiles
to extract personalization insights for outreach generation.
"""

from typing import Any


def build_analysis_prompt(candidate: dict, enrichment: dict, job_req: dict) -> str:
    """
    Build the analysis prompt for Stage 1 (Deep GitHub Profile Analysis).

    This prompt instructs GPT-4 to analyze a candidate's GitHub profile and
    identify key personalization points for outreach messages.

    Args:
        candidate: Candidate data from GitHub (username, name, bio, repos, languages, etc.)
        enrichment: Enriched contact data from Module 010 (email, linkedin, twitter, blog, company)
        job_req: Job requirements (role, skills, experience, company, salary_range, tech_stack)

    Returns:
        Formatted prompt string for GPT-4

    Example:
        >>> prompt = build_analysis_prompt(candidate, enrichment, job_req)
        >>> response = llm_client.chat(prompt)  # Returns structured JSON insights
    """

    # Extract candidate data
    username = candidate.get("github_username", "")
    name = candidate.get("name", username)
    bio = candidate.get("bio", "No bio available")
    location = candidate.get("location", "Location not specified")
    top_repos = candidate.get("top_repos", [])
    languages = candidate.get("languages", [])
    total_repos = candidate.get("total_repos", 0)
    contribution_count = candidate.get("contribution_count", 0)

    # Extract enrichment data
    email = enrichment.get("primary_email")
    linkedin = enrichment.get("linkedin_username")
    twitter = enrichment.get("twitter_username")
    blog = enrichment.get("blog_url")
    company = enrichment.get("company")
    hireable = enrichment.get("hireable")

    # Extract job requirements
    role = job_req.get("role_type", "Software Engineer")
    required_skills = job_req.get("required_skills", [])
    experience_level = job_req.get("experience_level", "Mid-level")
    company_name = job_req.get("company_name", "Our Company")
    salary_range = job_req.get("salary_range", "Competitive salary")
    tech_stack = job_req.get("tech_stack", [])

    # Format repositories for context
    repos_context = ""
    if top_repos:
        repos_context = "Top Repositories:\n"
        for i, repo in enumerate(top_repos[:5], 1):  # Top 5 repos
            repo_name = repo.get("name", "Unknown")
            repo_desc = repo.get("description", "No description")
            repo_lang = repo.get("language", "Unknown")
            repo_stars = repo.get("stars", 0)
            repos_context += f"{i}. **{repo_name}** ({repo_lang}, stars: {repo_stars})\n   {repo_desc}\n"
    else:
        repos_context = "No repositories available (minimal data scenario)"

    # Format languages
    languages_str = ", ".join(languages[:5]) if languages else "Not specified"

    # Format enrichment summary
    enrichment_summary = []
    if email:
        enrichment_summary.append(f"Email: {email}")
    if linkedin:
        enrichment_summary.append(f"LinkedIn: linkedin.com/in/{linkedin}")
    if twitter:
        enrichment_summary.append(f"Twitter: @{twitter}")
    if blog:
        enrichment_summary.append(f"Blog: {blog}")
    if company:
        enrichment_summary.append(f"Current Company: {company}")
    if hireable is not None:
        enrichment_summary.append(f"Hireable: {hireable}")

    enrichment_context = "\n".join(enrichment_summary) if enrichment_summary else "No enrichment data available"

    # Build the prompt
    prompt = f"""You are a technical recruiting researcher with 10 years of experience analyzing GitHub profiles to identify personalization opportunities for developer outreach.

**Your Mission:**
Deeply analyze this candidate's GitHub profile and identify the most compelling personalization points for recruiting outreach. Focus on specific, actionable insights that will make a recruiter's message stand out.

**Candidate Profile:**
- GitHub Username: {username}
- Name: {name}
- Bio: {bio}
- Location: {location}
- Total Repositories: {total_repos}
- Total Contributions: {contribution_count}
- Programming Languages: {languages_str}

{repos_context}

**Enrichment Data:**
{enrichment_context}

**Job Opportunity:**
- Role: {role}
- Company: {company_name}
- Experience Level: {experience_level}
- Required Skills: {", ".join(required_skills[:5]) if required_skills else "Not specified"}
- Tech Stack: {", ".join(tech_stack[:5]) if tech_stack else "Not specified"}
- Salary Range: {salary_range}

**Analysis Task:**
Analyze this candidate and provide structured insights in JSON format with the following fields:

1. **achievements** (list of 3 strings): Identify the candidate's top 3 technical achievements based on their GitHub activity. Be specific - mention actual repos, features they built, or technical challenges they solved. Focus on achievements relevant to the job opportunity.

2. **passion_areas** (list of strings): What technical domains or technologies is this candidate passionate about? Look at their repo topics, language preferences, and project types.

3. **career_trajectory** (string): Based on their work, what is their likely career trajectory? Are they junior to mid? Mid to senior? Senior to staff? Be realistic based on repo complexity and contribution patterns.

4. **conversation_starters** (list of 3 strings): Identify 3 specific, unique conversation starters that would grab this candidate's attention. These should reference specific repos, technical implementations, or insights NOT found on a typical resume. Make them technical and specific.

5. **minimal_data_fallback** (boolean): Is this a minimal data scenario (< 3 repos or low activity)? If true, focus conversation starters on potential rather than past work.

**Important Guidelines:**
- Be SPECIFIC: Instead of "impressive work", say "Your redis-clone implementation's handling of concurrent writes with locks"
- Be RELEVANT: Connect achievements to the job opportunity when possible
- Be REALISTIC: Don't oversell or make false claims
- Be UNIQUE: Find insights that aren't on LinkedIn or a resume
- If minimal data (< 3 repos), set minimal_data_fallback: true and focus on potential/interests

**Output Format:**
Return ONLY a valid JSON object with this exact structure:
{{
    "achievements": [
        "Specific achievement 1 with repo name",
        "Specific achievement 2 with repo name",
        "Specific achievement 3 with repo name"
    ],
    "passion_areas": ["Domain 1", "Domain 2", "Domain 3"],
    "career_trajectory": "Current level to Next level path",
    "conversation_starters": [
        "Specific technical detail from repo 1",
        "Specific technical detail from repo 2",
        "Specific technical detail from repo 3"
    ],
    "minimal_data_fallback": false
}}

**Example Good Output:**
{{
    "achievements": [
        "Built redis-clone with 1.2k stars implementing distributed caching with concurrent write handling",
        "Contributed async/await patterns to popular Python library with 50+ merged PRs",
        "Created real-time WebSocket server handling 10k+ concurrent connections"
    ],
    "passion_areas": ["Systems Programming", "Distributed Systems", "Performance Optimization"],
    "career_trajectory": "Senior to Staff Engineer path based on system design complexity",
    "conversation_starters": [
        "Your redis-clone's concurrent write locks implementation is exactly how we approach caching at {company_name}",
        "Noticed your async-patterns repo - we're solving similar concurrency challenges with 10M+ events/sec",
        "The WebSocket server you built handles connections at scale we're targeting for our real-time platform"
    ],
    "minimal_data_fallback": false
}}

Now analyze the candidate profile above and return the JSON analysis:"""

    return prompt


def build_minimal_data_fallback_prompt(candidate: dict, enrichment: dict, job_req: dict) -> str:
    """
    Build a fallback analysis prompt for candidates with minimal GitHub data.

    Used when candidate has < 3 repos or very low activity. Focuses on potential
    rather than past achievements.

    Args:
        candidate: Candidate data (may be minimal)
        enrichment: Enriched contact data
        job_req: Job requirements

    Returns:
        Fallback prompt focused on potential and interests
    """

    username = candidate.get("github_username", "")
    name = candidate.get("name", username)
    bio = candidate.get("bio", "No bio available")
    languages = candidate.get("languages", [])

    role = job_req.get("role_type", "Software Engineer")
    company_name = job_req.get("company_name", "Our Company")

    languages_str = ", ".join(languages[:3]) if languages else "Not specified"

    prompt = f"""You are a technical recruiting researcher analyzing a candidate with minimal public GitHub activity.

**Candidate Profile:**
- Username: {username}
- Name: {name}
- Bio: {bio}
- Languages: {languages_str}

**Job Opportunity:**
- Role: {role}
- Company: {company_name}

**Task:**
This candidate has minimal public GitHub data. Focus your analysis on POTENTIAL and INTERESTS rather than achievements.

Return JSON with:
{{
    "achievements": [
        "Focus on potential based on bio/interests",
        "Mention any visible language skills",
        "Emphasize growth opportunity at {company_name}"
    ],
    "passion_areas": ["Infer from bio or default to job tech stack"],
    "career_trajectory": "Early career or transitioning - emphasize learning opportunity",
    "conversation_starters": [
        "Reference their stated interests from bio",
        "Mention learning opportunities in the role",
        "Focus on company culture and mentorship"
    ],
    "minimal_data_fallback": true
}}

Return the JSON analysis:"""

    return prompt
