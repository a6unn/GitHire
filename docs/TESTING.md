# Testing Guide

Comprehensive testing guide for GitHire project.

## Test Coverage

**Current Status**: 266+ tests passing

- **Module 001 (JD Parser)**: 33 tests ✅
- **Module 002 (GitHub Sourcer)**: 121 tests ✅
- **Module 003 (Ranking Engine)**: 49 tests ✅
- **Module 004 (Outreach Generator)**: 63 tests ✅
- **Backend API**: Integration tests ✅
- **Frontend**: Component and integration tests ✅

## Testing Stack

### Backend (Python)
- **Framework**: pytest
- **Mocking**: pytest-mock, unittest.mock
- **Async Testing**: pytest-asyncio
- **Coverage**: pytest-cov
- **Fixtures**: pytest fixtures

### Frontend (TypeScript)
- **Framework**: Vitest
- **React Testing**: @testing-library/react
- **User Events**: @testing-library/user-event
- **Mocking**: vi (Vitest)

## Running Tests

### Backend Tests

```bash
# Run all tests
pytest

# Run specific module
pytest tests/jd_parser/
pytest tests/github_sourcer/
pytest tests/ranking_engine/
pytest tests/outreach_generator/
pytest tests/backend_api/

# Run specific test file
pytest tests/jd_parser/test_parser.py

# Run specific test function
pytest tests/jd_parser/test_parser.py::test_parse_basic_jd

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=src --cov-report=html
pytest --cov=src --cov-report=term-missing

# Run tests in parallel (faster)
pytest -n auto

# Run only failed tests from last run
pytest --lf

# Run tests matching pattern
pytest -k "test_skill"
```

### Frontend Tests

```bash
cd frontend

# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run with coverage
npm run test:coverage

# Run specific test file
npm test -- src/components/Button.test.tsx

# Run tests matching pattern
npm test -- -t "Button"

# Update snapshots
npm test -- -u
```

## Test Structure

### Backend Test Structure

```
tests/
├── conftest.py              # Shared fixtures
├── jd_parser/
│   ├── test_parser.py       # JDParser tests
│   ├── test_llm_client.py   # LLM client tests
│   ├── test_skill_normalizer.py
│   └── test_validators.py
├── github_sourcer/
│   ├── test_search_service.py
│   ├── test_github_client.py
│   ├── test_profile_enricher.py
│   ├── test_skill_detector.py
│   └── test_location_parser.py
├── ranking_engine/
│   ├── test_ranker.py
│   ├── test_skill_matcher.py
│   └── test_scorers.py
├── outreach_generator/
│   ├── test_generator.py
│   ├── test_personalization.py
│   └── test_content_validator.py
└── backend_api/
    ├── test_auth_router.py
    ├── test_projects_router.py
    ├── test_workflow_router.py
    └── test_outreach_router.py
```

### Frontend Test Structure

```
frontend/src/
├── components/
│   ├── Button.tsx
│   ├── Button.test.tsx
│   ├── Card.tsx
│   └── Card.test.tsx
├── pages/
│   ├── DashboardPage.tsx
│   └── DashboardPage.test.tsx
└── utils/
    ├── formatters.ts
    └── formatters.test.ts
```

## Writing Tests

### Backend Test Example

```python
# tests/jd_parser/test_parser.py
import pytest
from src.jd_parser import parse_jd
from src.jd_parser.models import JobRequirement

class TestJDParser:
    """Test suite for JD Parser."""

    def test_parse_basic_jd(self):
        """Test parsing a basic job description."""
        jd_text = """
        Looking for a Senior Python Developer with 5+ years of experience.
        Must have experience with FastAPI and PostgreSQL.
        """

        result = parse_jd(jd_text)

        assert isinstance(result, JobRequirement)
        assert result.role == "Senior Python Developer"
        assert "Python" in result.required_skills
        assert "FastAPI" in result.required_skills
        assert result.experience_years == 5

    def test_parse_jd_with_invalid_input(self):
        """Test parser handles invalid input gracefully."""
        with pytest.raises(ValueError, match="Job description too short"):
            parse_jd("Hi")

    @pytest.mark.asyncio
    async def test_async_operation(self):
        """Test async operations."""
        result = await some_async_function()
        assert result is not None

    @pytest.fixture
    def sample_jd(self):
        """Fixture providing sample job description."""
        return """
        Senior Python Developer position...
        """

    def test_with_fixture(self, sample_jd):
        """Test using fixture."""
        result = parse_jd(sample_jd)
        assert result.role is not None
```

