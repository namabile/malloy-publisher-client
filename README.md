# Malloy Publisher Client

A Python client for interacting with the Malloy Publisher API. This client provides a type-safe interface for working with Malloy projects, packages, models, and executing queries.

## Features

- Type-safe API client with Pydantic models
- Full support for Malloy Publisher API endpoints
- Async HTTP client using `httpx`
- Comprehensive error handling
- Context manager support for resource cleanup

## Requirements

- Python 3.11 or higher
- UV package manager

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/malloy-publisher-client.git
cd malloy-publisher-client
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate  # On Windows
```

3. Install dependencies using UV:
```bash
uv pip install -e ".[dev]"
```

## Usage

Here's a basic example of how to use the client:

```python
from malloy_publisher.api_client.client import MalloyAPIClient, QueryParams

# Initialize the client
client = MalloyAPIClient(
    base_url="https://your-malloy-publisher-url",
    api_key="your-api-key"  # Optional
)

# List all projects
projects = client.list_projects()

# List packages in a project
packages = client.list_packages("project_name")

# List models in a package
models = client.list_models("project_name", "package_name")

# Execute a query
query_params = QueryParams(
    project_name="project_name",
    package_name="package_name",
    path="model_path",
    query="your query here"
)
result = client.execute_query(query_params)

# Use as a context manager
with MalloyAPIClient(base_url="https://your-malloy-publisher-url") as client:
    # Your code here
    pass
```

## Development

### Setting Up Development Environment

1. Install development dependencies:
```bash
uv pip install -e ".[dev]"
```

2. Install pre-commit hooks (if configured):
```bash
pre-commit install
```

### Code Style

This project uses:
- Black for code formatting
- MyPy for type checking
- Ruff for linting

To format code:
```bash
black .
```

To run type checks:
```bash
mypy .
```

To run linter:
```bash
ruff check .
```

### Running Tests

The project uses pytest for testing. To run tests:
```bash
pytest
```

For verbose output:
```bash
pytest -v
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and ensure all checks pass
5. Commit your changes using conventional commits
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guide
- Add type hints to all functions
- Write docstrings for all public functions and classes
- Add tests for new functionality
- Update documentation as needed

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
