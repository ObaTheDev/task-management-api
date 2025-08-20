# Task Management API

A comprehensive CRUD API for task management built with FastAPI, featuring complete test coverage and professional deployment setup.

## Features

### Core Functionality
- **CRUD Operations**: Create, Read, Update, Delete tasks
- **Task Model**: UUID, name, description, status (created/in_progress/completed)
- **Status Management**: Proper task lifecycle management
- **Validation**: Comprehensive input validation and error handling

### Technical Features
- **FastAPI Framework**: High-performance async API framework
- **SQLAlchemy ORM**: Database abstraction with SQLite/PostgreSQL support
- **Pydantic Models**: Data validation and serialization
- **Automatic API Documentation**: Swagger UI and ReDoc
- **Docker Support**: Containerized deployment
- **Comprehensive Testing**: pytest and Gauge test frameworks
- **PEP8 Compliance**: Clean, readable code following Python standards

## Quick Start

### Local Development

1. **Clone and Setup**
```bash
git clone <repository-url>
cd task-management-api
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Run the Application**
```bash
python main.py
```

3. **Access the API**
- API Base URL: http://localhost:8000
- Swagger Documentation: http://localhost:8000/docs
- ReDoc Documentation: http://localhost:8000/redoc

### Docker Deployment

#### SQLite Version (Development)
```bash
docker-compose up --build
```

#### PostgreSQL Version (Production)
```bash
docker-compose --profile postgres up --build
```

## API Endpoints

### Tasks

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/tasks/` | Create a new task |
| GET | `/tasks/{uuid}` | Get a specific task |
| GET | `/tasks/` | List all tasks (with filtering) |
| PUT | `/tasks/{uuid}` | Update a task |
| DELETE | `/tasks/{uuid}` | Delete a task |

### Utility

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/docs` | Swagger UI documentation |
| GET | `/redoc` | ReDoc documentation |

## API Usage Examples

### Create a Task
```bash
curl -X POST "http://localhost:8000/tasks/" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Complete project documentation",
       "description": "Write comprehensive API documentation"
     }'
```

### Get All Tasks
```bash
curl -X GET "http://localhost:8000/tasks/"
```

### Filter Tasks by Status
```bash
curl -X GET "http://localhost:8000/tasks/?status=in_progress"
```

### Update a Task
```bash
curl -X PUT "http://localhost:8000/tasks/{task-uuid}" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Updated task name",
       "status": "completed"
     }'
```

### Delete a Task
```bash
curl -X DELETE "http://localhost:8000/tasks/{task-uuid}"
```

## Task Model

```json
{
  "uuid": "123e4567-e89b-12d3-a456-426614174000",
  "name": "Task name",
  "description": "Task description",
  "status": "created",
  "created_at": "2024-01-01T12:00:00.000Z",
  "updated_at": "2024-01-01T12:00:00.000Z"
}
```

### Status Values
- `created` - Initial status for new tasks
- `in_progress` - Task is being worked on
- `completed` - Task is finished

## Testing

The application includes comprehensive test coverage using both pytest and Gauge frameworks.

### Pytest Tests

Run all pytest tests:
```bash
pytest -v
```

Run with coverage:
```bash
pytest --cov=main --cov-report=html
```

Test categories:
- **CRUD Operations**: All create, read, update, delete operations
- **Validation**: Input validation and error handling
- **Edge Cases**: Boundary conditions and error scenarios
- **API Documentation**: Documentation endpoints
- **Performance**: Large dataset handling

### Gauge Tests

Install Gauge:
```bash
# On macOS
brew install gauge

# On Ubuntu
sudo apt-get install gauge

# On Windows
choco install gauge
```

Run Gauge tests:
```bash
gauge run specs
```

Gauge test scenarios:
- Task lifecycle management
- Status transitions
- Error handling
- API documentation validation
- End-to-end workflows

## Database Configuration

### SQLite (Default)
Perfect for development and testing. Database file is created automatically.

### PostgreSQL (Production)
Set the `DATABASE_URL` environment variable:
```bash
export DATABASE_URL="postgresql://user:password@localhost:5432/tasks_db"
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `sqlite:///./tasks.db` |

## Code Quality

### PEP8 Compliance
The codebase follows PEP8 standards with:
- Proper naming conventions
- Consistent indentation (4 spaces)
- Line length under 88 characters
- Comprehensive docstrings
- Type hints throughout

### Clean Code Principles
- **Single Responsibility**: Each class/function has one purpose
- **DRY**: No code duplication
- **SOLID Principles**: Proper abstraction and dependency injection
- **Error Handling**: Comprehensive exception handling
- **Documentation**: Clear docstrings and comments

## Project Structure

```
task-management-api/
├── main.py              # Main application file
├── requirements.txt     # Python dependencies
├── Dockerfile          # Docker configuration
├── docker-compose.yml  # Docker Compose setup
├── README.md           # This file
├── test_main.py        # Pytest test suite
├── specs/              # Gauge test specifications
│   └── tasks.spec     # Gauge test scenarios
├── step_impl.py        # Gauge step implementations
└── data/              # Database directory (created automatically)
```

## Performance Considerations

- **Async Support**: FastAPI provides excellent async performance
- **Database Indexing**: Proper database indexes for efficient queries
- **Pagination**: Built-in pagination for large datasets
- **Connection Pooling**: SQLAlchemy connection pooling
- **Caching**: Response caching headers for static content

## Security Features

- **Input Validation**: Comprehensive Pydantic validation
- **SQL Injection Prevention**: SQLAlchemy ORM protection
- **CORS Support**: Configurable CORS policies
- **UUID Usage**: Secure, non-sequential identifiers
- **Error Handling**: No sensitive information in error responses

## Deployment

### Development
```bash
python main.py
```

### Production with Docker
```bash
docker-compose --profile postgres up -d
```

### Health Monitoring
The API includes a health check endpoint (`/health`) and Docker health checks for monitoring.

## API Documentation

### Swagger UI
Interactive API documentation available at `/docs` with:
- Request/response schemas
- Try-it-out functionality
- Authentication options
- Response examples

### ReDoc
Alternative documentation interface at `/redoc` with:
- Clean, readable format
- Detailed schema information
- Code examples
- Download options

## Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Ensure all tests pass
5. Follow PEP8 coding standards
6. Submit a pull request

## Testing Requirements Compliance

### Framework Scoring
- **FastAPI**: (Primary framework)
- **Gauge**: (Primary test framework)
- **pytest**: (Secondary test framework)

### Code Quality
-  PEP8 compliance throughout
-  Clean code principles applied
-  Comprehensive error handling
-  Type hints and documentation
-  SOLID principles implementation

### Optional Features
-  Swagger documentation
-  Docker support with docker-compose
-  Comprehensive README with examples
-  Production-ready database support
-  Health monitoring
-  CORS support
-  Pagination and filtering

## Contact

For technical questions: telegram -> @bezb0zhnik

## License

This project is provided as a technical demonstration for evaluation purposes.