### Frontend Test Example

```typescript
// src/components/Button.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { Button } from './Button';

describe('Button', () => {
  it('renders button with text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  it('calls onClick when clicked', () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Click me</Button>);

    fireEvent.click(screen.getByText('Click me'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('disables button when disabled prop is true', () => {
    render(<Button disabled>Click me</Button>);
    const button = screen.getByText('Click me');

    expect(button).toBeDisabled();
  });

  it('applies correct variant class', () => {
    render(<Button variant="primary">Click me</Button>);
    const button = screen.getByText('Click me');

    expect(button).toHaveClass('bg-primary-600');
  });
});
```

## Fixtures and Mocking

### Backend Fixtures

```python
# tests/conftest.py
import pytest
from src.jd_parser.models import JobRequirement
from src.github_sourcer.models import Candidate

@pytest.fixture
def sample_job_requirement():
    """Provide sample JobRequirement for tests."""
    return JobRequirement(
        role="Senior Python Developer",
        required_skills=["Python", "FastAPI", "PostgreSQL"],
        experience_years=5,
        location="San Francisco, CA",
        preferred_skills=["Docker", "Redis"],
        confidence_scores={
            "role": 0.95,
            "skills": 0.90,
            "experience": 0.85
        }
    )

@pytest.fixture
def sample_candidate():
    """Provide sample Candidate for tests."""
    return Candidate(
        github_username="johnsmith",
        profile_url="https://github.com/johnsmith",
        bio="Python developer",
        location="San Francisco",
        email="john@example.com",
        company="TechCorp",
        public_repos=45,
        followers=230,
        following=120,
        created_at="2018-01-15T00:00:00Z",
        detected_skills={
            "Python": SkillConfidence(confidence=0.95, signals=["repos", "languages"]),
            "FastAPI": SkillConfidence(confidence=0.85, signals=["repos"])
        },
        top_languages=["Python", "JavaScript"],
        top_repositories=[]
    )

@pytest.fixture
def mock_openai_client(mocker):
    """Mock OpenAI API client."""
    mock = mocker.patch("src.jd_parser.llm_client.OpenAIClient")
    mock.return_value.complete.return_value = {
        "role": "Senior Python Developer",
        "required_skills": ["Python", "FastAPI"],
        "experience_years": 5
    }
    return mock

@pytest.fixture
def mock_github_client(mocker):
    """Mock GitHub API client."""
    mock = mocker.patch("src.github_sourcer.services.github_client.GitHubClient")
    mock.return_value.search_users.return_value = [...]
    return mock
```

### Frontend Mocking

```typescript
// src/__mocks__/api/projects.ts
import { vi } from 'vitest';

export const projectsApi = {
  getProjects: vi.fn().mockResolvedValue({
    projects: [
      {
        project_id: '1',
        name: 'Test Project',
        status: 'draft',
        candidate_count: 0,
      },
    ],
    total: 1,
  }),

  createProject: vi.fn().mockResolvedValue({
    project_id: '1',
    name: 'New Project',
    status: 'draft',
  }),
};
```

```typescript
// Using in tests
import { projectsApi } from '@/api/projects';

vi.mock('@/api/projects');

describe('ProjectsPage', () => {
  it('fetches and displays projects', async () => {
    render(<ProjectsPage />);

    await waitFor(() => {
      expect(screen.getByText('Test Project')).toBeInTheDocument();
    });

    expect(projectsApi.getProjects).toHaveBeenCalledTimes(1);
  });
});
```

## Integration Testing

### Backend API Integration Tests

