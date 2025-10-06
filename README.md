# GitHire

**AI-Powered GitHub Developer Recruitment Platform**

GitHire is an AI-driven POC recruitment tool that sources, ranks, and helps you reach out to software developers using GitHub as the primary talent source.

## Overview

GitHire automates the recruitment workflow:
1. **Analyze Job Description** - AI extracts required skills, experience, and tech stack
2. **Source Candidates** - Search GitHub for developers matching the criteria
3. **Rank & Score** - Intelligent ranking based on skill match, activity, and domain relevance
4. **Personalize Outreach** - AI-generated messages referencing candidate's actual work

## Core Principles

This project follows strict constitutional principles (see [`.specify/memory/constitution.md`](.specify/memory/constitution.md)):

- **🤖 AI-First**: LLMs power JD parsing and personalized outreach
- **🔒 Privacy-First**: Only public GitHub data, GDPR compliant
- **📍 Single Source**: GitHub API only (no LinkedIn/job boards in POC)
- **🔍 Transparent**: Explainable ranking and AI decisions
- **🧩 Modular**: Clean separation of concerns (parser, sourcer, ranker, outreach)

## Development Workflow

This project uses **Spec-Driven Development** with the Specify toolkit:

```bash
/constitution  # Define/update project principles
/specify       # Create feature specifications
/clarify       # De-risk and clarify specs
/plan          # Generate implementation plans
/tasks         # Create actionable task lists
/analyze       # Validate alignment
/implement     # Execute implementation
```

## Getting Started

### Prerequisites
- Node.js 18+ or Python 3.11+
- GitHub Personal Access Token (for API access)
- OpenAI/Anthropic API key (for AI features)

### Quick Start
```bash
# Clone and install
git clone <repo-url>
cd juicebox

# Set up environment
cp .env.example .env
# Add your API keys to .env

# Install dependencies
npm install  # or: pip install -r requirements.txt

# Run tests
npm test     # or: pytest

# Start development
npm run dev  # or: python -m githire
```

## Project Structure

```
.claude/           # Claude Code commands
.specify/          # Spec-driven development toolkit
  ├── memory/      # Constitution and state
  ├── scripts/     # Helper scripts
  └── templates/   # Document templates
specs/             # Feature specifications and plans
src/               # Source code (TBD)
tests/             # Test suites (TBD)
```

## Architecture (Planned)

### Modular Components
- **JD Parser**: `input: raw JD → output: {skills, experience, domain}`
- **GitHub Sourcer**: `input: requirements → output: [candidates]`
- **Ranking Engine**: `input: candidates + JD → output: scored candidates`
- **Outreach Generator**: `input: candidate + JD → output: personalized message`

## Privacy & Compliance

- ✅ Public GitHub data only (no scraping private repos)
- ✅ GDPR compliant (30-day data retention, right to erasure)
- ✅ GitHub API Terms of Service compliant
- ✅ Rate limiting (max 5000 req/hour authenticated)
- ✅ Opt-out mechanism for candidates

## License

[To be determined]

## Contributing

This is currently a POC project. Contributions will be considered after initial release.

---

**Constitution Version**: 1.0.0 | **Last Updated**: 2025-10-05
