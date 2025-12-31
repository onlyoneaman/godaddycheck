"""
Pytest configuration and fixtures.
"""

import os
import pytest


@pytest.fixture
def mock_credentials(monkeypatch):
    """Provide mock GoDaddy credentials for testing."""
    monkeypatch.setenv("GODADDY_API_KEY", "test_key_12345")
    monkeypatch.setenv("GODADDY_API_SECRET", "test_secret_67890")


@pytest.fixture
def has_real_credentials():
    """Check if real GoDaddy credentials are available."""
    return (
        os.getenv("GODADDY_API_KEY") is not None
        and os.getenv("GODADDY_API_SECRET") is not None
        and not os.getenv("GODADDY_API_KEY").startswith("test_")
    )


@pytest.fixture
def skip_without_credentials(has_real_credentials):
    """Skip test if real credentials are not available."""
    if not has_real_credentials:
        pytest.skip("Skipping: Real GoDaddy API credentials not found")


# Sample test data
@pytest.fixture
def sample_domain():
    """Return a sample domain for testing."""
    return "example.com"


@pytest.fixture
def sample_query():
    """Return a sample query for suggestions."""
    return "tech"


@pytest.fixture
def sample_check_response():
    """Return a sample domain check response."""
    return {
        "domain": "example.com",
        "available": False,
        "currency": "USD",
        "definitive": True,
        "period": 1
    }


@pytest.fixture
def sample_suggest_response():
    """Return a sample domain suggestions response."""
    return [
        {
            "domain": "techstartup.com",
            "available": True,
            "price": 129900000,  # In micro-dollars
            "currency": "USD"
        },
        {
            "domain": "mytech.io",
            "available": True,
            "price": 399900000,  # In micro-dollars
            "currency": "USD"
        }
    ]


@pytest.fixture
def sample_tlds_response():
    """Return a sample TLDs response."""
    return [
        {"name": "com", "type": "GENERIC"},
        {"name": "io", "type": "COUNTRY_CODE"},
        {"name": "org", "type": "GENERIC"},
        {"name": "net", "type": "GENERIC"}
    ]
