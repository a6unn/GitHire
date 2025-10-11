"""
Refinement Prompt Template for Stage 3 (Quality Validation)

This module provides the LLM prompt for refining and polishing outreach messages
to remove clichés, verify specifics, and ensure quality.
"""

from typing import Any


def build_refinement_prompt(
    message: str,
    candidate: dict,
    detected_cliches: list[str]
) -> str:
    """
    Build the refinement prompt for Stage 3 (Quality Validation).

    This prompt instructs GPT-4 to review and refine a generated message,
    removing clichés and ensuring personalization quality.

    Args:
        message: Original message text to refine
        candidate: Candidate data (for verifying repo mentions)
        detected_cliches: List of clichés detected in the message

    Returns:
        Formatted prompt string for GPT-4

    Example:
        >>> prompt = build_refinement_prompt(message, candidate, ["reaching out"])
        >>> response = llm_client.complete(prompt)  # Returns refined message
    """
    # Extract candidate data
    username = candidate.get("github_username", "")
    top_repos = candidate.get("top_repos", [])

    # Format repo names for verification
    repo_names = [repo.get("name", "") for repo in top_repos[:3]]
    repo_names_str = ", ".join(repo_names) if repo_names else "No repos available"

    # Format detected clichés
    cliches_str = ", ".join(detected_cliches) if detected_cliches else "None detected"

    prompt = f"""You are a quality assurance specialist for recruiting messages. Your job is to review and refine outreach messages to ensure they are personalized, authentic, and free of recruiter clichés.

**Original Message to Review:**
{message}

**Candidate Context:**
- GitHub Username: {username}
- Top Repositories: {repo_names_str}

**Detected Clichés (MUST REMOVE):**
{cliches_str}

**Your Refinement Task:**

1. **Remove Clichés**: If any clichés were detected, remove them and replace with more authentic phrasing
   - Instead of "reaching out", use "contacting you" or just remove
   - Instead of "great opportunity", use "opportunity" or be more specific
   - Instead of "passionate team", describe the actual team or remove

2. **Verify Specific Mentions**: Ensure at least ONE specific repository is mentioned by name
   - If no repo is mentioned, this is a RED FLAG - the message is too generic
   - Repo names from candidate: {repo_names_str}

3. **Verify Technical Details**: Ensure the message shows actual code review
   - Should mention specific features, architecture choices, or implementation details
   - Generic phrases like "impressive work" are NOT sufficient

4. **Verify CTA Clarity**: Ensure the call-to-action is clear
   - Should have action words: "chat", "discuss", "schedule", "call"
   - Should have a link or clear next step

5. **Polish for Authenticity**: Make the message sound like a developer wrote it, not a recruiter
   - Be brief and specific
   - Use technical language naturally
   - Respect the candidate's time

**Important Constraints:**
- Maintain the original message length (don't make it significantly longer or shorter)
- Preserve the salary range if present
- Keep the overall structure (Hook → Context → Opportunity → CTA)
- DO NOT add new clichés while removing old ones

**Output Format:**
Return ONLY the refined message text. Do NOT include explanations or meta-commentary.

**Example Good Refinement:**

Original: "I'm reaching out about a great opportunity at TechCorp. Your work is impressive! We'd love to chat."

Refined: "Hi, I noticed your redis-clone project's concurrent write handling. We're building a similar distributed caching layer at TechCorp and need that exact expertise. Senior Backend role, $150k-$200k. Interested in a quick chat?"

**Now refine the original message above:"""

    return prompt
