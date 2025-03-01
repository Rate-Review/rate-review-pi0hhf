# Justice Bid Rate Negotiation System - Backend

## Overview

The Justice Bid Rate Negotiation System backend is a comprehensive API-driven platform designed to systematize the legal rate negotiation process between law firms and their corporate clients. This backend implementation provides the core services, data models, and business logic required to support the entire rate negotiation lifecycle.

The backend follows a microservices architecture to enable independent scaling of components while ensuring separation of concerns. It provides RESTful APIs for frontend interaction and integrates with external systems such as eBilling platforms and UniCourt for attorney performance data.

## Technology Stack

### Core Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.11+ | Primary programming language |
| Flask | 2.3+ | Web framework for API layer |
| SQLAlchemy | 2.0+ | ORM for database interactions |
| PostgreSQL | 15+ | Primary relational database |
| Redis | 7.0+ | Caching and message broker |
| MongoDB | 6.0+ | Document storage for unstructured data |
| Elasticsearch | 8.8+ | Search functionality |
| Celery | 5.3+ | Task queue for async processing |

### Key Libraries

| Library | Version | Purpose |
|---------|---------|---------|
| Flask-RESTful | 0.3.10+ | Simplifies building RESTful APIs |
| Pydantic | 2.0+ | Data validation and settings management |
| Pandas | 2.0+ | Data processing for analytics |
| NumPy | 1.24+ | Numerical computing |
| LangChain | 0.0.27+ | AI framework integration |
| Pytest | 7.3+ | Testing framework |
| Alembic | 1.11+ | Database migrations |
| Marshmallow | 3.19+ | Object serialization/deserialization |

### Development Tools

| Tool | Version | Purpose |
|------|---------|---------|
| Poetry | 1.5+ | Dependency management |
| Docker | 23+ | Containerization |
| Docker Compose | 2.17+ | Local development environment |
| Black | 23.3+ | Code formatting |
| Flake8 | 6.0+ | Linting |
| MyPy | 1.3+ | Static type checking |
| Pre-commit | 3.3+ | Git hooks for code quality |

## Getting Started

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- Poetry
- Git

### Setup Instructions

1. **Clone the repository:**

   ```bash
   git clone https://github.com/justicebid/rate-negotiation-system.git
   cd rate-negotiation-system/src/backend
   ```

2. **Install dependencies using Poetry:**

   ```bash
   poetry install
   ```

3. **Set up environment variables:**

   Create a `.env` file in the project root:

   ```
   # Database Configuration
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=justicebid
   DB_USER=postgres
   DB_PASSWORD=postgres
   
   # Redis Configuration
   REDIS_HOST=localhost
   REDIS_PORT=6379
   
   # MongoDB Configuration
   MONGO_URI=mongodb://localhost:27017/justicebid
   
   # Elasticsearch Configuration
   ELASTICSEARCH_HOST=localhost
   ELASTICSEARCH_PORT=9200
   
   # API Configuration
   API_SECRET_KEY=your-secret-key-here
   JWT_SECRET_KEY=your-jwt-secret-key-here
   
   # Integration Configuration
   UNICOURT_API_KEY=your-unicourt-api-key
   OPENAI_API_KEY=your-openai-api-key
   
   # Environment
   FLASK_ENV=development
   FLASK_DEBUG=1
   ```

4. **Start the development environment:**

   ```bash
   docker-compose up -d
   ```

   This will start PostgreSQL, Redis, MongoDB, and Elasticsearch.

5. **Initialize the database:**

   ```bash
   poetry run flask db upgrade
   ```

