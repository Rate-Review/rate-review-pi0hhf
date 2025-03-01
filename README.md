# Justice Bid Rate Negotiation System

[![Build Status](https://github.com/justicebid/rate-negotiation-system/workflows/build/badge.svg)](https://github.com/justicebid/rate-negotiation-system/actions)
[![Test Coverage](https://codecov.io/gh/justicebid/rate-negotiation-system/branch/main/graph/badge.svg)](https://codecov.io/gh/justicebid/rate-negotiation-system)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

<p align="center">
  <img src="public/images/logo-light.svg" alt="Justice Bid Logo" width="300">
</p>

## Project Overview

The Justice Bid Rate Negotiation System is a comprehensive platform designed to systematize the legal rate negotiation process between law firms and their clients. The system addresses the inefficient, email-based negotiation process currently used in the industry by providing a structured, analytics-driven approach to rate proposals, negotiations, and approvals.

The platform serves two primary user groups - law firms seeking to propose new rates to their clients, and corporate legal departments (clients) who need to evaluate, negotiate, and approve these rates. By incorporating AI-driven analytics, third-party performance data, and automated workflows, the system delivers actionable recommendations while maintaining a complete audit trail of all negotiations.

## Features

- **Rate Request Workflow**: Structured process for initiating, submitting, and tracking rate requests
- **Rate Submission Interface**: Streamlined interface for law firms to submit proposed rates
- **Rate Negotiation Interface**: Interactive interface for counter-proposals and approvals
- **Analytics Dashboard**: Comprehensive analytics on rate impact and peer comparisons
- **AI-Driven Recommendations**: Intelligent suggestions for rate proposals and negotiations
- **Approval Workflows**: Configurable approval processes within organizations
- **Outside Counsel Guidelines Management**: Tool for creating and negotiating OCGs
- **Integration Framework**: Connections to eBilling systems, law firm systems, and UniCourt
- **Multi-currency Support**: Handle rates in different currencies with conversion capabilities
- **Security and Compliance**: Enterprise-grade security with role-based permissions

## Technology Stack

The Justice Bid Rate Negotiation System employs a modern technology stack:

### Frontend
- **React.js v18.0+**: Component-based UI framework
- **Redux**: State management
- **Material UI v5.14+**: UI component library
- **Chart.js v4.0+**: Data visualization
- **TypeScript v5.0+**: Type-safe JavaScript

### Backend
- **Python v3.11+**: Core language for backend services
- **Flask v2.3+**: Web framework
- **SQLAlchemy v2.0+**: ORM for database access
- **Pandas v2.0+**: Data analysis
- **LangChain v0.0.27+**: AI framework integration

### Database & Storage
- **PostgreSQL v15+**: Primary relational database
- **MongoDB v6.0+**: Document storage for unstructured data
- **Redis v7.0+**: Caching and message brokering
- **AWS S3**: File storage

### DevOps & Infrastructure
- **Docker**: Containerization
- **Kubernetes**: Container orchestration
- **AWS**: Cloud infrastructure
- **GitHub Actions**: CI/CD pipeline

## Architecture

The Justice Bid system employs a microservices architecture organized around business domains:

<p align="center">
  <img src="docs/images/architecture-diagram.png" alt="System Architecture" width="800">
</p>

Key architectural components include:

- **Frontend Application**: React.js-based SPA with responsive design
- **API Gateway**: Entry point for all client requests
- **Microservices**:
  - Rate Service
  - Negotiation Service
  - Analytics Service
  - Integration Service
  - AI Service
  - Organization Service
  - Messaging Service
  - Document Service
- **Databases**: PostgreSQL for structured data, MongoDB for documents
- **Cache Layer**: Redis for performance optimization
- **Message Queue**: For asynchronous processing
- **Storage**: S3 for file storage

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Node.js v18+ and npm v9+ (for local frontend development)
- Python v3.11+ (for local backend development)
- PostgreSQL v15+ (for local database)

### Docker Setup (Recommended)

The easiest way to get started is using Docker Compose:

1. Clone the repository:
   ```bash
   git clone https://github.com/justicebid/rate-negotiation-system.git
   cd rate-negotiation-system
   ```

2. Start the application:
   ```bash
   docker-compose -f infrastructure/docker/docker-compose.yml -f infrastructure/docker/docker-compose.dev.yml up
   ```

3. Access the application at http://localhost:3000

### Manual Setup

If you prefer to set up the components manually:

#### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd src/backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install poetry
   poetry install
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Run migrations:
   ```bash
   flask db upgrade
   ```

6. Start the development server:
   ```bash
   flask run
   ```

#### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd src/web
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. Start the development server:
   ```bash
   npm start
   ```

### Running Tests

#### Backend Tests
```bash
cd src/backend
pytest
```

#### Frontend Tests
```bash
cd src/web
npm test
```

## Project Structure

```
justice-bid/
├── .github/                    # GitHub configuration
├── docs/                       # Documentation
├── infrastructure/             # Infrastructure as Code
│   ├── docker/                 # Docker configuration
│   ├── k8s/                    # Kubernetes manifests
│   └── terraform/              # Terraform modules
├── src/
│   ├── backend/                # Backend services
│   │   ├── rate_service/       # Rate management service
│   │   ├── negotiation_service/# Negotiation service
│   │   ├── analytics_service/  # Analytics service
│   │   ├── integration_service/# Integration service
│   │   ├── ai_service/         # AI service
│   │   ├── organization_service/# Organization service
│   │   ├── messaging_service/  # Messaging service
│   │   └── document_service/   # Document service
│   └── web/                    # Frontend application
│       ├── public/             # Static assets
│       └── src/                # React source code
│           ├── components/     # Reusable UI components
│           ├── containers/     # Container components
│           ├── pages/          # Page components
│           ├── hooks/          # Custom React hooks
│           ├── services/       # API services
│           └── utils/          # Utility functions
├── tests/                      # Integration tests
├── .editorconfig               # Editor configuration
├── .gitignore                  # Git ignore file
├── docker-compose.yml          # Docker Compose configuration
├── README.md                   # This file
└── LICENSE                     # License information
```

## Development Guidelines

### Code Style

- Frontend: Follow ESLint and Prettier configuration
- Backend: Follow PEP 8 style guide with Black formatter
- Use meaningful comments and documentation
- Write unit tests for all new features

### Git Workflow

1. Create a feature branch from `develop`
2. Make changes and commit using conventional commit messages
3. Push branch and create a pull request
4. Ensure CI pipeline passes
5. Request code review
6. Address review comments
7. Merge to `develop` once approved

### Documentation

- Update API documentation for any endpoint changes
- Maintain up-to-date component documentation
- Add comments explaining complex logic
- Update README files where appropriate

## API Documentation

The Justice Bid API follows RESTful principles with consistent patterns. Detailed API documentation is available at:

- Development: http://localhost:8000/api/docs
- Staging: https://staging-api.justicebid.com/api/docs
- Production: https://api.justicebid.com/api/docs

The API documentation is generated using OpenAPI and provides interactive exploration of all endpoints, request/response examples, and authentication requirements.

## Deployment

### Staging Deployment

Merges to the `develop` branch automatically deploy to the staging environment:

```bash
git checkout develop
git pull
git merge --no-ff feature/your-feature
git push
```

### Production Deployment

Production deployments are triggered by creating a release tag:

```bash
git checkout main
git pull
git merge --no-ff develop
git tag v1.0.0
git push --tags
```

### Manual Deployment

For manual deployment using Docker:

```bash
docker-compose -f infrastructure/docker/docker-compose.yml -f infrastructure/docker/docker-compose.prod.yml up -d
```

For Kubernetes deployment:

```bash
kubectl apply -f infrastructure/k8s/
```

## Contributing

We welcome contributions to the Justice Bid Rate Negotiation System! Please read our [Contributing Guidelines](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## Code of Conduct

This project and everyone participating in it is governed by the [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Security

For information about our security policies and how to report security vulnerabilities, please read our [Security Policy](SECURITY.md).

## License

This project is licensed under the [MIT License](LICENSE).