```python
# tests/backend_api/test_auth_router.py
import pytest
from fastapi.testclient import TestClient
from src.backend_api.main import app

@pytest.fixture
def client():
    """Test client for API."""
    return TestClient(app)

@pytest.fixture
def auth_headers(client):
    """Get authentication headers."""
    # Register and login
    client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "testpass123"
    })

    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "testpass123"
    })

    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_register_user(client):
    """Test user registration."""
    response = client.post("/auth/register", json={
        "email": "newuser@example.com",
        "password": "securepass123"
    })

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert "user_id" in data

def test_login_user(client):
    """Test user login."""
    # First register
    client.post("/auth/register", json={
        "email": "user@example.com",
        "password": "pass123"
    })

    # Then login
    response = client.post("/auth/login", json={
        "email": "user@example.com",
        "password": "pass123"
    })

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_create_project(client, auth_headers):
    """Test creating a project."""
    response = client.post(
        "/projects",
        json={
            "name": "Test Project",
            "job_title": "Python Developer",
            "job_description_text": "Looking for a Python developer with FastAPI experience"
        },
        headers=auth_headers
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Project"
    assert data["status"] == "draft"
```

### Frontend Integration Tests

```typescript
// src/__tests__/integration/auth-flow.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import App from '@/App';

describe('Authentication Flow', () => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });

  const renderApp = () => {
    return render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </QueryClientProvider>
    );
  };

  it('completes full auth flow', async () => {
    const user = userEvent.setup();
    renderApp();

    // Should show login page
    expect(screen.getByText(/sign in/i)).toBeInTheDocument();

    // Click register link
    await user.click(screen.getByText(/create account/i));

    // Fill registration form
    await user.type(screen.getByLabelText(/email/i), 'test@example.com');
    await user.type(screen.getByLabelText(/password/i), 'testpass123');
    await user.click(screen.getByRole('button', { name: /register/i }));

    // Should redirect to dashboard
    await waitFor(() => {
      expect(screen.getByText(/dashboard/i)).toBeInTheDocument();
    });
  });
});
```

## Test Coverage

### View Coverage Report

```bash
# Backend
pytest --cov=src --cov-report=html
open htmlcov/index.html

# Frontend
npm run test:coverage
open coverage/index.html
```

### Coverage Goals

- **Overall**: > 80%
- **Critical paths**: > 95%
- **Business logic**: > 90%
- **UI components**: > 70%

## Test Best Practices

### DO ✅

- **Write tests first** (TDD when possible)
- **Test behavior, not implementation**
- **Use descriptive test names**
- **One assertion per test** (when possible)
- **Mock external dependencies**
- **Test edge cases and error conditions**
- **Keep tests independent**
- **Use fixtures for common setup**

### DON'T ❌

- **Don't test implementation details**
- **Don't write brittle tests**
- **Don't ignore failing tests**
- **Don't skip error cases**
- **Don't mock everything**
- **Don't write slow tests**
- **Don't duplicate test logic**

### Example: Good vs Bad

**Bad**:
```python
def test_parser():
    """Test parser."""  # Vague name
    result = parse_jd("Looking for developer")
    assert result.role is not None  # Testing implementation
```

**Good**:
```python
def test_parse_jd_extracts_role_from_basic_description():
    """Test that parser correctly extracts role from simple job description."""
    jd_text = "Looking for a Senior Python Developer"

    result = parse_jd(jd_text)

    assert result.role == "Senior Python Developer"
```

## Continuous Integration

### GitHub Actions Example

`.github/workflows/test.yml`:
```yaml
name: Tests

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -e .
          pip install pytest pytest-cov
      - name: Run tests
        run: pytest --cov=src --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install dependencies
        run: cd frontend && npm ci
      - name: Run tests
        run: cd frontend && npm test
```

## Performance Testing

### Load Testing (Backend)

Using `locust`:

```python
# locustfile.py
from locust import HttpUser, task, between

class GitHireUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        """Login before tasks."""
        response = self.client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "testpass123"
        })
        self.token = response.json()["access_token"]

    @task
    def get_projects(self):
        self.client.get("/projects", headers={
            "Authorization": f"Bearer {self.token}"
        })

    @task(3)
    def get_project_details(self):
        self.client.get(f"/projects/{self.project_id}", headers={
            "Authorization": f"Bearer {self.token}"
        })
```

```bash
# Run load test
locust -f locustfile.py --host=http://localhost:8000
```

## Debugging Tests

### Python Debugger

```python
# Add to test
import pdb; pdb.set_trace()

# Or use breakpoint()
breakpoint()
```

### VS Code Test Debugging

`.vscode/launch.json`:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Pytest",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": ["-v", "${file}"],
      "console": "integratedTerminal",
      "justMyCode": false
    }
  ]
}
```

---

**Last Updated**: 2025-10-10