6. **Run the development server:**

   ```bash
   poetry run flask run
   ```

   The API will be available at [http://localhost:5000](http://localhost:5000).

7. **Access the API documentation:**

   Browse to [http://localhost:5000/api/docs](http://localhost:5000/api/docs) to view the Swagger UI documentation.

## Project Structure

The backend follows a domain-driven microservices architecture:

```
src/backend/
├── app/
│   ├── api/                    # API definitions
│   │   ├── v1/                 # API version 1
│   │   │   ├── endpoints/      # API endpoints by domain
│   │   │   │   ├── rates/
│   │   │   │   ├── negotiations/
│   │   │   │   ├── analytics/
│   │   │   │   ├── organizations/
│   │   │   │   ├── integrations/
│   │   │   │   ├── ai/
│   │   │   │   └── documents/
│   │   │   ├── schemas/        # Request/response schemas
│   │   │   └── __init__.py
│   │   └── __init__.py
│   ├── core/                   # Core application code
│   │   ├── config.py           # Configuration
│   │   ├── security.py         # Authentication and authorization
│   │   └── errors.py           # Error handling
│   ├── db/                     # Database models and migrations
│   │   ├── models/             # SQLAlchemy models
│   │   │   ├── rates.py
│   │   │   ├── negotiations.py
│   │   │   ├── organizations.py
│   │   │   ├── users.py
│   │   │   └── ...
│   │   ├── repositories/       # Database access layer
│   │   ├── migrations/         # Alembic migrations
│   │   └── __init__.py
│   ├── services/               # Business logic
│   │   ├── rate_service.py
│   │   ├── negotiation_service.py
│   │   ├── analytics_service.py
│   │   ├── organization_service.py
│   │   ├── integration_service.py
│   │   ├── ai_service.py
│   │   ├── document_service.py
│   │   └── __init__.py
│   ├── worker/                 # Background task workers
│   │   ├── tasks/              # Celery tasks
│   │   └── __init__.py
│   └── __init__.py             # Application factory
├── tests/                      # Test suite
│   ├── conftest.py             # Test configuration
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   └── api/                    # API tests
├── scripts/                    # Utility scripts
├── docker/                     # Docker configuration
├── .env.example                # Example environment variables
├── poetry.lock                 # Lock file
├── pyproject.toml              # Project dependencies
├── alembic.ini                 # Alembic configuration
├── docker-compose.yml          # Docker Compose configuration
└── README.md                   # This file
```

### Key Components

#### Microservices

The backend is composed of several microservices, each responsible for a specific domain:

- **Rate Service**: Manages rate data lifecycle
- **Negotiation Service**: Handles negotiation workflows
- **Analytics Service**: Processes data for insights
- **Organization Service**: Manages organizations and users
- **Integration Service**: Handles external system connections
- **AI Service**: Provides AI-powered recommendations
- **Document Service**: Manages OCGs and documents

#### Service Communication

Services communicate primarily through:
- Direct API calls for synchronous operations
- Message queues (Celery/Redis) for asynchronous operations
- Event-driven architecture for workflow transitions

## API Documentation

### API Design Principles

- RESTful architecture
- Resource-based URLs
- Standard HTTP methods (GET, POST, PUT, DELETE)
- JSON as the primary data exchange format
- JWT-based authentication
- Consistent error responses
- Versioning via URL path (/api/v1/...)

### Core API Endpoints

#### Rate Service API

```
GET    /api/v1/rates                   # List rates with filtering
POST   /api/v1/rates                   # Create new rate
GET    /api/v1/rates/:id               # Get rate details
PUT    /api/v1/rates/:id               # Update rate
GET    /api/v1/rates/:id/history       # Get rate history
POST   /api/v1/rates/:id/approve       # Approve rate
POST   /api/v1/rates/:id/reject        # Reject rate
POST   /api/v1/rates/:id/counter       # Counter-propose rate
```

#### Negotiation Service API

```
GET    /api/v1/negotiations                    # List negotiations
POST   /api/v1/negotiations                    # Create negotiation
GET    /api/v1/negotiations/:id                # Get negotiation details
PUT    /api/v1/negotiations/:id/status         # Update negotiation status
GET    /api/v1/negotiations/:id/rates          # Get rates in negotiation
POST   /api/v1/negotiations/:id/submit         # Submit rates for negotiation
POST   /api/v1/negotiations/:id/approve        # Approve negotiation
POST   /api/v1/negotiations/:id/reject         # Reject negotiation
```

#### Analytics Service API

```
GET    /api/v1/analytics/impact                # Get rate impact analysis
GET    /api/v1/analytics/comparison            # Get peer comparison
GET    /api/v1/analytics/trends                # Get historical trends
GET    /api/v1/analytics/performance           # Get attorney performance
POST   /api/v1/analytics/reports               # Create custom report
GET    /api/v1/analytics/reports/:id           # Get report results
```

#### Organization Service API

```
GET    /api/v1/organizations                   # List organizations
POST   /api/v1/organizations                   # Create organization
GET    /api/v1/organizations/:id               # Get organization details
PUT    /api/v1/organizations/:id               # Update organization
GET    /api/v1/organizations/:id/users         # List organization users
POST   /api/v1/organizations/:id/users         # Add user to organization
```

#### AI Service API

```
POST   /api/v1/ai/chat                         # Chat with AI
POST   /api/v1/ai/recommendations/rates        # Get rate recommendations
POST   /api/v1/ai/recommendations/actions      # Get action recommendations
POST   /api/v1/ai/analyze                      # Analyze specific data
```

### Authentication

The API uses JWT (JSON Web Token) for authentication:

1. Obtain a token:
   ```
   POST /api/v1/auth/login
   {
     "email": "user@example.com",
     "password": "password"
   }
   ```

2. Use the token in subsequent requests:
   ```
   Authorization: Bearer <your_token>
   ```

### Error Handling

All API errors follow a consistent format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message",
    "details": {
      "field_name": "Field-specific error"
    }
  }
}
```

Common HTTP status codes:
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 422: Validation Error
- 500: Server Error

## Database

### Schema Overview

The system uses a hybrid database approach:
- PostgreSQL for structured data (rates, organizations, users)
- MongoDB for document storage (messages, OCGs)
- Redis for caching and message queuing
- Elasticsearch for search functionality

#### Core Entity Relationships

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│  Organizations  │       │    Attorneys    │       │      Rates      │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ org_id          │       │ attorney_id     │       │ rate_id         │
│ name            │       │ name            │       │ attorney_id     │
│ type            │◄──────┤ org_id          │◄──────┤ effective_date  │
│ domain          │       │ office_id       │       │ expiration_date │
│ settings        │       │ staff_class_id  │       │ amount          │
└─────────────────┘       │ bar_date        │       │ currency        │
                          │ graduation_date │       │ status          │
┌─────────────────┐       │ timekeeper_ids  │       │ history         │
│  Staff Classes  │       └─────────────────┘       └─────────────────┘
├─────────────────┤                                  
│ class_id        │       ┌─────────────────┐       ┌─────────────────┐
│ org_id          │       │     Offices     │       │   Negotiations  │
│ name            │       ├─────────────────┤       ├─────────────────┤
│ experience_type │       │ office_id       │       │ negotiation_id  │
│ min_experience  │       │ org_id          │       │ client_org_id   │
│ max_experience  │       │ city            │       │ firm_org_id     │
└─────────────────┘       │ state           │       │ start_date      │
                          │ country         │       │ status          │
┌─────────────────┐       │ region          │       │ deadline        │
│  Peer Groups    │       └─────────────────┘       └─────────────────┘
├─────────────────┤                                  
│ group_id        │       ┌─────────────────┐       ┌─────────────────┐
│ org_id          │       │    Messages     │       │ Rate Proposals  │
│ name            │       ├─────────────────┤       ├─────────────────┤
│ criteria        │       │ message_id      │       │ proposal_id     │
└─────────────────┘       │ negotiation_id  │       │ negotiation_id  │
                          │ parent_id       │       │ rate_id         │
┌─────────────────┐       │ sender_id       │       │ proposed_amount │
│  Billing Data   │       │ content         │       │ status          │
├─────────────────┤       │ timestamp       │       │ message_id      │
│ billing_id      │       └─────────────────┘       │ timestamp       │
│ attorney_id     │                                 └─────────────────┘
│ client_org_id   │       ┌─────────────────┐       
│ matter_id       │       │      OCGs       │       ┌─────────────────┐
│ hours           │       ├─────────────────┤       │ Approval Flows  │
│ fees            │       │ ocg_id          │       ├─────────────────┤
│ date            │       │ client_org_id   │       │ flow_id         │
│ is_afa          │       │ sections        │       │ org_id          │
└─────────────────┘       │ alternatives    │       │ group_id        │
                          │ points          │       │ approvers       │
                          │ status          │       │ criteria        │
                          └─────────────────┘       └─────────────────┘
```

