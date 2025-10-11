# Development Guide

This guide will help you set up GitHire for local development.

## Prerequisites

### Required
- **Python 3.11+** ([Download](https://www.python.org/downloads/))
- **Node.js 18+** and npm ([Download](https://nodejs.org/))
- **Git** ([Download](https://git-scm.com/downloads))

### API Keys Required
- **GitHub Personal Access Token** (for GitHub API access)
  - Go to: GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
  - Generate new token with `public_repo` and `read:user` scopes

- **OpenAI API Key** (for LLM features)
  - Get from: https://platform.openai.com/api-keys
  - Requires paid account with credits

###

 Optional
- **Redis** (for caching, improves performance)
  - macOS: `brew install redis`
  - Ubuntu: `sudo apt-get install redis-server`
  - Windows: Use Docker or WSL

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/a6unn/GitHire.git
cd githire
```

### 2. Set Up Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your API keys
nano .env  # or use your preferred editor
```

Required variables in `.env`:
```bash
# OpenAI API Key (required)
OPENAI_API_KEY=sk-...

# GitHub Personal Access Token (required)
GITHUB_TOKEN=github_pat_...

# Optional: Redis configuration
REDIS_ENABLED=false
REDIS_HOST=localhost
REDIS_PORT=6379

# Optional: Database path (defaults to githire.db)
DATABASE_URL=sqlite:///./githire.db

# Security: JWT secret (auto-generated if not set)
JWT_SECRET_KEY=your-secret-key-here
```

### 3. Backend Setup

```bash
# Create a virtual environment
python3.11 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -e .

# Run database migrations (creates tables)
python3.11 -m src.backend_api.init_db

# Start the backend server
python3.11 -m uvicorn src.backend_api.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: http://localhost:8000

### 4. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at: http://localhost:5173

### 5. Verify Setup

1. Open http://localhost:5173 in your browser
2. Register a new account
3. Create a test project with a job description
4. Verify the pipeline runs successfully

## Project Structure

```
githire/
├── src/                    # Backend source code
│   ├── jd_parser/          # Module 001
│   ├── github_sourcer/     # Module 002
│   ├── ranking_engine/     # Module 003
│   ├── outreach_generator/ # Module 004
│   ├── backend_api/        # Module 005 (FastAPI)
│   ├── config/             # Configuration files
│   └── data/               # Data files (cities, skills)
├── frontend/               # Frontend React app
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── contexts/       # React contexts
│   │   ├── api/            # API client methods
│   │   └── types/          # TypeScript types
│   ├── public/             # Static assets
│   └── package.json
├── tests/                  # Test suites
├── docs/                   # Documentation
├── examples/               # Example code
├── .env.example            # Environment template
├── pyproject.toml          # Python dependencies
└── README.md
```

## Development Workflow

### Running in Development Mode

**Option 1: Run Separately** (Recommended for active development)

Terminal 1 - Backend:
```bash
source venv/bin/activate
python3.11 -m uvicorn src.backend_api.main:app --reload --host 0.0.0.0 --port 8000
```

Terminal 2 - Frontend:
```bash
cd frontend
npm run dev
```

**Option 2: Run in Background**

```bash
# Backend
python3.11 -m uvicorn src.backend_api.main:app --reload --host 0.0.0.0 --port 8000 > backend.log 2>&1 &

# Frontend
cd frontend && npm run dev > ../frontend.log 2>&1 &
```

### Hot Reloading

- **Backend**: FastAPI with `--reload` flag automatically reloads on file changes
- **Frontend**: Vite dev server with HMR (Hot Module Replacement)

### Database Management

**View Database**:
```bash
# Using SQLite CLI
sqlite3 githire.db

# Show tables
.tables

# Show schema
.schema users

# Query data
SELECT * FROM users;
```

**Reset Database**:
```bash
# Delete existing database
rm githire.db

# Recreate tables
python3.11 -m src.backend_api.init_db
```

**Database Migrations** (Manual for now):
```bash
# After model changes, add migration script to src/backend_api/migrations/
# Run migration
python3.11 -m src.backend_api.migrations.001_add_name_field
```

### API Documentation

FastAPI provides auto-generated API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

Use these for testing API endpoints directly from the browser.

### Running Tests

**Backend Tests** (pytest):
```bash
# Run all tests
pytest

# Run specific module tests
pytest tests/jd_parser/
pytest tests/github_sourcer/
pytest tests/ranking_engine/
pytest tests/outreach_generator/
pytest tests/backend_api/

# Run with coverage
pytest --cov=src --cov-report=html

# Run verbose
pytest -v

# Run specific test
pytest tests/jd_parser/test_parser.py::test_parse_basic_jd
```

**Frontend Tests** (Vitest):
```bash
cd frontend

# Run all tests
npm test

# Run with watch mode
npm run test:watch

# Run with coverage
npm run test:coverage
```

### Code Quality

**Python** (Backend):
```bash
# Format code
ruff format .

# Lint code
ruff check .

# Type checking
mypy src/

# Fix linting issues automatically
ruff check --fix .
```

**TypeScript** (Frontend):
```bash
cd frontend

# Lint
npm run lint

# Fix linting issues
npm run lint:fix

# Type checking
npm run type-check

# Format with Prettier
npm run format
```

### Environment-Specific Configuration

**Development** (.env):
```bash
DEBUG=true
LOG_LEVEL=DEBUG
OPENAI_API_KEY=sk-...
GITHUB_TOKEN=github_pat_...
```

**Testing** (.env.test):
```bash
DEBUG=false
DATABASE_URL=sqlite:///./test.db
OPENAI_API_KEY=sk-test-...
GITHUB_TOKEN=github_pat_test...
```

## Debugging

### Backend Debugging

**Using VS Code**:

Create `.vscode/launch.json`:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "src.backend_api.main:app",
        "--reload",
        "--host", "0.0.0.0",
        "--port", "8000"
      ],
      "jinja": true,
      "justMyCode": false
    }
  ]
}
```

**Using pdb** (Python debugger):
```python
# Add breakpoint in code
import pdb; pdb.set_trace()

# Or use breakpoint() in Python 3.7+
breakpoint()
```

**Logging**:
```python
import logging

logger = logging.getLogger(__name__)
logger.debug("Debug message")
logger.info("Info message")
logger.error("Error message")
```

### Frontend Debugging

**React DevTools**:
- Install: [Chrome](https://chrome.google.com/webstore/detail/react-developer-tools/fmkadmapgofadopljbjfkapdkoienihi) | [Firefox](https://addons.mozilla.org/en-US/firefox/addon/react-devtools/)
- Inspect component state and props

**Browser DevTools**:
```javascript
// Add console logs
console.log('Debug:', data);
console.table(array);

// Debugger breakpoint
debugger;
```

**React Query DevTools**:
Already integrated in development mode. Check bottom-right corner of the app.

## Common Issues

### Issue: "Module not found" errors

**Solution**:
```bash
# Backend
pip install -e .

# Frontend
cd frontend && npm install
```

### Issue: Database locked errors

**Solution**:
```bash
# Stop all running processes
pkill -f uvicorn

# Delete database and recreate
rm githire.db
python3.11 -m src.backend_api.init_db
```

### Issue: CORS errors in browser

**Solution**:
Check that frontend is running on `http://localhost:5173` (default Vite port). Backend CORS is configured for this origin.

If using different port, update `src/backend_api/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:YOUR_PORT"],
    ...
)
```

### Issue: Rate limit errors from GitHub

**Solution**:
1. Check your GitHub token is valid
2. Use Redis caching to reduce API calls
3. Wait for rate limit to reset (shown in error message)

### Issue: OpenAI API errors

**Solution**:
1. Verify API key is correct
2. Check account has credits
3. Verify internet connection
4. Check OpenAI status: https://status.openai.com/

## Performance Profiling

### Backend Profiling

**Using cProfile**:
```bash
python3.11 -m cProfile -o profile.stats demo_pipeline.py

# Analyze results
python3.11 -m pstats profile.stats
# Then use: sort cumulative, stats 20
```

**Using py-spy** (sampling profiler):
```bash
pip install py-spy

# Profile running process
py-spy top --pid <process-id>

# Generate flamegraph
py-spy record -o profile.svg -- python3.11 demo_pipeline.py
```

### Frontend Profiling

**React Profiler**:
1. Open React DevTools
2. Go to "Profiler" tab
3. Click record button
4. Interact with app
5. Stop recording and analyze

**Lighthouse** (Chrome DevTools):
1. Open DevTools → Lighthouse tab
2. Select categories
3. Generate report

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for contribution guidelines.

## IDE Setup

### VS Code

Recommended extensions:
```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "charliermarsh.ruff",
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "bradlc.vscode-tailwindcss",
    "dsznajder.es7-react-js-snippets"
  ]
}
```

### PyCharm

1. Mark `src/` as Sources Root
2. Set Python interpreter to virtual environment
3. Enable pytest as test runner
4. Configure ruff as external tool

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vitejs.dev/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [React Query Documentation](https://tanstack.com/query/latest)

---

**Last Updated**: 2025-10-10
