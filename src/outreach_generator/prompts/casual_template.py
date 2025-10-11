"""Casual tone prompt template for friendly outreach messages."""


def build_casual_prompt(
    candidate_name: str,
    candidate_username: str,
    candidate_bio: str,
    job_role: str,
    job_skills: list[str],
    relevant_repos: list[dict],
    depth: str
) -> str:
    """
    Build casual prompt for LLM to generate friendly outreach message.

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
            "Reference multiple projects and get into the technical details. "
            "Show genuine interest in their work and explain why it caught your attention. "
            "Make it conversational but substantial. Target 150-200 words."
        ),
        "medium": (
            "Mention 1-2 specific projects in a friendly way. "
            "Keep it conversational and approachable. Target 100-150 words."
        ),
        "surface": (
            "Keep it brief and friendly. Mention their GitHub presence and express interest. "
            "Target 80-120 words."
        )
    }

    # Build repos section
    repos_text = ""
    if relevant_repos:
        repos_text = "\n\nCandidate's Relevant Repositories:\n"
        for repo in relevant_repos[:3]:  # Max 3 repos
            repos_text += f"- **{repo['name']}** ({repo['stars']} stars): {repo['description']}\n"
    else:
        repos_text = "\n\nNote: Candidate has minimal public repository activity. Focus on their potential and interest in the role.\n"

    # Build bio section
    bio_text = f"\\nCandidate Bio: {candidate_bio}" if candidate_bio else ""

    prompt = f'''You are a friendly technical recruiter writing personalized, conversational outreach messages to GitHub developers.

Candidate Information:
- Name: {candidate_name}
- GitHub: @{candidate_username}{bio_text}{repos_text}

Job Role: {job_role}
Required Skills: {", ".join(job_skills)}

Task: Write a casual, friendly outreach message to this candidate about the {job_role} position.

Requirements:
- Use casual, conversational tone (but still professional - no slang)
- Be personable and approachable
- {depth_instructions.get(depth, depth_instructions["medium"])}
- Reference their actual work naturally in conversation
- Never make false claims about their experience
- Include a friendly call-to-action
- Start directly with the message (no subject line)
- DO NOT use placeholder brackets like [Your Name] or [Company] - write a complete message

Message:'''

    return prompt