### Migrations

Database migrations are managed with Alembic:

```bash
# Create a new migration
poetry run flask db migrate -m "Add new field to rates table"

# Apply migrations
poetry run flask db upgrade

# Rollback migration
poetry run flask db downgrade
```

### Indexing Strategy

Key indexes are configured for query optimization:

- Organizations: index on domain
- Users: composite index on organization_id + email
- Attorneys: index on organization_id + name, GIN index on timekeeper_ids
- Rates: composite indexes on attorney_id + client_id + status, effective_date + expiration_date
- Negotiations: composite index on client_id + firm_id + status

## Development Guidelines

### Code Style

The project follows these coding standards:
- PEP 8 for Python code style
- Black for code formatting
- Flake8 for linting
- MyPy for static type checking

### Development Workflow

1. Create a feature branch from `main`
2. Implement your changes
3. Write tests
4. Run the test suite and ensure all tests pass
5. Submit a pull request
6. Code review
7. Merge to `main` after approval

### Commit Message Format

```
feat(component): add rate negotiation interface
^    ^           ^
|    |           |
|    |           +-> Summary in present tense
|    |
|    +--------------> Component (api, db, service, etc.)
|
+-------------------> Type: feat, fix, docs, style, refactor, test, chore
```

### Git Hooks

The project uses pre-commit hooks for code quality checks. Install pre-commit:

