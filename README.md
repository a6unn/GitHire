# GitHire 

<div align="center">

**AI-Powered GitHub Developer Recruitment Platform**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/react-18-blue.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Tests](https://img.shields.io/badge/tests-266%20passing-success.svg)](./docs/TESTING.md)

[Features](#features) • [Quick Start](#quick-start) • [Documentation](#documentation) • [Architecture](#architecture) • [Contributing](#contributing)

</div>

---

## Overview

GitHire is a full-stack AI-powered recruitment platform that helps you source, evaluate, and reach out to software developers using GitHub as the primary talent source. It combines the power of LLMs with GitHub's rich developer data to streamline technical recruitment.

### How It Works

```
📝 Job Description → 🤖 AI Analysis → 🔍 GitHub Search → 📊 Smart Ranking → ✉️ Personalized Outreach
```

1. **Analyze Job Description** - AI extracts required skills, experience, and tech stack
2. **Source Candidates** - Search GitHub for developers matching the criteria
3. **Rank & Score** - Intelligent ranking based on skill match, activity, and domain relevance
4. **Personalize Outreach** - AI-generated messages referencing candidate's actual work
5. **Manage Pipeline** - Web-based dashboard to review, shortlist, and contact candidates

---

## ✨ Features

### Core Capabilities

- **AI-Powered Job Analysis** - Natural language processing of job descriptions
- **Advanced GitHub Search** - Multi-signal skill detection with library-level precision
- **Intelligent Ranking** - Multi-factor scoring (skills, experience, activity, domain)
- **Personalized Outreach** - Context-aware message generation with customization
- **Multi-Channel Support** - Email, LinkedIn, and Twitter/X outreach templates
- **Follow-Up Sequences** - Automated 3-stage follow-up campaigns

### Frontend Dashboard

- **Project Management** - Create and manage multiple recruitment projects
- **Candidate Browsing** - Review ranked candidates with detailed profiles
- **Shortlisting** - Select top candidates for outreach
- **Outreach Generation** - Generate and customize multi-channel messages
- **Profile Management** - User authentication and profile settings

### 🔧 Technical Features

- **Modular Architecture** - 5 independent, well-tested modules
- **Comprehensive Testing** - 266+ tests with >80% coverage
- **REST API** - FastAPI with auto-generated documentation
- **Real-time Updates** - React Query for optimized data fetching
- **Caching Layer** - Redis integration for GitHub API optimization
- **Type Safety** - TypeScript frontend, Pydantic backend validation

---

## Quick Start

### Prerequisites

- **Python 3.11+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** and npm - [Download](https://nodejs.org/)
- **GitHub Personal Access Token** - [Create token](https://github.com/settings/tokens)
- **OpenAI API Key** - [Get API key](https://platform.openai.com/api-keys)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/a6unn/GitHire.git
cd githire

# 2. Set up environment variables
cp .env.example .env
# Edit .env and add your API keys:
#   OPENAI_API_KEY=sk-...
#   GITHUB_TOKEN=github_pat_...

# 3. Backend setup
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .

# 4. Frontend setup
cd frontend
npm install
cd ..
```

### Running the Application

**Terminal 1 - Backend:**
```bash
source venv/bin/activate
python3.11 -m uvicorn src.backend_api.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Access the application:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## 📚 Documentation

Comprehensive documentation is available in the [`docs/`](./docs) directory:

- **[Quick Start Guide](./docs/QUICKSTART.md)** - Get up and running quickly
- **[Development Guide](./docs/DEVELOPMENT.md)** - Local development setup
- **[Architecture](./docs/ARCHITECTURE.md)** - System design and technical details
- **[API Reference](./docs/API_REFERENCE.md)** - Complete API documentation
- **[Testing Guide](./docs/TESTING.md)** - Testing practices and guidelines
- **[Deployment Guide](./docs/DEPLOYMENT.md)** - Production deployment options

---

## 🏗️ Architecture

### Tech Stack

**Frontend:**
- React 18 + TypeScript
- Vite (build tool)
- Tailwind CSS
- React Query (TanStack Query)
- React Router v6
- Axios

**Backend:**
- FastAPI (Python 3.11+)
- SQLAlchemy ORM
- SQLite / PostgreSQL
- JWT Authentication
- Redis (optional caching)

**AI & APIs:**
- OpenAI GPT-4 (job parsing, skill matching, outreach)
- GitHub REST API + GraphQL
- Async/await for performance

### Module Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Frontend (React + TypeScript)                 │
│  Dashboard • Projects • Candidates • Shortlisting • Outreach    │
└────────────────────────────┬────────────────────────────────────┘
                             │ REST API
┌────────────────────────────▼────────────────────────────────────┐
│                    Backend API (FastAPI)                         │
│  Authentication • Projects • Workflow • Multi-Stage Pipeline    │
└────────────────────────────┬────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────▼────────┐  ┌────────▼────────┐  ┌──────▼─────────┐
│  Module 001    │  │  Module 002     │  │  Module 003    │
│  JD Parser     │  │  GitHub Sourcer │  │  Ranking       │
│  (33 tests ✅) │  │  (121 tests ✅) │  │  (49 tests ✅) │
└────────────────┘  └─────────────────┘  └────────────────┘

        ┌────────────────────┬────────────────────┐
        │                    │                    │
┌───────▼────────┐  ┌────────▼────────┐  ┌──────▼─────────┐
│  Module 004    │  │  Module 005     │  │  Database      │
│  Outreach Gen  │  │  Contact Enrich │  │  (SQLite)      │
│  (63 tests ✅) │  │  (Integrated)   │  │                │
└────────────────┘  └─────────────────┘  └────────────────┘
```

For detailed architecture information, see [ARCHITECTURE.md](./docs/ARCHITECTURE.md).

---

## 📂 Project Structure

```
githire/
├── frontend/                 # React frontend application
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── pages/            # Page components
│   │   ├── contexts/         # React contexts (Auth, Toast)
│   │   ├── api/              # API client methods
│   │   └── types/            # TypeScript type definitions
│   ├── public/               # Static assets
│   └── package.json          # Frontend dependencies
│
├── src/                      # Backend source code
│   ├── jd_parser/            # Module 001: JD Parser
│   ├── github_sourcer/       # Module 002: GitHub Sourcer
│   ├── ranking_engine/       # Module 003: Ranking Engine
│   ├── outreach_generator/   # Module 004: Outreach Generator
│   ├── backend_api/          # Module 005: FastAPI Backend
│   ├── config/               # Configuration files
│   └── data/                 # Data files (cities, skills)
│
├── tests/                    # Test suites (266+ tests)
│   ├── jd_parser/            # JD Parser tests
│   ├── github_sourcer/       # GitHub Sourcer tests
│   ├── ranking_engine/       # Ranking Engine tests
│   ├── outreach_generator/   # Outreach Generator tests
│   └── backend_api/          # Backend API tests
│
├── docs/                     # Documentation
│   ├── QUICKSTART.md
│   ├── DEVELOPMENT.md
│   ├── ARCHITECTURE.md
│   ├── API_REFERENCE.md
│   ├── TESTING.md
│   └── DEPLOYMENT.md
│
├── .env.example              # Environment variables template
├── pyproject.toml            # Python dependencies
├── LICENSE                   # MIT License
└── README.md                 # This file
```

---

##  Testing

GitHire has comprehensive test coverage across all modules:

```bash
# Backend tests (266+ tests)
pytest

# Frontend tests
cd frontend && npm test

# Coverage report
pytest --cov=src --cov-report=html
```

**Test Coverage:**
- Module 001 (JD Parser): 33 tests ✅
- Module 002 (GitHub Sourcer): 121 tests ✅
- Module 003 (Ranking Engine): 49 tests ✅
- Module 004 (Outreach Generator): 63 tests ✅
- Backend API: Integration tests ✅
- Frontend: Component tests ✅

See [TESTING.md](./docs/TESTING.md) for detailed testing guidelines.

---

## 🔐 Privacy & Compliance

-  **Public Data Only** - Uses only publicly available GitHub data
-  **GDPR Compliant** - Data retention and right to erasure
-  **GitHub ToS Compliant** - Adheres to GitHub API terms of service
-  **Rate Limiting** - Respects GitHub API rate limits
-  **Transparent AI** - Explainable scoring and ranking
-  **Opt-Out Support** - Mechanism for candidates to opt out

---

## Key Highlights

### Advanced Skills Detection
Multi-signal ensemble scoring with library-level precision:
- Repository analysis
- README parsing
- Language detection
- Code frequency analysis
- Skill confidence scoring

### Intelligent Ranking
Multi-factor scoring system:
- **Skills Match** (40%) - LLM semantic matching
- **Experience** (20%) - Account age, stars, repos
- **Activity** (20%) - Followers, contributions
- **Domain Relevance** (20%) - LLM-based project analysis

### Personalized Outreach
Context-aware message generation:
- Adaptive depth (deep/medium/surface) based on ranking
- Multi-channel support (Email, LinkedIn, Twitter)
- Repository-specific personalization
- Cliché detection and avoidance
- 3-stage follow-up sequences

### Performance Optimizations
- Async parallel profile enrichment (25 profiles in ~4 seconds)
- Two-tier Redis caching (search + profiles)
- GraphQL batching for GitHub API
- React Query for optimized frontend data fetching

---

## Contributing

We welcome contributions! Please see our [Contributing Guide](./CONTRIBUTING.md) for details.

### Development Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest` and `npm test`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Code Quality

- **Python**: ruff for linting and formatting
- **TypeScript**: ESLint + Prettier
- **Tests**: Required for new features
- **Documentation**: Update docs for significant changes

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- **OpenAI** - GPT-4 for intelligent parsing and generation
- **GitHub** - Rich developer data and robust API
- **FastAPI** - High-performance Python web framework
- **React** - Modern UI development
- **Open Source Community** - For amazing tools and libraries

---

## 📬 Support

- **Documentation**: Check the [docs/](./docs) directory
- **Issues**: [GitHub Issues](https://github.com/a6unn/GitHire/issues)
- **Discussions**: [GitHub Discussions](https://github.com/a6unn/GitHire/discussions)

---

## 🗺️ Roadmap

- [ ] Email integration (SendGrid, SMTP)
- [ ] LinkedIn API integration
- [ ] Advanced analytics dashboard
- [ ] Team collaboration features
- [ ] Interview scheduling integration
- [ ] Chrome extension for LinkedIn sourcing
- [ ] Mobile app (React Native)

---

<div align="center">

**Built with ❤️ by the Ideas2IT team**

⭐ Star us on GitHub if you find this project helpful!

[Website](https://ideas2it.com) • [Documentation](./docs) • [API Docs](http://localhost:8000/docs)

</div>

---

**Version**: 1.0.0 | **Last Updated**: 2025-10-10
