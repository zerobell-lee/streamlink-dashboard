# Contributing to Streamlink Dashboard

Thank you for your interest in contributing to Streamlink Dashboard! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Guidelines](#contributing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)

## Code of Conduct

By participating in this project, you are expected to uphold our Code of Conduct. Please be respectful and constructive in all interactions.

## Getting Started

### Prerequisites

- **Backend**: Python 3.10+, pip
- **Frontend**: Node.js 20+, npm
- **Database**: SQLite (included)
- **Recording**: streamlink, ffmpeg
- **Container**: Docker & Docker Compose (optional)

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/streamlink-dashboard.git
   cd streamlink-dashboard
   ```

## Development Setup

### Backend Development

```bash
cd backend

# Create virtual environment (recommended)
python3.10 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run development server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

### Docker Development

```bash
# Build and run with Docker Compose
docker-compose up --build
```

## Contributing Guidelines

### Branch Strategy

We follow a Git Flow branching strategy:

- `master` - Production-ready code
- `develop` - Integration branch for next release
- `feature/*` - New features (branch from develop)
- `bugfix/*` - Bug fixes (branch from develop)
- `hotfix/*` - Critical fixes (branch from master)

### Branch Naming Convention

- `feature/issue-number-short-description`
- `bugfix/issue-number-short-description`
- `hotfix/critical-issue-description`

**Examples:**
- `feature/14-youtube-platform-integration`
- `bugfix/15-database-file-sync-issue`
- `hotfix/security-vulnerability-auth`

### Workflow

1. **Create Issue**: Always create an issue before starting work
2. **Create Branch**: Create a feature/bugfix branch from `develop`
3. **Development**: Make your changes following coding standards
4. **Testing**: Ensure all tests pass and add new tests if needed
5. **Documentation**: Update documentation if necessary
6. **Pull Request**: Submit PR to `develop` branch (not `master`)
7. **Code Review**: Address review feedback
8. **Merge**: Maintainer will merge after approval

## Pull Request Process

### Before Submitting

- [ ] Create or update tests for your changes
- [ ] Run the full test suite and ensure all tests pass
- [ ] Update documentation if needed
- [ ] Follow the coding standards
- [ ] Write clear, descriptive commit messages

### PR Requirements

- **Target Branch**: Submit PRs to `develop` branch
- **Description**: Use the PR template to describe your changes
- **Scope**: Keep PRs focused on a single feature/fix
- **Size**: Avoid large PRs (>500 lines changed)
- **Tests**: Include relevant tests
- **Breaking Changes**: Clearly mark breaking changes

### Review Process

1. Automated checks (CI/CD) must pass
2. Code review by maintainer(s)
3. Address feedback and update PR
4. Final approval and merge by maintainer

## Coding Standards

### Backend (Python)

- **Formatter**: Use Black for code formatting
- **Linting**: Follow flake8 guidelines
- **Type Hints**: Use type hints where appropriate
- **Docstrings**: Follow Google-style docstrings
- **Imports**: Organize imports (stdlib, third-party, local)

```python
# Example code style
from typing import Optional, List
import hashlib

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    \"\"\"
    Retrieve a user by their ID.
    
    Args:
        db: Database session
        user_id: User ID to lookup
        
    Returns:
        User object if found, None otherwise
    \"\"\"
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()
```

### Frontend (TypeScript/React)

- **Formatter**: Use Prettier for code formatting
- **Linting**: Follow ESLint configuration
- **Components**: Use functional components with hooks
- **Props**: Define TypeScript interfaces for props
- **State**: Use Zustand for global state, useState for local state

```typescript
// Example component
interface RecordingCardProps {
  recording: Recording;
  onDelete: (id: number) => void;
}

export const RecordingCard: React.FC<RecordingCardProps> = ({
  recording,
  onDelete,
}) => {
  const [isLoading, setIsLoading] = useState(false);
  
  // Component logic here
  
  return (
    <div className="recording-card">
      {/* Component JSX */}
    </div>
  );
};
```

### Commit Messages

Follow Conventional Commits specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(auth): implement JSON login endpoint
fix(ui): resolve dashboard layout issues
docs: update installation instructions
test: add unit tests for recording service
```

## Testing

### Backend Testing

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py
```

### Frontend Testing

```bash
cd frontend

# Run unit tests
npm test

# Run tests in watch mode
npm run test:watch

# Run E2E tests (if available)
npm run test:e2e
```

### Integration Testing

- Test both frontend and backend together
- Verify API endpoints work correctly
- Test authentication flow end-to-end
- Validate recording functionality

## Documentation

### Code Documentation

- **Backend**: Use docstrings for functions and classes
- **Frontend**: Use JSDoc comments for complex functions
- **API**: Document API endpoints in code
- **README**: Keep README.md up to date

### When to Update Documentation

- Adding new features
- Changing existing functionality
- Updating configuration options
- Modifying API endpoints
- Adding new dependencies

## Getting Help

- **Questions**: Use GitHub Discussions or create a Question issue
- **Bugs**: Create a Bug Report issue
- **Features**: Create a Feature Request issue
- **Chat**: (Add Discord/Slack link if available)

## Recognition

All contributors will be recognized in our README.md file. Thank you for helping make Streamlink Dashboard better!

## License

By contributing to this project, you agree that your contributions will be licensed under the same license as the project (see LICENSE file).