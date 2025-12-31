# Tests

## Running Tests

### Quick Start

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run all unit tests (no credentials needed)
pytest -m "not integration"

# Run with coverage
pytest -m "not integration" --cov=godaddycheck --cov-report=html

# Run all tests including integration (needs credentials)
pytest
```

### Test Categories

**Unit Tests** (`test_client.py`)
- No API credentials required
- Fast, runs in < 1 second
- Tests internal logic: price normalization, retry logic, etc.
- Uses mocks and fixtures

**Integration Tests** (`test_integration.py`)
- Requires real GoDaddy API credentials
- Makes actual API calls
- Slower, depends on network
- Marked with `@pytest.mark.integration`

### Running Specific Tests

```bash
# Only unit tests
pytest tests/test_client.py -v

# Only integration tests
pytest -m integration -v

# Exclude slow tests
pytest -m "not slow"

# Run specific test class
pytest tests/test_client.py::TestPriceNormalization -v

# Run specific test
pytest tests/test_client.py::TestPriceNormalization::test_normalize_price_cents_to_dollars -v
```

### Test Coverage

```bash
# Generate coverage report
pytest --cov=godaddycheck --cov-report=term-missing

# Generate HTML coverage report
pytest --cov=godaddycheck --cov-report=html
# Open htmlcov/index.html in browser
```

### Setting Up for Integration Tests

1. Get GoDaddy API credentials: https://developer.godaddy.com/keys

2. Set environment variables:
   ```bash
   export GODADDY_API_KEY="your_key"
   export GODADDY_API_SECRET="your_secret"
   ```

3. Or use `.env` file:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

4. Run integration tests:
   ```bash
   pytest -m integration
   ```

### CI/CD

For continuous integration:

```bash
# Run only unit tests (no credentials)
pytest -m "not integration" --cov=godaddycheck

# With credentials in CI
export GODADDY_API_KEY="${CI_API_KEY}"
export GODADDY_API_SECRET="${CI_API_SECRET}"
pytest --cov=godaddycheck
```

### Test Fixtures

Available fixtures (see `conftest.py`):
- `mock_credentials` - Mock API credentials for testing
- `has_real_credentials` - Check if real credentials are available
- `skip_without_credentials` - Skip test if no real credentials
- `sample_domain` - Sample domain name
- `sample_check_response` - Sample API response for check
- `sample_suggest_response` - Sample API response for suggest
- `sample_tlds_response` - Sample API response for tlds

### Writing New Tests

**Unit Test Example:**
```python
def test_my_feature(mock_credentials):
    """Test description."""
    client = GoDaddyClient()
    result = client.my_method()
    assert result == expected
```

**Integration Test Example:**
```python
@pytest.mark.integration
def test_my_integration(skip_without_credentials):
    """Test description."""
    client = GoDaddyClient()
    result = client.check("example.com")
    assert "domain" in result
```

## Test Structure

```
tests/
├── conftest.py           # Pytest fixtures and configuration
├── test_client.py        # Unit tests (no API calls)
├── test_integration.py   # Integration tests (real API calls)
└── README.md             # This file
```

## Troubleshooting

**"Skipping: Real GoDaddy API credentials not found"**
- Integration tests are skipped without credentials
- This is expected behavior
- Set GODADDY_API_KEY and GODADDY_API_SECRET to run them

**"ModuleNotFoundError: No module named 'godaddycheck'"**
- Install package: `pip install -e .`
- Or install with dev deps: `pip install -e ".[dev]"`

**Tests are slow**
- Unit tests should be fast (< 1s)
- Integration tests are slower (network calls)
- Skip integration: `pytest -m "not integration"`

**Import errors**
- Make sure you're in the project root
- Activate virtual environment if using one
- Reinstall: `pip install -e .`
