# AGENTS.md - Project Context for AI Agents & Developers

This document provides comprehensive context about the `godaddycheck` project for AI agents and human developers.

## Project Overview

**godaddycheck** is a Python package and CLI tool for checking domain availability using the GoDaddy API. It provides three core functions:
- **check**: Check if a domain is available
- **suggest**: Get domain name suggestions based on keywords
- **tlds**: List available top-level domains

## Design Philosophy

### Minimal but Robust
- Keep the codebase small and focused
- Include only what's necessary (retry logic, error handling, price normalization)
- No over-engineering or premature abstractions
- Clean, readable code over clever tricks

### Moderate Robustness
The project sits between "bare minimum" and "production-grade enterprise":
- ✅ Retry logic with exponential backoff
- ✅ Proper error handling for network/API errors
- ✅ Price normalization (GoDaddy returns prices in cents)
- ✅ Type hints for better IDE support
- ❌ No complex logging framework (keep it simple)
- ❌ No caching (YAGNI - You Aren't Gonna Need It)
- ❌ No rate limiting tracking (let GoDaddy handle it)

## Architecture

### Core Components

#### 1. `client.py` - The Heart
Contains the `GoDaddyClient` class and convenience functions.

**Key Design Decisions:**
- Uses `httpx` (not requests) for modern HTTP handling
- Lazy initialization of HTTP client (only created when needed)
- Context manager support for automatic cleanup
- Retry logic built into `_retry_request()` method
- Price normalization in `_normalize_price()` and `_normalize_result()`

**Retry Strategy:**
- Max 3 retries by default
- Exponential backoff: 1s → 2s → 4s (capped at 10s)
- Only retries on: network errors, timeouts, 429 (rate limit), 5xx errors
- Does NOT retry on: 4xx client errors (except 429)

**Price Normalization:**
```python
# GoDaddy API returns prices in various formats
# If > 1000, divide by 100 (cents → dollars)
1299 → 12.99
3999 → 39.99
12.99 → 12.99 (already in dollars)
```

#### 2. `cli.py` - Command Line Interface
Simple argparse-based CLI with three subcommands.

**Design Choices:**
- Subcommands (check, suggest, tlds) for clarity
- `--json` flag for machine-readable output
- Human-friendly output by default
- Exit codes: 0 for success, 1 for errors

#### 3. `__init__.py` - Public API
Exports the main interface:
```python
from godaddycheck import check, suggest, tlds, GoDaddyClient
```

## File Structure Explained

```
godaddycheck/
├── godaddycheck/               # Main package
│   ├── __init__.py            # Public API exports
│   ├── client.py              # Core client (300+ lines)
│   └── cli.py                 # CLI interface (150+ lines)
│
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── test_client.py         # Unit tests
│   └── test_integration.py    # Integration tests (if credentials available)
│
├── .env.example               # Example environment file
├── .gitignore                 # Git ignore rules
├── LICENSE                     # MIT License
├── README.md                   # User documentation
├── AGENTS.md                   # This file - AI/dev context
├── pyproject.toml             # Modern Python packaging (PEP 621)
├── setup.py                    # Backwards-compatible setup
└── requirements.txt            # Dependencies
```

## API Endpoints Used

This package wraps three GoDaddy API v1 endpoints:

### 1. Check Domain Availability
```
GET /v1/domains/available?domain={domain}&checkType={FAST|FULL}
```
- `FAST`: Quick check (~100ms)
- `FULL`: More thorough check (~500ms)
- Returns: `{available: bool, price: int, currency: str, domain: str}`

### 2. Suggest Domains
```
GET /v1/domains/suggest?query={keyword}&limit={number}
```
- Returns array of domain suggestions
- Each includes: domain (domain name only)
- Note: Does NOT include availability or price. Use check() method for each domain to get availability.

### 3. List TLDs
```
GET /v1/domains/tlds
```
- Returns array of all available TLDs
- Each includes: name, type (GENERIC, COUNTRY_CODE, etc.)

## Authentication

GoDaddy uses SSO key authentication:
```
Authorization: sso-key {API_KEY}:{API_SECRET}
```

Required environment variables:
- `GODADDY_API_KEY`
- `GODADDY_API_SECRET`

Get credentials from: https://developer.godaddy.com/

## Error Handling Strategy

### Retryable Errors (will retry up to 3 times)
- `httpx.NetworkError` - Network connection issues
- `httpx.TimeoutException` - Request timeout
- `429 Too Many Requests` - Rate limiting
- `5xx` errors - Server errors

### Non-Retryable Errors (fail immediately)
- `400 Bad Request` - Invalid domain name
- `401 Unauthorized` - Invalid credentials
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Invalid endpoint
- Other `4xx` errors

## Development Guidelines

### When to Edit Files

**`client.py`** - Edit when:
- Adding new GoDaddy API endpoints
- Modifying retry logic
- Changing error handling
- Updating price normalization

**`cli.py`** - Edit when:
- Adding new CLI commands
- Changing output format
- Adding new command-line flags

**`pyproject.toml`** - Edit when:
- Bumping version number
- Adding dependencies
- Changing package metadata

### Testing Strategy

**Unit Tests** (`test_client.py`):
- Test price normalization logic
- Test error handling without API calls
- Test client initialization
- Mock HTTP responses

**Integration Tests** (`test_integration.py`):
- Real API calls (requires credentials)
- Only run if `GODADDY_API_KEY` is set
- Test actual domain checks
- Validate response formats

**Run Tests:**
```bash
# Unit tests only (no credentials needed)
pytest tests/test_client.py

# All tests (needs credentials)
pytest

# With coverage
pytest --cov=godaddycheck
```

## Common Tasks

### Adding a New API Feature

1. Add method to `GoDaddyClient` in `client.py`
2. Add convenience function if needed
3. Export from `__init__.py`
4. Add CLI command in `cli.py` (if applicable)
5. Update README.md with examples
6. Add tests

### Releasing a New Version

1. Update version in `pyproject.toml`
2. Update version in `setup.py`
3. Update version in `__init__.py`
4. Update CHANGELOG (if you create one)
5. Build: `python -m build`
6. Publish: `twine upload dist/*`

### Debugging API Issues

Check in this order:
1. Are credentials set? (`echo $GODADDY_API_KEY`)
2. Are credentials valid? (test in GoDaddy portal)
3. Is the domain format correct? (e.g., "example.com" not "www.example.com")
4. Check API status: https://status.godaddy.com/
5. Enable httpx logging: `logging.basicConfig(level=logging.DEBUG)`

## Dependencies

### Production
- `httpx>=0.24.0` - Modern HTTP client
  - Why httpx? Supports both sync/async, better than requests
  - Version 0.24.0+: stable API, good performance

### Development
- `pytest>=7.0.0` - Testing framework
- `pytest-cov>=4.0.0` - Coverage reporting

### Why No Other Dependencies?
- **No logging library**: stdlib logging is sufficient
- **No click/typer**: argparse works fine for 3 commands
- **No pydantic**: type hints + dict is enough
- **No retry library**: custom retry is 20 lines
- **No python-dotenv**: Not required, just convenient

## Inspiration & Credits

This project is inspired by the bella project's `godaddy_service.py` implementation. Key differences:

**From bella:**
- ✅ Retry logic with exponential backoff
- ✅ Price normalization
- ✅ Clean API design
- ✅ Error handling patterns

**Not from bella:**
- ❌ No Flask/web framework integration
- ❌ No logging to files
- ❌ No batch domain checking (kept it simple)
- ❌ No caching layer

## Future Considerations

### Could Add (but YAGNI for now)
- Async support (`AsyncGoDaddyClient`)
- Batch domain checking
- Local TLD caching
- Rate limit tracking
- More comprehensive tests
- CI/CD pipeline

### Should NOT Add (scope creep)
- Domain registration (different API endpoints)
- DNS management
- Email hosting features
- Website builder integration
- Payment processing

## Tips for AI Agents

When working with this codebase:

1. **Read before modifying**: Always read the full file before editing
2. **Keep it minimal**: Don't add features not requested
3. **Maintain style**: Follow existing code patterns
4. **Test changes**: Update tests when adding features
5. **Update docs**: Keep README and this file in sync

### Common Requests & How to Handle

**"Add domain registration"**
→ Out of scope. This is a *checker*, not a registrar.

**"Make it faster"**
→ Already fast. httpx is modern, retry logic is efficient.

**"Add caching"**
→ Domain availability changes rapidly. Caching could give stale data.

**"Support async"**
→ Valid request. Would require significant refactoring. Ask user if really needed.

**"Add more tests"**
→ Yes! Always welcome. Focus on edge cases and integration tests.

## Questions?

For humans: Check README.md or open an issue
For AI agents: This file should have what you need, but ask the user if unclear
