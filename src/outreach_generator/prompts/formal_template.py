"""Formal tone prompt template for professional outreach messages."""


def build_formal_prompt(
    candidate_name: str,
    candidate_username: str,
    candidate_bio: str,
    job_role: str,
    job_skills: list[str],
    relevant_repos: list[dict],
    depth: str
) -> str:
    """
    Build formal prompt for LLM to generate professional outreach message.

    Args:
        candidate_name: Candidate's display name (or username if no name)
        candidate_username: GitHub username
        candidate_bio: Candidate's bio (may be empty)
        job_role: Job title/role
        job_skills: List of required skills
        relevant_repos: List of repo dicts with name, description, stars
        depth: Personalization depth ("deep", "medium", "surface")

    Returns:
        Formatted prompt string for LLM
    """
    # Depth instructions
    depth_instructions = {
        "deep": (
            "Provide detailed analysis of their work. Reference specific projects, "
            "analyze technical choices, and connect their experience to the role requirements. "
            "Make it clear you've thoroughly reviewed their profile. Target 150-200 words."
        ),
        "medium": (
            "Reference 1-2 specific projects and explain how they relate to the role. "
            "Keep it professional but concise. Target 100-150 words."
        ),
        "surface": (
            "Mention their GitHub presence and general technical background. "
            "Focus on the opportunity rather than deep technical analysis. Target 80-120 words."
        )
    }

    # Build repos section
    repos_text = ""
    if relevant_repos:
        repos_text = "\n\nCandidate's Relevant Repositories:\n"
        for repo in relevant_repos[:3]:  # Max 3 repos
            repos_text += f"- **{repo['name']}** ({repo['stars']} stars): {repo['description']}\n"
    else:
        repos_text = "\n\nNote: Candidate has minimal public repository activity. Focus on potential and transferable skills.\n"

    # Build bio section
    bio_text = f"\\nCandidate Bio: {candidate_bio}" if candidate_bio else ""

    prompt = f'''You are a professional technical recruiter writing personalized outreach messages to GitHub developers.

Candidate Information:
- Name: {candidate_name}
- GitHub: @{candidate_username}{bio_text}{repos_text}

Job Role: {job_role}
Required Skills: {", ".join(job_skills)}

Task: Write a professional outreach message to this candidate about the {job_role} position.

Requirements:
- Use formal, professional tone
- Structure: Brief introduction → Technical fit (reference their work) → Opportunity description → Clear next steps
- {depth_instructions.get(depth, depth_instructions["medium"])}
- Be authentic - only reference actual projects/skills from their profile
- Never make false claims about their experience
- Include a clear call-to-action
- Start directly with the message (no subject line)
- DO NOT use placeholder brackets like [Your Name] or [Company] - write a complete message

Message:'''

    return prompt