```bash
poetry run pre-commit install
```

### Documentation

- Use docstrings for all modules, classes, and functions
- Follow Google's Python Style Guide for docstring format
- Keep API documentation up to date using OpenAPI annotations

## Testing

### Test Suite Organization

Tests are organized into:
- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test interactions between components
- **API Tests**: Test API endpoints end-to-end

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run specific test category
poetry run pytest tests/unit/
poetry run pytest tests/integration/
poetry run pytest tests/api/

# Run tests with coverage
poetry run pytest --cov=app tests/
```

### Test Data

Test fixtures are provided in `tests/conftest.py` and specific test modules.

### Mocking External Services

External services like UniCourt and OpenAI are mocked during testing:

```python
# Example of mocking the UniCourt API
@pytest.fixture
def mock_unicourt_api(monkeypatch):
    def mock_get_attorney(*args, **kwargs):
        return {
            "id": "attorney123",
            "name": "John Smith",
            "bar_number": "12345",
            "performance_metrics": {
                "win_rate": 0.75,
                "case_count": 120
            }
        }
    
    monkeypatch.setattr(
        "app.services.integration_service.unicourt_client.get_attorney",
        mock_get_attorney
    )
```

## Deployment

### Containerization

The application is containerized using Docker:

```bash
# Build the Docker image
docker build -t justicebid/backend -f docker/Dockerfile .

# Run the container
docker run -p 5000:5000 justicebid/backend
```

### Kubernetes Deployment

Kubernetes manifests are provided in the `k8s/` directory:

```bash
# Apply Kubernetes configuration
kubectl apply -f k8s/
```

### CI/CD Pipeline

The CI/CD pipeline uses GitHub Actions:
1. Run tests on each pull request
2. Build and push Docker image on merge to main
3. Deploy to staging environment
4. Run integration tests
5. Manual promotion to production

### Environment Configuration

Different environments (development, staging, production) use different sets of environment variables. Environment variables are managed in AWS Parameter Store or Kubernetes Secrets.

## Integration Points

### eBilling System Integration

The system integrates with various eBilling platforms:

- **Onit**: REST API integration for rate data exchange
- **TeamConnect**: REST API integration for rate and timekeeper data
- **Legal Tracker**: REST API/file-based integration
- **BrightFlag**: REST API integration

### UniCourt Integration

Integration with UniCourt for attorney performance data:

- Attorney mapping between systems
- Retrieval of performance metrics
- Periodic data refresh

### AI Integration

Integration with AI providers:

- OpenAI for chat and recommendations
- Support for client-specific AI environments
- Configurable AI settings

### File Import/Export

Support for file-based data exchange:

- Excel templates for rate data
- CSV import/export
- PDF export for documents

## Contributing

Contributions are welcome! Please follow the [CONTRIBUTING.md](CONTRIBUTING.md) guidelines.

## License

This project is licensed under the [LICENSE](LICENSE) file in the repository.