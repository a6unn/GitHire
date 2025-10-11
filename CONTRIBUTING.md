# Contributing to GitHire

Thank you for your interest in contributing to GitHire! We welcome contributions from the community and are grateful for your support.

## Table of Contents

- [Ways to Contribute](#ways-to-contribute)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Code Style Guidelines](#code-style-guidelines)
- [Commit Message Guidelines](#commit-message-guidelines)
- [Pull Request Process](#pull-request-process)
- [Testing Requirements](#testing-requirements)
- [Code Review Process](#code-review-process)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Features](#suggesting-features)
- [Community Guidelines](#community-guidelines)

## Ways to Contribute

There are many ways to contribute to GitHire:

- **Code Contributions**: Bug fixes, new features, performance improvements
- **Documentation**: Improve existing docs, add examples, fix typos
- **Testing**: Write tests, report bugs, test new features
- **Design**: UI/UX improvements, visual assets, branding
- **Community**: Answer questions, help other users, spread the word

## Getting Started

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/githire.git
cd githire

# Add upstream remote
git remote add upstream https://github.com/a6unn/GitHire.git
```

### 2. Set Up Development Environment

Follow the complete setup guide in [DEVELOPMENT.md](./docs/DEVELOPMENT.md).

**Quick Start:**

```bash
# Backend setup
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .

# Frontend setup
cd frontend
npm install

# Copy environment variables
cp .env.example .env
# Edit .env with your API keys
```

### 3. Create a Branch

```bash
# Create a feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/bug-description
```

## Development Workflow

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

### Before Committing

1. **Run tests** to ensure nothing breaks:
   ```bash
   # Backend tests
   pytest

   # Frontend tests
   cd frontend && npm test
   ```

2. **Run linters** to maintain code quality:
   ```bash
   # Python
   ruff check .
   ruff format .

   # TypeScript
   cd frontend
   npm run lint
   npm run format
   ```

3. **Run type checking**:
   ```bash
   # Python
   mypy src/

   # TypeScript
   cd frontend && npm run type-check
   ```

## Code Style Guidelines

### Python (Backend)

- **Python Version**: 3.11+
- **Formatter**: `ruff format`
- **Linter**: `ruff check`
- **Type Hints**: Use type hints for all function signatures
- **Docstrings**: Use Google-style docstrings

**Example:**
```python
from typing import List, Optional
from pydantic import BaseModel

def search_candidates(
    query: str,
    limit: int = 10,
    location: Optional[str] = None
) -> List[Candidate]:
    """Search for candidates matching the query.

    Args:
        query: Search query string
        limit: Maximum number of results to return
        location: Optional location filter

    Returns:
        List of matching Candidate objects

    Raises:
        ValueError: If query is empty
        APIError: If GitHub API request fails
    """
    if not query:
        raise ValueError("Query cannot be empty")

    # Implementation
    return candidates
```

### TypeScript (Frontend)

- **TypeScript**: Strict mode enabled
- **Formatter**: Prettier
- **Linter**: ESLint with React plugin
- **Component Style**: Functional components with hooks
- **Props**: Use TypeScript interfaces

**Example:**
```typescript
interface CandidateCardProps {
  candidate: Candidate;
  onSelect: (candidateId: string) => void;
  isSelected?: boolean;
}

export function CandidateCard({
  candidate,
  onSelect,
  isSelected = false
}: CandidateCardProps) {
  const handleClick = () => {
    onSelect(candidate.github_username);
  };

  return (
    <div
      className={`card ${isSelected ? 'selected' : ''}`}
      onClick={handleClick}
    >
      {/* Component content */}
    </div>
  );
}
```

### General Guidelines

- **File Naming**:
  - Python: `snake_case.py`
  - TypeScript: `PascalCase.tsx` for components, `camelCase.ts` for utilities
- **Line Length**: Maximum 100 characters (Python), 120 characters (TypeScript)
- **Imports**: Group and sort imports logically
- **Comments**: Write clear, concise comments for complex logic
- **Error Handling**: Always handle errors gracefully

## Commit Message Guidelines

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification.

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, missing semicolons, etc.)
- `refactor`: Code refactoring without changing functionality
- `test`: Adding or updating tests
- `chore`: Maintenance tasks (dependencies, build scripts, etc.)
- `perf`: Performance improvements

### Examples

```bash
feat(github-sourcer): add skill confidence scoring

Implement ensemble scoring for skill detection using multiple signals:
- Repository analysis
- README parsing
- Language detection

Closes #123
```

```bash
fix(auth): resolve token expiration handling

Fixed issue where expired tokens weren't properly refreshed,
causing users to be logged out unexpectedly.

Fixes #456
```

```bash
docs(readme): update installation instructions

Added clarification for Windows users and updated
Node.js version requirement to 18+.
```

### Scope

Use the module or component affected:
- `jd-parser`
- `github-sourcer`
- `ranking-engine`
- `outreach-generator`
- `backend-api`
- `frontend`
- `docs`
- `tests`

## Pull Request Process

### 1. Update Your Branch

```bash
# Fetch latest changes from upstream
git fetch upstream

# Rebase your branch
git rebase upstream/main
```

### 2. Push Your Changes

```bash
git push origin feature/your-feature-name
```

### 3. Create Pull Request

1. Go to the GitHub repository
2. Click "New Pull Request"
3. Select your branch
4. Fill out the PR template

### PR Template

```markdown
## Description
Brief description of the changes

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Related Issues
Fixes #(issue number)

## Testing
Describe the tests you ran to verify your changes:
- [ ] Unit tests pass (`pytest`)
- [ ] Frontend tests pass (`npm test`)
- [ ] Manual testing completed

## Checklist
- [ ] My code follows the style guidelines
- [ ] I have performed a self-review of my code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] Any dependent changes have been merged and published

## Screenshots (if applicable)
Add screenshots for UI changes
```

### 4. Code Review

- Be responsive to feedback
- Make requested changes promptly
- Keep discussions professional and constructive
- Request re-review after addressing feedback

### 5. Merge

Once approved, a maintainer will merge your PR. We use:
- **Squash and merge** for feature branches
- **Rebase and merge** for bug fixes
- **Merge commit** for significant features

## Testing Requirements

### Backend Tests

All new code must have corresponding tests:

```python
# tests/module_name/test_feature.py
import pytest
from src.module_name import feature_function

class TestFeatureName:
    """Test suite for feature_function."""

    def test_basic_functionality(self):
        """Test basic use case."""
        result = feature_function("input")
        assert result == "expected_output"

    def test_edge_case(self):
        """Test edge case handling."""
        with pytest.raises(ValueError, match="Invalid input"):
            feature_function("")

    @pytest.mark.asyncio
    async def test_async_operation(self):
        """Test async functionality."""
        result = await async_feature_function()
        assert result is not None
```

**Coverage Requirements:**
- Minimum 80% coverage for new code
- 100% coverage for critical paths
- All edge cases tested

### Frontend Tests

```typescript
// src/components/Feature.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { Feature } from './Feature';

describe('Feature', () => {
  it('renders correctly', () => {
    render(<Feature />);
    expect(screen.getByText('Feature')).toBeInTheDocument();
  });

  it('handles user interaction', async () => {
    const onAction = vi.fn();
    render(<Feature onAction={onAction} />);

    fireEvent.click(screen.getByRole('button'));

    await waitFor(() => {
      expect(onAction).toHaveBeenCalledTimes(1);
    });
  });
});
```

### Running Tests

```bash
# Run all tests
pytest                    # Backend
cd frontend && npm test   # Frontend

# Run with coverage
pytest --cov=src --cov-report=html
npm run test:coverage

# Run specific tests
pytest tests/module_name/
npm test -- Feature.test.tsx
```

## Code Review Process

### For Contributors

- Respond to reviews within 48 hours
- Address all comments (or explain why you disagree)
- Mark conversations as resolved after addressing
- Request re-review when ready

### For Reviewers

Focus on:
- **Correctness**: Does the code work as intended?
- **Tests**: Are there adequate tests?
- **Performance**: Are there obvious performance issues?
- **Security**: Are there security concerns?
- **Maintainability**: Is the code readable and maintainable?
- **Documentation**: Are changes documented?

Review checklist:
- [ ] Code follows style guidelines
- [ ] Tests are comprehensive
- [ ] Documentation is updated
- [ ] No breaking changes (or properly documented)
- [ ] Performance is acceptable
- [ ] Security considerations addressed

## Reporting Bugs

### Before Reporting

1. **Search existing issues** to avoid duplicates
2. **Test with latest version** to ensure bug still exists
3. **Gather information** about your environment

### Bug Report Template

```markdown
## Bug Description
A clear and concise description of what the bug is.

## Steps to Reproduce
1. Go to '...'
2. Click on '...'
3. Scroll down to '...'
4. See error

## Expected Behavior
What you expected to happen.

## Actual Behavior
What actually happened.

## Screenshots
If applicable, add screenshots.

## Environment
- OS: [e.g., macOS 13.0]
- Python Version: [e.g., 3.11.5]
- Node.js Version: [e.g., 18.17.0]
- Browser: [e.g., Chrome 118]

## Additional Context
Any other context about the problem.

## Possible Solution
(Optional) Suggest a fix or reason for the bug.
```

## Suggesting Features

### Feature Request Template

```markdown
## Feature Description
A clear and concise description of the feature.

## Problem Statement
What problem does this feature solve?

## Proposed Solution
How should this feature work?

## Alternatives Considered
What other solutions did you consider?

## Additional Context
Any other context, mockups, or examples.

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3
```

## Community Guidelines

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors, regardless of:
- Experience level
- Gender identity and expression
- Sexual orientation
- Disability
- Personal appearance
- Body size
- Race
- Ethnicity
- Age
- Religion
- Nationality

### Expected Behavior

- **Be respectful** and considerate in all interactions
- **Be collaborative** and help others when possible
- **Be patient** with newcomers and those learning
- **Accept constructive criticism** gracefully
- **Focus on what's best** for the community and project

### Unacceptable Behavior

- Harassment, discrimination, or offensive comments
- Personal attacks or insults
- Trolling or inflammatory comments
- Spam or excessive self-promotion
- Publishing others' private information

### Enforcement

Violations may result in:
1. Warning from maintainers
2. Temporary ban from project
3. Permanent ban from project

Report issues to: [project maintainers email]

## Getting Help

### Documentation

- [Development Guide](./docs/DEVELOPMENT.md)
- [Architecture Overview](./docs/ARCHITECTURE.md)
- [API Reference](./docs/API_REFERENCE.md)
- [Testing Guide](./docs/TESTING.md)
- [Deployment Guide](./docs/DEPLOYMENT.md)

### Communication

- **GitHub Discussions**: For questions and general discussion
- **GitHub Issues**: For bug reports and feature requests
- **Pull Requests**: For code contributions

### Common Questions

**Q: I'm new to open source. How do I start?**
A: Start with issues labeled `good first issue` or `help wanted`. Read our documentation and feel free to ask questions!

**Q: How long does code review take?**
A: We aim to review PRs within 3-5 business days. Complex PRs may take longer.

**Q: Can I work on an issue that's already assigned?**
A: Please check with the assignee first or wait for the issue to be unassigned.

**Q: My PR has merge conflicts. What do I do?**
A: Rebase your branch on the latest `main` branch and resolve conflicts locally.

## Recognition

Contributors will be:
- Listed in CHANGELOG.md for their contributions
- Mentioned in release notes for significant features
- Added to the GitHub contributors page

Thank you for contributing to GitHire! 🎉

---

**Questions?** Open a [GitHub Discussion](https://github.com/a6unn/GitHire/discussions) or reach out to the maintainers.
