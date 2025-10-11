"""
End-to-End Pipeline Demo: JD Parser → GitHub Sourcer → Ranking Engine → Outreach Generator

Demonstrates the complete GitHire recruitment pipeline from job description text
to ranked GitHub candidate profiles with personalized outreach messages.
"""

import asyncio
import json
from src.jd_parser import parse_jd
from src.github_sourcer import search_github
from src.ranking_engine import rank_candidates
from src.outreach_generator import generate_outreach_batch


async def main():
    print("=" * 80)
    print("GitHire: End-to-End Recruitment Pipeline Demo")
    print("=" * 80)
    print()

    # Step 1: Parse Job Description
    print("STEP 1: Parse Job Description")
    print("-" * 80)

    jd_text = """
    Looking for a Senior Python Developer with 5+ years of experience.
    Must have strong experience with FastAPI and Docker.
    Location: India or Remote.
    Nice to have: PostgreSQL, Redis, Kubernetes experience.
    """

    print(f"Input JD:\n{jd_text}")
    print()

    job_requirement = parse_jd(jd_text)
    print(f"✓ Parsed successfully!")
    print(f"  Role: {job_requirement.role}")
    print(f"  Required Skills: {job_requirement.required_skills}")
    print(f"  Preferred Skills: {job_requirement.preferred_skills}")
    print(f"  Experience: {job_requirement.years_of_experience.range_text}")
    print(f"  Location: {job_requirement.location_preferences}")
    print(f"  Seniority: {job_requirement.seniority_level}")
    print()

    # Step 2: Search GitHub
    print("STEP 2: Search GitHub for Matching Candidates")
    print("-" * 80)

    result = await search_github(job_requirement)

    candidates = result["candidates"]
    metadata = result["metadata"]

    print(f"✓ Search complete!")
    print(f"  Total found: {metadata.total_candidates_found}")
    print(f"  Returned: {metadata.candidates_returned}")
    print(f"  Cache hit: {metadata.cache_hit}")
    print(f"  Execution time: {metadata.execution_time_ms}ms")
    print(f"  Rate limit remaining: {metadata.rate_limit_remaining}")
    print()

    # Step 3: Rank Candidates
    print("STEP 3: Rank Candidates by Fit")
    print("-" * 80)

    if candidates:
        ranked_candidates = rank_candidates(candidates, job_requirement)

        print(f"✓ Ranking complete!")
        print(f"  Candidates ranked: {len(ranked_candidates)}")
        print()

        # Step 4: Show Top Ranked Candidates
        print("STEP 4: Top Ranked Candidates")
        print("-" * 80)

        for ranked in ranked_candidates[:5]:  # Show top 5
            print(f"\n#{ranked.rank}: {ranked.github_username} (Score: {ranked.total_score:.1f}/100)")
            print(f"  Name: {ranked.name or 'N/A'}")
            print(f"  Location: {ranked.candidate.location or 'N/A'}")
            print(f"  Scores: Skill={ranked.skill_match_score:.1f}, Exp={ranked.experience_score:.1f}, "
                  f"Activity={ranked.activity_score:.1f}, Domain={ranked.domain_score:.1f}")
            print(f"  Matched Skills: {', '.join(ranked.score_breakdown.matched_skills) or 'None'}")
            if ranked.score_breakdown.missing_skills:
                print(f"  Missing Skills: {', '.join(ranked.score_breakdown.missing_skills)}")
            print(f"  Profile: {ranked.profile_url}")
    else:
        print("  No candidates to rank")

    print()

    # Step 5: Generate Outreach Messages
    if candidates and ranked_candidates:
        print("STEP 5: Generate Personalized Outreach Messages")
        print("-" * 80)

        # Generate outreach for top 5 ranked candidates
        top_candidates = ranked_candidates[:5]
        outreach_messages = generate_outreach_batch(top_candidates, job_requirement, tone="formal")

        print(f"✓ Outreach generation complete!")
        print(f"  Messages generated: {len(outreach_messages)}")
        print()

        # Display outreach messages
        print("TOP OUTREACH MESSAGES")
        print("-" * 80)

        for msg in outreach_messages[:3]:  # Show top 3 messages
            print(f"\n{'='*80}")
            print(f"Rank #{msg.rank}: {msg.candidate_username}")
            print(f"Confidence: {msg.confidence_score:.1f}/100 | Tone: {msg.tone.value}")
            print(f"Tokens: {msg.tokens_used} | Fallback: {msg.fallback_applied}")
            if msg.personalization_metadata.referenced_repositories:
                print(f"Referenced Repos: {', '.join(msg.personalization_metadata.referenced_repositories[:2])}")
            print(f"{'='*80}")
            print()
            print(msg.message_text)
            print()

        print("=" * 80)
    else:
        outreach_messages = []
        print("\nSkipping outreach generation (no candidates)")

    print()
    print("=" * 80)
    print(f"Pipeline complete! Generated {len(outreach_messages)} outreach messages.")
    print("=" * 80)

    # Save results
    output_file = "pipeline_output.json"
    with open(output_file, "w") as f:
        output = {
            "job_requirement": job_requirement.model_dump(mode="json"),
            "ranked_candidates": [rc.model_dump(mode="json") for rc in ranked_candidates] if candidates else [],
            "outreach_messages": [msg.model_dump(mode="json") for msg in outreach_messages] if outreach_messages else [],
            "metadata": metadata.model_dump(mode="json")
        }
        json.dump(output, f, indent=2, default=str)

    print(f"\n✓ Full results saved to: {output_file}")


if __name__ == "__main__":
    asyncio.run(main())
