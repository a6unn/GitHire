# juicebox Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-10-09

## Active Technologies
- **Python 3.11+**: Core language
- **LLM SDKs**: OpenAI + Anthropic for parsing and outreach
- **Pydantic v2**: Data validation and models
- **httpx**: Async HTTP client for GitHub API
- **Redis**: Caching layer (optional)
- **pytest + pytest-asyncio**: Testing framework
- **PyYAML**: Configuration management
- **FastAPI**: Backend API framework
- **SQLAlchemy**: Database ORM

## Project Structure
```
src/
  ├── jd_parser/           # Module 001 (33 tests)
  ├── github_sourcer/      # Module 002 (121 tests - ENHANCED)
  ├── ranking_engine/      # Module 003 (49 tests)
  ├── outreach_generator/  # Module 004 (63 tests)
  ├── backend_api/         # Module 005 (Backend API)
  ├── config/              # Shared config files
  └── data/                # Data files (cities, aliases)
tests/                     # 266 total tests
```

## Commands
```bash
# Run all tests
pytest

# Run specific module tests
pytest tests/github_sourcer/

# Run with verbose output
pytest -v

# Code formatting
ruff check .
black .
```

## Code Style
- Python 3.11+ type hints
- Async/await for I/O operations
- Pydantic models for validation
- Follow PEP 8 conventions

## Module Status

### ✅ Module 001: JD Parser (COMPLETE)
- 33/33 tests passing
- Natural language job description parsing
- Skill normalization with LLM fallback

### ✅ Module 002: GitHub Sourcer (ENHANCED - COMPLETE)
- 121/121 tests passing
- **NEW:** Advanced skills detection (library-level: pandas, numpy, React)
- **NEW:** Location intelligence (hierarchical city/state/country matching)
- **NEW:** Multi-signal ensemble scoring (dependencies, topics, bio, languages)
- **NEW:** Skill confidence scoring with transparent signal weights
- **NEW:** Fuzzy matching for location typos
- **NEW:** GraphQL batching for performance
- **NEW:** Configurable weights in external YAML files
- GitHub API integration with rate limiting
- Redis two-tier caching

### ✅ Module 003: Ranking Engine (COMPLETE)
- 49/49 tests passing
- Multi-factor scoring (skills, experience, activity, domain)
- LLM-based semantic skill matching

### ✅ Module 004: Outreach Generator (COMPLETE)
- 63/63 tests passing
- Personalized message generation
- Tone control (formal/casual)
- Content validation

### ✅ Module 005: Backend API (COMPLETE)
- FastAPI REST API
- Authentication with JWT
- Project management
- Pipeline execution

### ✅ Module 006: Frontend App (COMPLETE)
- React + TypeScript
- Vite build system
- Full integration with backend

## Recent Changes
- **2025-10-09**: Enhanced Module 002 with advanced skills detection, location intelligence, and ensemble scoring (62 new tests)
- **2025-10-06**: Completed all 6 modules with 204 tests
- **2025-10-05**: Added JD Parser module

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->