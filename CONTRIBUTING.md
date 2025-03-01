# Contributing to Justice Bid Rate Negotiation System

## Introduction

Thank you for your interest in contributing to the Justice Bid Rate Negotiation System! This platform is designed to systematize the legal rate negotiation process between law firms and their clients, addressing inefficiencies in the current email-based negotiation processes used in the legal industry.

Your contributions help improve this platform for both law firms seeking to propose new rates to their clients and corporate legal departments who need to evaluate, negotiate, and approve these rates.

We value all contributions, whether they're bug fixes, feature enhancements, documentation improvements, or other forms of participation.

## Code of Conduct

The Justice Bid project is committed to fostering an open and welcoming environment. All contributors are expected to adhere to our Code of Conduct, which can be found in the [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) file in the repository.

The Code of Conduct outlines our expectations for participant behavior as well as the consequences for unacceptable behavior. We invite all contributors to read and follow it to help us create a positive and respectful community.

## Getting Started

### Prerequisites

To contribute to the Justice Bid project, you'll need:

- Node.js (v18+) and npm (v9+)
- Python (v3.11+)
- Docker and Docker Compose
- Git

### Repository Setup

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/justice-bid.git
   cd justice-bid
   ```
3. Add the original repository as an upstream remote:
   ```bash
   git remote add upstream https://github.com/justice-bid/justice-bid.git
   ```

### Backend Setup

1. Create a Python virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

3. Set up environment variables (copy from example):
   ```bash
   cp .env.example .env
   ```

4. Run database migrations:
   ```bash
   flask db upgrade
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Set up environment variables (copy from example):
   ```bash
   cp .env.example .env
   ```

### Running the Application

1. Start the backend server:
   ```bash
   # From the project root
   flask run
   ```

2. Start the frontend development server:
   ```bash
   # From the frontend directory
   npm start
   ```

3. Alternatively, use Docker Compose to run the entire application:
   ```bash
   docker-compose up
   ```

## Development Workflow

### Branching Strategy

- `main` - The production branch, containing stable code
- `develop` - The development branch, where features are integrated before release
- `feature/*` - Feature branches, created from `develop` for new features
- `bugfix/*` - Bugfix branches, created from `develop` for bug fixes
- `hotfix/*` - Hotfix branches, created from `main` for critical production fixes

### Commit Guidelines

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification for commit messages:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Types include:
- `feat:` - A new feature
- `fix:` - A bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, semicolons, etc)
- `refactor:` - Code refactoring without changes to functionality
- `perf:` - Performance improvements
- `test:` - Adding or updating tests
- `build:` - Changes to build system or dependencies
- `ci:` - Changes to CI configuration
- `chore:` - Other changes that don't modify src or test files

### Development Lifecycle

1. Pull the latest changes from the upstream repository
2. Create a new branch for your feature or bugfix
3. Make your changes, following coding standards
4. Write/update tests to cover your changes
5. Run tests and ensure they pass
6. Submit a pull request against the `develop` branch

## Coding Standards

### Frontend (React/TypeScript)

- Follow the TypeScript coding guidelines
- Use functional components with hooks over class components
- Use the provided UI component library for consistent styling
- Follow the React file organization structure:
  ```
  src/
  ├── components/    # Reusable UI components
  ├── containers/    # Container components
  ├── pages/         # Page components
  ├── hooks/         # Custom React hooks
  ├── services/      # API services
  ├── utils/         # Utility functions
  └── assets/        # Static assets
  ```
- Use meaningful component and variable names
- Document all components, hooks, and complex functions with JSDoc
- Run ESLint and Prettier before committing:
  ```bash
  npm run lint
  npm run format
  ```

### Backend (Python)

- Follow PEP 8 style guide
- Use meaningful function, variable, and class names
- Document all functions, classes, and modules with docstrings
- Organize imports according to:
  1. Standard library imports
  2. Third-party library imports
  3. Local application imports
- Maintain maximum line length of 88 characters
- Use type hints where applicable
- Run linting and formatting before committing:
  ```bash
  flake8
  black .
  isort .
  ```

## Testing

Testing is a critical part of the development process for the Justice Bid project.

### Unit Testing

- Frontend: Use Jest and React Testing Library
- Backend: Use pytest
- Aim for ≥90% code coverage for core business logic
- Aim for ≥80% code coverage for UI components

### Integration Testing

- Write integration tests that verify different components work together
- Use API contract testing to validate endpoints
- Test database operations against a test database

### End-to-End Testing

- Use Cypress for end-to-end testing of critical workflows
- Focus on key user journeys:
  - Rate submission and approval
  - Negotiation process
  - Analytics dashboard functionality

### Running Tests

- Frontend tests:
  ```bash
  cd frontend
  npm test           # Run tests
  npm run test:cov   # Run tests with coverage
  ```

- Backend tests:
  ```bash
  pytest             # Run all tests
  pytest --cov       # Run tests with coverage
  ```

- E2E tests:
  ```bash
  cd frontend
  npm run cypress    # Open Cypress test runner
  npm run e2e        # Run E2E tests headlessly
  ```

## Documentation

Good documentation is essential for maintaining and scaling the Justice Bid platform.

### Code Documentation

- Document all components, functions, and classes
- Explain complex logic with inline comments
- Use meaningful variable and function names that reduce the need for comments
- For frontend, use JSDoc for components and functions
- For backend, use Google-style docstrings

### API Documentation

- All API endpoints must be documented using OpenAPI/Swagger
- Include request/response examples
- Document error responses and status codes
- Update API documentation when adding or modifying endpoints

### Project Documentation

- Update relevant README files for any significant changes
- For major features, update or create appropriate documentation in the docs directory
- Consider creating or updating architecture diagrams for significant changes

## Issue Reporting

### Bug Reports

1. Check if the bug has already been reported
2. Use the [Bug Report Template](.github/ISSUE_TEMPLATE/bug_report.md)
3. Provide detailed reproduction steps
4. Include relevant system information
5. Attach screenshots if applicable
6. Indicate the severity of the issue

### Feature Requests

1. Check if the feature has already been requested
2. Use the [Feature Request Template](.github/ISSUE_TEMPLATE/feature_request.md)
3. Clearly describe the problem the feature would solve
4. Explain the desired solution
5. Consider alternatives you've thought about
6. Include any additional context or mockups

## Pull Requests

1. Create a pull request using the [Pull Request Template](.github/PULL_REQUEST_TEMPLATE.md)
2. Provide a clear, descriptive title
3. Reference any related issues
4. Describe the changes in detail
5. Include screenshots for UI changes
6. Ensure all checks pass (tests, linting, etc.)
7. Request review from appropriate team members

### PR Requirements

All pull requests must:
- Address a specific issue or feature
- Include appropriate tests
- Maintain or improve code coverage
- Follow coding standards
- Include necessary documentation updates
- Pass all CI checks

## Code Review

The code review process helps maintain code quality and knowledge sharing.

### Reviewer Responsibilities

- Respond to PRs within 2 business days
- Check code against the project's coding standards
- Verify tests are adequate and pass
- Ensure documentation is updated appropriately
- Provide constructive feedback
- Approve only when all issues are addressed

### Author Responsibilities

- Be responsive to reviewer feedback
- Explain design decisions when requested
- Make requested changes or justify why they shouldn't be made
- Keep the PR focused and of reasonable size
- Address all comments before requesting re-review

### Review Criteria

PRs will be approved when:
- All automated checks pass
- Code follows project standards
- Adequate tests are included
- Documentation is updated
- Reviewer concerns are addressed

## CI/CD Process

The Justice Bid project uses GitHub Actions for continuous integration and deployment.

### CI Workflow

For every push and pull request:
1. Linting and static analysis
2. Unit tests
3. Build verification
4. Integration tests
5. Code coverage reporting

For the `develop` and `main` branches:
1. All of the above checks
2. End-to-end tests
3. Deployment to the appropriate environment

### Troubleshooting CI Issues

1. Check the GitHub Actions logs for specific errors
2. Verify that tests pass locally in a clean environment
3. Compare your branch with the target branch for dependency changes
4. For persistent issues, reach out to the team in the development channel

## Questions?

If you have questions about contributing that aren't answered here, please reach out to the team via:
- GitHub Discussions
- The project Slack channel
- Email at maintainers@justicebid.example.com